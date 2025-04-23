'''
ui/app.py - Task Ticker GUI with Strict Mode and Recurrence Support
Author: Neils Haldane-Lutterodt
'''

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from uuid import uuid4
from datetime import datetime

from models.task import Task, TaskMeta
from logic.operations import (
    toggle_status,
    filter_tasks,
    sort_tasks,
    validate_dependency,
    create_task_lookup,
    recurrence_structure
)
from logic.validation import validate_task_creation
from storage.file_io import load_tasks, save_tasks
from storage.settings import load_settings, save_settings
from ui.controller import TaskController
from ui.undo import UndoManager

ALL_GROUPS_LABEL = "All Groups"
ALL_TAGS_LABEL = "All Tags"

class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("720x800")
        self.root.resizable(False, False)

        self.tasks = load_tasks()
        self.settings = load_settings()
        self.controller = TaskController(self)
        self.visible_tasks = []
        self.task_lookup = create_task_lookup(self.tasks)
        self.undo_manager = UndoManager(limit=20)

        self.filter_mode = tk.StringVar(value="All")
        self.group_filter = tk.StringVar(value=self.settings.get("default_group", ALL_GROUPS_LABEL))
        self.tag_filter = tk.StringVar(value=ALL_TAGS_LABEL)
        self.group_entry_var = tk.StringVar(value="Personal")
        self.sort_key = tk.StringVar(value=self.settings.get("default_sort", "due_date"))
        self.sequence_input = tk.StringVar(value="1")
        self.selected_dependency = tk.StringVar(value="None")
        self.recur_option = tk.StringVar(value="None")
        self.dependency_map = {}
        self.strict_mode_var = tk.IntVar(value=int(self.settings.get("strict_mode", False)))

        self.build_ui()
        self.update_all_filters()
        self.render_task_list()

    def build_ui(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        options_menu = tk.Menu(self.menu, tearoff=0)
        options_menu.add_checkbutton(
            label="Strict Mode",
            variable=self.strict_mode_var,
            onvalue=1,
            offvalue=0,
            command=self.toggle_strict_mode
        )
        self.menu.add_cascade(label="Options", menu=options_menu)

        control = tk.Frame(self.root)
        control.pack(pady=(10, 0))

        tk.Label(control, text="Status:").grid(row=0, column=0)
        tk.OptionMenu(control, self.filter_mode, "All", "Pending", "Done", command=lambda _: self.render_task_list()).grid(row=0, column=1)

        tk.Label(control, text="Group:").grid(row=0, column=2)
        self.group_dropdown = tk.OptionMenu(control, self.group_filter, ALL_GROUPS_LABEL, command=lambda _: self.render_task_list())
        self.group_dropdown.grid(row=0, column=3)

        tk.Label(control, text="Tag:").grid(row=0, column=4)
        self.tag_dropdown = tk.OptionMenu(control, self.tag_filter, ALL_TAGS_LABEL, command=lambda _: self.render_task_list())
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
        self.task_listbox = tk.Listbox(list_frame, width=100, height=20, selectmode="extended")
        self.task_listbox.pack(side=tk.LEFT)
        self.task_listbox.bind("<Double-Button-1>", self.edit_notes_for_selected)
        scrollbar = tk.Scrollbar(list_frame, command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        btns = tk.Frame(self.root)
        btns.pack(pady=10)
        tk.Button(btns, text="Delete", command=self.delete_task, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Toggle Done", command=self.toggle_selected_task, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Mark All Done", command=self.mark_all_done).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Clear by Filter", command=self.clear_by_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Batch Edit Tags", command=self.batch_edit_tags).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Move to Group", command=self.move_to_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Undo", command=self.perform_undo).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Redo", command=self.perform_redo).pack(side=tk.LEFT, padx=5)

    def toggle_strict_mode(self):
        self.settings["strict_mode"] = bool(self.strict_mode_var.get())
        save_settings(self.settings)
        messagebox.showinfo("Strict Mode", f"Strict Mode is now {'enabled' if self.settings['strict_mode'] else 'disabled'}.")

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

        new_task = Task(
            task=name,
            meta=TaskMeta(
                group=group,
                due_date=due,
                sequence=seq,
                depends_on=depends_on,
                tags=tags,
                notes="",
                recurrence=recur_dict
            )
        )

        if depends_on:
            parent = self.task_lookup[depends_on]
            if not validate_dependency(new_task, parent):
                validation = {"block": True, "message": "Dependency validation failed."}
                if validation["block"]:
                    messagebox.showerror("Blocked", validation["message"])
                    return

        rules = {
            "strict_mode": self.settings.get("strict_mode", False),
            "dependency_order": True,
            "group_priority_exclusive": True,
            "group_unique_names": True
        }
        validation = validate_task_creation(new_task, self.task_lookup, rules=rules)
        if validation["block"]:
            messagebox.showerror("Blocked", validation["message"])
            return
        elif validation["warn"]:
            proceed = messagebox.askyesno("Warning", validation["message"] + "\n\nProceed anyway?")
            if not proceed:
                return

        self.tasks.append(new_task)
        self.task_lookup[new_task.id] = new_task
        self.task_input.delete(0, tk.END)
        self.task_input.focus()
        self.tag_input.delete(0, tk.END)
        self.sequence_input.set(str(seq + 1))
        self.group_entry_var.set("Personal")
        self.recur_option.set("None")
        self.selected_dependency.set("None")

        self.update_all_filters()
        self.save_all()
        self.render_task_list()

    def render_task_list(self):
        try:
            selected_idx = self.task_listbox.curselection()[0]
        except IndexError:
            selected_idx = None

        self.visible_tasks = filter_tasks(self.tasks, self.filter_mode.get(), self.group_filter.get())
        tag = self.tag_filter.get()
        if tag != ALL_TAGS_LABEL:
            self.visible_tasks = [t for t in self.visible_tasks if tag in t.tags]
        self.visible_tasks = sort_tasks(self.visible_tasks, self.sort_key.get())

        self.task_listbox.delete(0, tk.END)
        for t in self.visible_tasks:
            blocked = "⛔" if t.is_blocked(self.task_lookup) else ""
            tags = f" 🏷️ {', '.join(t.tags)}" if t.tags else ""
            recur = f" 🔁 {t.recurrence['frequency'].capitalize()}" if t.recurrence.get("frequency") != "none" else ""
            self.task_listbox.insert(
                tk.END,
                f"[{t.sequence}] {'✔' if t.is_done() else ''} {t.task} [{t.group}] (Due: {t.due_date}){tags}{recur} {blocked}"
            )

        if selected_idx is not None and selected_idx < len(self.visible_tasks):
            self.task_listbox.select_set(selected_idx)

    def edit_notes_for_selected(self, event):
        try:
            idx = self.task_listbox.nearest(event.y)
            task = self.visible_tasks[idx]
            self.open_notes_editor(task)
        except IndexError:
            pass

    def open_notes_editor(self, task):
        notes_window = tk.Toplevel(self.root)
        notes_window.title("Notes")
        notes_window.geometry("500x300")
        notes_window.resizable(False, False)

        text_area = tk.Text(notes_window, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_area.insert(tk.END, task.notes)

        def save_notes_and_close():
            # Capture old and new notes for undo/redo
            old_notes = task.notes
            new_notes = text_area.get("1.0", tk.END).strip()
            def undo_action():
                task.notes = old_notes
                self.save_all()
            def redo_action():
                task.notes = new_notes
                self.save_all()
            self.undo_manager.register(undo_action, redo_action)
            task.notes = new_notes
            self.save_all()
            notes_window.destroy()

        tk.Button(notes_window, text="Save Notes", command=save_notes_and_close).pack(pady=5)

    def toggle_selected_task(self):
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.visible_tasks[idx]
            # Capture pre-toggle state
            old_tasks = list(self.tasks)
            old_lookup = dict(self.task_lookup)
            new_clone = toggle_status(task, self.task_lookup)
            if new_clone:
                self.tasks.append(new_clone)
                self.task_lookup[new_clone.id] = new_clone
            # Register undo/redo for toggle status
            new_tasks = list(self.tasks)
            new_lookup = dict(self.task_lookup)
            def undo_action():
                self.tasks.clear()
                self.tasks.extend(old_tasks)
                self.task_lookup.clear()
                self.task_lookup.update(old_lookup)
                self.update_all_filters()
            def redo_action():
                self.tasks.clear()
                self.tasks.extend(new_tasks)
                self.task_lookup.clear()
                self.task_lookup.update(new_lookup)
                self.update_all_filters()
            self.undo_manager.register(undo_action, redo_action)
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
            orig_index = self.tasks.index(task)
            # register undo/redo actions
            def undo_action():
                self.tasks.insert(orig_index, task)
                self.task_lookup[task.id] = task
            def redo_action():
                self.tasks.remove(task)
                self.task_lookup.pop(task.id, None)
            self.undo_manager.register(undo_action, redo_action)
            # perform delete
            self.tasks.remove(task)
            self.task_lookup.pop(task.id, None)
            self.update_all_filters()
            self.save_all()
            self.render_task_list()
        except IndexError:
            messagebox.showerror("Error", "No task selected.")

    def perform_undo(self):
        if self.undo_manager.undo():
            self.save_all()
            self.render_task_list()

    def perform_redo(self):
        if self.undo_manager.redo():
            self.save_all()
            self.render_task_list()

    def update_group_filter(self):
        menu = self.group_dropdown["menu"]
        groups = sorted({t.group for t in self.tasks})
        menu.delete(0, "end")
        menu.add_command(label=ALL_GROUPS_LABEL, command=lambda: self.group_filter.set(ALL_GROUPS_LABEL))
        for g in groups:
            menu.add_command(label=g, command=lambda val=g: self.group_filter.set(val))

    def update_tag_filter(self):
        all_tags = sorted({tag for task in self.tasks for tag in task.tags})
        menu = self.tag_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label=ALL_TAGS_LABEL, command=lambda: self.tag_filter.set(ALL_TAGS_LABEL))
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

    def update_all_filters(self):
        self.update_group_filter()
        self.update_tag_filter()
        self.update_dependency_dropdown()

    def save_all(self):
        save_tasks(self.tasks)
        self.settings["default_sort"] = self.sort_key.get()
        self.settings["default_group"] = self.group_filter.get()
        save_settings(self.settings)
        self.update_all_filters()
        self.render_task_list()

    # Batch operation delegates
    def mark_all_done(self):
        self.controller.batch_mark_done()
        self.render_task_list()

    def clear_by_filter(self):
        self.controller.clear_by_filter()
        self.render_task_list()

    def batch_edit_tags(self):
        self.controller.batch_edit_tags()

    def move_to_group(self):
        self.controller.move_to_group()