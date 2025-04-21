"""
Task Ticker v6.5 - Robust Toggle, Visual Consistency, Session Undo Tracking
Author: Neils Haldane-Lutterodt
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from uuid import uuid4
from datetime import datetime
import shutil
import logging

# ---------------------------
# FILE SETTINGS
# ---------------------------
TASKS_FILE = "tasks.json"
BACKUP_FILE = "tasks_backup.json"
LOG_FILE = "task_ticker.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("400x550")
        self.root.resizable(False, False)

        self.tasks = []
        self.visible_tasks = []
        self.filter_mode = tk.StringVar(value="All")

        # Simple session-based undo stack
        self.status_undo_stack = {}

        self.create_widgets()
        self.load_tasks_from_file()

    # ---------------------------
    # UI SETUP
    # ---------------------------
    def create_widgets(self):
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=(10, 0))

        tk.Label(filter_frame, text="Filter:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))
        filter_dropdown = tk.OptionMenu(
            filter_frame,
            self.filter_mode,
            "All", "Pending", "Done",
            command=lambda _: self.render_task_list()
        )
        filter_dropdown.config(width=10)
        filter_dropdown.pack(side=tk.LEFT)

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

        toggle_btn = tk.Button(btn_frame, text="Toggle Done", command=self.toggle_task_status, bg="#2196F3", fg="white")
        toggle_btn.grid(row=0, column=1, padx=10)

    # ---------------------------
    # TASK ACTIONS
    # ---------------------------
    def add_task(self):
        raw_text = self.task_input.get().strip()

        if not raw_text:
            messagebox.showwarning("Empty Input", "Please enter a task.")
            return

        if len(raw_text) > 100:
            messagebox.showwarning("Too Long", "Tasks should be under 100 characters.")
            return

        task = {
            "id": str(uuid4()),
            "task": raw_text,
            "status": "pending",
            "created_at": datetime.now().isoformat(timespec='seconds'),
            "priority": "normal"
        }

        self.tasks.append(task)
        self.task_input.delete(0, tk.END)
        self.save_tasks_to_file()
        self.render_task_list()
        logging.info(f"Task added: {task}")

    def delete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            task = self.visible_tasks[index]
            confirm = messagebox.askyesno("Confirm Delete", f"Delete task: '{task['task']}'?")
            if confirm:
                self.tasks = [t for t in self.tasks if t["id"] != task["id"]]
                self.status_undo_stack.pop(task["id"], None)
                self.save_tasks_to_file()
                self.render_task_list()
                logging.info(f"Task deleted: {task}")
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to delete.")

    def toggle_task_status(self):
        """Toggle between done and pending states with undo tracking"""
        try:
            index = self.task_listbox.curselection()[0]
            task = self.visible_tasks[index]
            task_to_update = self.find_task_by_id(task["id"])

            if task_to_update and task_to_update["status"] in {"pending", "done"}:
                prev_status = task_to_update["status"]
                task_to_update["status"] = "pending" if prev_status == "done" else "done"
                self.status_undo_stack[task_to_update["id"]] = prev_status  # Track last status
                logging.info(f"Task status toggled: {task_to_update}")
                self.save_tasks_to_file()
                self.render_task_list()
            else:
                messagebox.showwarning("Unsupported Status", f"Task status '{task_to_update.get('status')}' is not toggleable.")
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to toggle status.")

    def find_task_by_id(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    # ---------------------------
    # FILTERING / DISPLAY
    # ---------------------------
    def get_filtered_tasks(self):
        mode = self.filter_mode.get()
        if mode == "Pending":
            return [t for t in self.tasks if t["status"] == "pending"]
        elif mode == "Done":
            return [t for t in self.tasks if t["status"] == "done"]
        return self.tasks

    def format_task_display(self, task):
        """Ensures visual consistency for task rendering"""
        text = task["task"]
        if task["status"] == "done":
            return f"✔ {text}"
        return text

    def render_task_list(self):
        """Updates the Listbox UI with filtered tasks"""
        self.task_listbox.delete(0, tk.END)
        self.visible_tasks = self.get_filtered_tasks()

        for task in self.visible_tasks:
            display = self.format_task_display(task)
            self.task_listbox.insert(tk.END, display)

    # ---------------------------
    # FILE HANDLING
    # ---------------------------
    def save_tasks_to_file(self):
        try:
            if os.path.exists(TASKS_FILE):
                shutil.copy(TASKS_FILE, BACKUP_FILE)

            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            logging.error(f"Save Error: {e}")
            messagebox.showerror("Save Error", f"Error saving tasks:\n{e}")

    def load_tasks_from_file(self):
        if not os.path.exists(TASKS_FILE):
            return

        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.validate_json_data(data)
            self.tasks = data
            self.render_task_list()
        except Exception as e:
            logging.error(f"Load Error: {e}")
            self.recover_tasks_file(error_msg=str(e))

    def validate_json_data(self, data):
        if not isinstance(data, list):
            raise ValueError("Task file is not a list.")
        for item in data:
            if not all(k in item for k in ("id", "task", "status")):
                raise ValueError("Malformed task entry in JSON.")

    def recover_tasks_file(self, error_msg="Unknown"):
        messagebox.showwarning("Task File Corrupted",
            f"The task file appears corrupted or invalid.\n\nError: {error_msg}\n\nStarting with a fresh list.")
        self.tasks = []
        self.save_tasks_to_file()
        self.task_listbox.delete(0, tk.END)
        logging.warning("Recovered from corrupted task file.")


# ---------------------------
# APP ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTickerApp(root)
    root.mainloop()

    if not os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'w') as f:
            json.dump([], f)
    logging.info("Task Ticker closed.")
    logging.shutdown()
    # Ensure backup file is created if it doesn't exist
    if not os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'w') as f:
            json.dump([], f)