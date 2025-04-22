'''
Task Ticker v9 - Task Dependencies and Sequencing
Author: Neils Haldane-Lutterodt
'''

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
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
SETTINGS_FILE = "settings.json"
LOG_FILE = "task_ticker.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_SETTINGS = {
    "auto_sort": False,
    "default_sort": "due_date"
}

class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("600x680")
        self.root.resizable(False, False)

        self.tasks = []
        self.visible_tasks = []
        self.status_undo_stack = {}

        self.filter_mode = tk.StringVar(value="All")
        self.group_filter = tk.StringVar(value="All Groups")
        self.group_entry_var = tk.StringVar(value="Personal")

        self.sort_key = tk.StringVar(value="due_date")
        self.settings = self.load_settings()

        self.dependency_map = {}  # Maps dropdown labels to UUIDs
        self.selected_dependency = tk.StringVar(value="None")
        self.sequence_input = tk.StringVar(value="1")

        self.create_widgets()
        self.load_tasks_from_file()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=(10, 0))

        tk.Label(control_frame, text="Status:").grid(row=0, column=0, padx=5)
        status_menu = tk.OptionMenu(control_frame, self.filter_mode, "All", "Pending", "Done", command=lambda _: self.render_task_list())
        status_menu.grid(row=0, column=1)

        tk.Label(control_frame, text="Group:").grid(row=0, column=2, padx=5)
        self.group_dropdown = tk.OptionMenu(control_frame, self.group_filter, "All Groups", command=lambda _: self.render_task_list())
        self.group_dropdown.grid(row=0, column=3)

        tk.Label(control_frame, text="Sort by:").grid(row=1, column=0, padx=5)
        sort_menu = tk.OptionMenu(control_frame, self.sort_key, "due_date", "created_at", "priority", "sequence", command=lambda _: self.sort_and_render())
        sort_menu.grid(row=1, column=1)

        sort_btn = tk.Button(control_frame, text="Sort Now", command=self.sort_and_render)
        sort_btn.grid(row=1, column=2, columnspan=2, pady=5)

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.task_input = tk.Entry(entry_frame, width=30)
        self.task_input.pack(side=tk.LEFT, padx=(10, 5))

        self.due_input = DateEntry(entry_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.due_input.pack(side=tk.LEFT, padx=5)

        self.sequence_entry = tk.Entry(entry_frame, width=5, textvariable=self.sequence_input)
        self.sequence_entry.pack(side=tk.LEFT)

        self.group_input = tk.Entry(entry_frame, width=10, textvariable=self.group_entry_var)
        self.group_input.pack(side=tk.LEFT, padx=5)

        add_btn = tk.Button(entry_frame, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white")
        add_btn.pack(side=tk.LEFT)

        dep_frame = tk.Frame(self.root)
        dep_frame.pack()

        tk.Label(dep_frame, text="Depends On:").pack(side=tk.LEFT)
        self.dep_dropdown = tk.OptionMenu(dep_frame, self.selected_dependency, "None")
        self.dep_dropdown.pack(side=tk.LEFT)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.task_listbox = tk.Listbox(list_frame, height=18, width=80)
        self.task_listbox.pack(side=tk.LEFT)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Delete Task", command=self.delete_task, bg="#f44336", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Toggle Done", command=self.toggle_task_status, bg="#2196F3", fg="white").grid(row=0, column=1, padx=10)

    def add_task(self):
        text = self.task_input.get().strip()
        group = self.group_input.get().strip() or "General"
        due_date = self.due_input.get_date().isoformat()
        sequence = int(self.sequence_input.get() or 1)
        dep_label = self.selected_dependency.get()
        depends_on = self.dependency_map.get(dep_label) if dep_label != "None" else None

        if not text:
            messagebox.showwarning("Empty Input", "Please enter a task.")
            return

        if depends_on:
            parent = self.find_task_by_id(depends_on)
            if parent and parent['due_date'] > due_date:
                messagebox.showwarning("Due Date Conflict", "Dependent task has an earlier due date than its parent.")

        if depends_on == "self":
            messagebox.showerror("Invalid Dependency", "A task cannot depend on itself.")
            return

        task = {
            "id": str(uuid4()),
            "task": text,
            "status": "pending",
            "group": group.title(),
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "priority": "normal",
            "sequence": sequence,
            "depends_on": depends_on
        }

        self.tasks.append(task)
        self.task_input.delete(0, tk.END)
        self.group_entry_var.set(group.title())
        self.sequence_input.set(str(sequence + 1))
        self.selected_dependency.set("None")
        self.save_tasks_to_file()
        self.update_group_filter_options()
        self.update_dependency_dropdown()
        self.sort_and_render()
        logging.info(f"Task added: {task}")

    def delete_task(self):
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.visible_tasks[idx]
            self.tasks = [t for t in self.tasks if t["id"] != task["id"]]
            self.save_tasks_to_file()
            self.update_group_filter_options()
            self.update_dependency_dropdown()
            self.sort_and_render()
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to delete.")

    def toggle_task_status(self):
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.visible_tasks[idx]
            if task.get("depends_on"):
                dep = self.find_task_by_id(task["depends_on"])
                if dep and dep["status"] != "done":
                    messagebox.showwarning("Dependency Unmet", f"This task depends on '{dep['task']}' which is not yet done.")
                    return
            for t in self.tasks:
                if t["id"] == task["id"]:
                    t["status"] = "pending" if t["status"] == "done" else "done"
                    break
            self.save_tasks_to_file()
            self.sort_and_render()
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to toggle.")

    def sort_and_render(self):
        key = self.sort_key.get()
        self.tasks.sort(key=lambda t: t.get(key) or ("9999-12-31" if key == "due_date" else 9999))
        self.render_task_list()

    def get_filtered_tasks(self):
        status = self.filter_mode.get()
        group = self.group_filter.get()
        filtered = self.tasks
        if status != "All":
            filtered = [t for t in filtered if t["status"] == status.lower()]
        if group != "All Groups":
            filtered = [t for t in filtered if t["group"] == group]
        return filtered

    def render_task_list(self):
        self.task_listbox.delete(0, tk.END)
        self.visible_tasks = self.get_filtered_tasks()
        for t in self.visible_tasks:
            blocked = " ⛔" if t.get("depends_on") and self.find_task_by_id(t["depends_on"])["status"] != "done" else ""
            seq = f"[{t.get('sequence', '?')}]"
            line = f"{seq} {'✔' if t['status']=='done' else ''} {t['task']} [{t['group']}] (Due: {t['due_date']}){blocked}"
            self.task_listbox.insert(tk.END, line)

    def update_group_filter_options(self):
        groups = sorted({t["group"] for t in self.tasks})
        menu = self.group_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="All Groups", command=lambda: self.set_group_filter("All Groups"))
        for g in groups:
            menu.add_command(label=g, command=lambda val=g: self.set_group_filter(val))

    def set_group_filter(self, val):
        self.group_filter.set(val)
        self.render_task_list()

    def update_dependency_dropdown(self):
        self.dependency_map.clear()
        menu = self.dep_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="None", command=lambda: self.selected_dependency.set("None"))
        for task in self.tasks:
            label = f"{task['task']} [{task['group']}] (ID: {task['id'][:6]}...)"
            self.dependency_map[label] = task["id"]
            menu.add_command(label=label, command=lambda val=label: self.selected_dependency.set(val))

    def find_task_by_id(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def save_tasks_to_file(self):
        if os.path.exists(TASKS_FILE):
            shutil.copy(TASKS_FILE, BACKUP_FILE)
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def load_tasks_from_file(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    self.tasks = json.load(f)
                self.update_group_filter_options()
                self.update_dependency_dropdown()
                self.sort_and_render()
            except Exception as e:
                messagebox.showwarning("Load Error", str(e))
                self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTickerApp(root)
    root.mainloop()

    logging.info("Task Ticker closed.")
    logging.shutdown()
