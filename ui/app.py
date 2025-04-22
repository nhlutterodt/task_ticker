'''
ui/app.py - Task Ticker GUI with Recurring Task Support
Author: Neils Haldane-Lutterodt
'''

from logic.operations import (
    toggle_status,
    filter_tasks,
    sort_tasks,
    validate_dependency,
    create_task_lookup,
    recurrence_structure  # <-- now valid!
)
from storage.file_io import load_tasks, save_tasks
from storage.settings import load_settings, save_settings

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from uuid import uuid4
from datetime import datetime
from models.task import Task
from storage.file_io import load_tasks, save_tasks
from storage.settings import load_settings, save_settings
from logic.operations import (
    toggle_status,
    filter_tasks,
    sort_tasks,
    validate_dependency,
    create_task_lookup,
    recurrence_structure
)

class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("680x760")
        self.root.resizable(False, False)

        self.tasks = load_tasks()
        self.settings = load_settings()
        self.visible_tasks = []
        self.task_lookup = create_task_lookup(self.tasks)

        self.filter_mode = tk.StringVar(value="All")
        self.group_filter = tk.StringVar(value="All Groups")
        self.tag_filter = tk.StringVar(value="All Tags")
        self.group_entry_var = tk.StringVar(value="Personal")
        self.sort_key = tk.StringVar(value=self.settings.get("default_sort", "due_date"))
        self.sequence_input = tk.StringVar(value="1")
        self.selected_dependency = tk.StringVar(value="None")
        self.recur_option = tk.StringVar(value="None")
        self.dependency_map = {}

        self.build_ui()
        self.update_group_filter()
        self.update_tag_filter()
        self.update_dependency_dropdown()
        self.render_task_list()

    def build_ui(self):
        control = tk.Frame(self.root)
        control.pack(pady=(10, 0))

        tk.Label(control, text="Status:").grid(row=0, column=0)
        tk.OptionMenu(control, self.filter_mode, "All", "Pending", "Done", command=lambda _: self.render_task_list()).grid(row=0, column=1)

        tk.Label(control, text="Group:").grid(row=0, column=2)
        self.group_dropdown = tk.OptionMenu(control, self.group_filter, "All Groups", command=lambda _: self.render_task_list())
        self.group_dropdown.grid(row=0, column=3)

        tk.Label(control, text="Tag:").grid(row=0, column=4)
        self.tag_dropdown = tk.OptionMenu(control, self.tag_filter, "All Tags", command=lambda _: self.render_task_list())
        self.tag_dropdown.grid(row=0, column=5)

        tk.Label(control, text="Sort:").grid(row=1, column=0)
        tk.OptionMenu(control, self.sort_key, "due_date", "created_at", "priority", "sequence", command=self.render_task_list).grid(row=1, column=1)
        tk.Button(control, text="Sort Now", command=self.render_task_list).grid(row=1, column=2, columnspan=2)

        entry = tk.Frame(self.root)
        entry.pack(pady=10)

        self.task_input = tk.Entry(entry, width=30)
        self.task_input.pack(side=tk.LEFT, padx=(10, 5))

        self.due_input = DateEntry(entry, width=12, date_pattern='yyyy-mm-dd')
        self.due_input.pack(side=tk.LEFT, padx=5)

        self.sequence_entry = tk.Entry(entry, width=5, textvariable=self.sequence_input)
        self.sequence_entry.pack(side=tk.LEFT)

        self.group_input = tk.Entry(entry, width=10, textvariable=self.group_entry_var)
        self.group_input.pack(side=tk.LEFT)

        tk.Label(entry, text="Tags:").pack(side=tk.LEFT)
        self.tag_input = tk.Entry(entry, width=14)
        self.tag_input.pack(side=tk.LEFT)

        tk.Label(entry, text="Recurrence:").pack(side=tk.LEFT)
        self.recur_menu = tk.OptionMenu(entry, self.recur_option, *recurrence_structure.keys())
        self.recur_menu.pack(side=tk.LEFT)

        tk.Button(entry, text="Add", bg="#4CAF50", fg="white", command=self.add_task).pack(side=tk.LEFT, padx=5)

        dep_frame = tk.Frame(self.root)
        dep_frame.pack()
        tk.Label(dep_frame, text="Depends On:").pack(side=tk.LEFT)
        self.dep_dropdown = tk.OptionMenu(dep_frame, self.selected_dependency, "None")
        self.dep_dropdown.pack(side=tk.LEFT)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)
        self.task_listbox = tk.Listbox(list_frame, width=94, height=18)
        self.task_listbox.pack(side=tk.LEFT)
        self.task_listbox.bind("<Double-Button-1>", self.edit_notes_for_selected)

        scrollbar = tk.Scrollbar(list_frame, command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        btns = tk.Frame(self.root)
        btns.pack(pady=10)
        tk.Button(btns, text="Delete", command=self.delete_task, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Toggle Done", command=self.toggle_selected_task, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)

    def add_task(self):
        name = self.task_input.get().strip()
        if not name:
            messagebox.showwarning("Missing Task", "Please enter a task description.")
            return

        group = self.group_input.get().strip() or "General"
        due = self.due_input.get_date().isoformat()
        seq = int(self.sequence_input.get() or 1)
        dep_label = self.selected_dependency.get()
        depends_on = self.dependency_map.get(dep_label) if dep_label != "None" else None
        tags = [t.strip() for t in self.tag_input.get().strip().split(",") if t.strip()]
        recur_val = self.recur_option.get()
        recur_dict = recurrence_structure[recur_val]

        if depends_on:
            parent = self.task_lookup.get(depends_on)
            if parent and not validate_dependency(Task(name, group, due), parent):
                messagebox.showwarning("Due Date Conflict", "This task is due before its dependency.")

        new_task = Task(
            task=name,
            group=group,
            due_date=due,
            sequence=seq,
            depends_on=depends_on,
            tags=tags,
            notes="",
            recurrence=recur_dict
        )

        self.tasks.append(new_task)
        self.task_lookup[new_task.id] = new_task
        self.task_input.delete(0, tk.END)
        self.tag_input.delete(0, tk.END)
        self.sequence_input.set(str(seq + 1))
        self.selected_dependency.set("None")

        self.update_group_filter()
        self.update_tag_filter()
        self.update_dependency_dropdown()
        self.save_all()
        self.render_task_list()

    def render_task_list(self):
        self.visible_tasks = filter_tasks(self.tasks, self.filter_mode.get(), self.group_filter.get())

        tag = self.tag_filter.get()
        if tag != "All Tags":
            self.visible_tasks = [t for t in self.visible_tasks if tag in t.tags]

        self.visible_tasks = sort_tasks(self.visible_tasks, self.sort_key.get())
        self.task_listbox.delete(0, tk.END)
        for t in self.visible_tasks:
            blocked = "⛔" if t.is_blocked(self.task_lookup) else ""
            tags = f" 🏷️ {', '.join(t.tags)}" if t.tags else ""
            recur = f" 🔁 {t.recurrence['frequency'].capitalize()}" if t.recurrence and t.recurrence.get("frequency") != "none" else ""
            self.task_listbox.insert(
                tk.END,
                f"[{t.sequence}] {'✔' if t.is_done() else ''} {t.task} [{t.group}] (Due: {t.due_date}){tags}{recur} {blocked}"
            )

    def edit_notes_for_selected(self, event):
        try:
            idx = self.task_listbox.nearest(event.y)
            task = self.visible_tasks[idx]
            self.open_notes_editor(task)
        except IndexError:
            return

    def open_notes_editor(self, task):
        notes_window = tk.Toplevel(self.root)
        notes_window.title(f"Notes for Task [{task.task}]")
        notes_window.geometry("500x300")
        notes_window.resizable(False, False)

        text_area = tk.Text(notes_window, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_area.insert(tk.END, task.notes)

        def save_notes_and_close():
            task.notes = text_area.get("1.0", tk.END).strip()
            self.save_all()
            notes_window.destroy()

        tk.Button(notes_window, text="Save Notes", command=save_notes_and_close).pack(pady=5)

    def toggle_selected_task(self):
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.visible_tasks[idx]
            new_clone = toggle_status(task, self.task_lookup)
            if new_clone:
                self.tasks.append(new_clone)
                self.task_lookup[new_clone.id] = new_clone
            self.save_all()
            self.render_task_list()
        except ValueError as ve:
            messagebox.showwarning("Blocked", str(ve))
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task.")

    def delete_task(self):
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.visible_tasks[idx]
            self.tasks.remove(task)
            self.task_lookup.pop(task.id, None)
            self.update_group_filter()
            self.update_tag_filter()
            self.update_dependency_dropdown()
            self.save_all()
            self.render_task_list()
        except IndexError:
            messagebox.showerror("Error", "No task selected.")

    def update_group_filter(self):
        menu = self.group_dropdown["menu"]
        groups = sorted(set(t.group for t in self.tasks))
        menu.delete(0, "end")
        menu.add_command(label="All Groups", command=lambda: self.group_filter.set("All Groups"))
        for g in groups:
            menu.add_command(label=g, command=lambda val=g: self.group_filter.set(val))

    def update_tag_filter(self):
        all_tags = sorted({tag for task in self.tasks for tag in task.tags})
        menu = self.tag_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="All Tags", command=lambda: self.tag_filter.set("All Tags"))
        for tag in all_tags:
            menu.add_command(label=tag, command=lambda val=tag: self.tag_filter.set(val))

    def update_dependency_dropdown(self):
        self.dependency_map.clear()
        menu = self.dep_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="None", command=lambda: self.selected_dependency.set("None"))
        for task in self.tasks:
            label = f"{task.task} [{task.group}] ({task.id[:6]}...)"
            self.dependency_map[label] = task.id
            menu.add_command(label=label, command=lambda val=label: self.selected_dependency.set(val))

    def save_all(self):
        save_tasks(self.tasks)
        self.settings["default_sort"] = self.sort_key.get()
        self.settings["default_group"] = self.group_filter.get()
        save_settings(self.settings)
