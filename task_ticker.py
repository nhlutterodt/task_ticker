"""
Task Ticker v3 - Enhanced To-Do List with Metadata, Backup, and Resilience
Author: Neils Haldane-Lutterodt
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
import shutil

TASKS_FILE = "tasks.json"
BACKUP_FILE = "tasks_backup.json"

class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Now using list of dicts to store task metadata
        self.tasks = []

        self.create_widgets()
        self.load_tasks_from_file()

    # ---------------------------
    # UI SETUP
    # ---------------------------
    def create_widgets(self):
        """Create and layout all widgets"""

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.task_input = tk.Entry(entry_frame, width=30, font=('Arial', 12))
        self.task_input.pack(side=tk.LEFT, padx=(10, 5))

        add_btn = tk.Button(entry_frame, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white")
        add_btn.pack(side=tk.LEFT)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.task_listbox = tk.Listbox(list_frame, height=15, width=45, font=('Arial', 11))
        self.task_listbox.pack(side=tk.LEFT)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        delete_btn = tk.Button(btn_frame, text="Delete Task", command=self.delete_task, bg="#f44336", fg="white")
        delete_btn.grid(row=0, column=0, padx=10)

        done_btn = tk.Button(btn_frame, text="Mark Done", command=self.mark_done, bg="#2196F3", fg="white")
        done_btn.grid(row=0, column=1, padx=10)

    # ---------------------------
    # TASK OPERATIONS
    # ---------------------------
    def add_task(self):
        """Adds a new task with metadata"""
        raw_text = self.task_input.get().strip()

        if not raw_text:
            messagebox.showwarning("Empty Input", "Please enter a task.")
            return

        sanitized_text = raw_text.replace("<", "").replace(">", "").replace(";", "")

        task = {
            "task": sanitized_text,
            "status": "pending",
            "created_at": datetime.now().isoformat(timespec='seconds'),
            "priority": "normal"
        }

        self.tasks.append(task)
        self.task_listbox.insert(tk.END, sanitized_text)
        self.task_input.delete(0, tk.END)
        self.save_tasks_to_file()

    def delete_task(self):
        """Deletes the selected task"""
        try:
            index = self.task_listbox.curselection()[0]
            task = self.tasks[index]

            confirm = messagebox.askyesno("Confirm Delete", f"Delete task: '{task['task']}'?")
            if confirm:
                self.task_listbox.delete(index)
                self.tasks.pop(index)
                self.save_tasks_to_file()
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to delete.")

    def mark_done(self):
        """Marks selected task as completed"""
        try:
            index = self.task_listbox.curselection()[0]
            task = self.tasks[index]

            if task["status"] == "done":
                messagebox.showinfo("Already Done", "This task is already marked as done.")
                return

            task["status"] = "done"
            updated_text = f"✔ {task['task']}"
            self.task_listbox.delete(index)
            self.task_listbox.insert(index, updated_text)

            self.save_tasks_to_file()
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to mark as done.")

    # ---------------------------
    # FILE HANDLING
    # ---------------------------
    def save_tasks_to_file(self):
        """Saves current task list to file, with backup"""
        try:
            # Backup current file first
            if os.path.exists(TASKS_FILE):
                shutil.copy(TASKS_FILE, BACKUP_FILE)

            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=4)

        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving tasks:\n{e}")

    def load_tasks_from_file(self):
        """Loads tasks from file and populates the GUI"""
        if not os.path.exists(TASKS_FILE):
            return

        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.validate_json_data(data)
            self.tasks = data

            for task in self.tasks:
                text = task['task']
                if task['status'] == "done":
                    text = f"✔ {text}"
                self.task_listbox.insert(tk.END, text)

        except Exception as e:
            self.recover_tasks_file(error_msg=str(e))

    def validate_json_data(self, data):
        """Validates JSON task format"""
        if not isinstance(data, list):
            raise ValueError("Task file is not a list.")
        for item in data:
            if not isinstance(item, dict) or "task" not in item or "status" not in item:
                raise ValueError("Malformed task entry in JSON.")

    def recover_tasks_file(self, error_msg="Unknown"):
        """Attempts to recover from file corruption"""
        messagebox.showwarning("Task File Corrupted",
            f"The task file appears corrupted or invalid.\n\nError: {error_msg}\n\nStarting with a fresh list.")
        self.tasks = []
        self.save_tasks_to_file()
        self.task_listbox.delete(0, tk.END)

# ---------------------------
# APP ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTickerApp(root)
    root.mainloop()
    # Ensure backup file is created if it doesn't exist
    if not os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'w') as f:
            json.dump([], f)    # Create an empty backup file if it doesn't exist           