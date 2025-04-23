"""
TaskController Module
=====================
This module defines the `TaskController` class, which serves as the controller for managing task-related operations 
in a Tkinter-based task management application. It provides methods for batch operations, task filtering, tag editing, 
and group management, while integrating undo/redo functionality and validation mechanisms.
Classes:
--------
- TaskController: Handles user interactions and task operations, including batch updates, filtering, and group changes.
Methods:
--------
- __init__(app):
    Initializes the TaskController with a reference to the main application instance.
- get_selected_tasks():
    Retrieves the currently selected tasks from the task listbox.
- batch_mark_done():
    Marks selected tasks as done, with validation for batch conflicts and undo/redo support.
- clear_by_filter():
    Deletes tasks matching the current filter criteria, with confirmation prompts and undo/redo support.
- batch_edit_tags():
    Adds a specified tag to all selected tasks, with undo/redo support.
- move_to_group():
    Moves selected tasks to a specified group, with validation for task creation and batch conflicts, 
    and undo/redo support.
Dependencies:
-------------
- tkinter: Used for UI components like message boxes and dialogs.
- logic.operations: Provides task-related operations such as toggling status and filtering tasks.
- logic.validation: Provides validation functions for task creation and batch conflict detection.
Usage:
------
This class is intended to be used as part of a larger Tkinter-based application. It interacts with the application's 
task list, task lookup, and undo manager to provide a seamless user experience for managing tasks.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
from logic.operations import toggle_status, filter_tasks
from logic.validation import validate_task_creation, validate_batch_conflicts

class TaskController:
    def __init__(self, app):
        self.app = app

    def get_selected_tasks(self):
        idxs = self.app.task_listbox.curselection()
        return [self.app.visible_tasks[i] for i in idxs]

    def batch_mark_done(self):
        tasks = self.get_selected_tasks()
        # Pre-validation for batch conflicts
        if not validate_batch_conflicts(tasks):
            messagebox.showerror("Batch Conflict", "Conflicting high-priority tasks in selection.")
            return
        # Capture pre-action state
        old_tasks = list(self.app.tasks)
        old_lookup = dict(self.app.task_lookup)
        for t in tasks:
            try:
                clone = toggle_status(t, self.app.task_lookup)
                if clone:
                    self.app.tasks.append(clone)
                    self.app.task_lookup[clone.id] = clone
            except ValueError as ve:
                messagebox.showwarning("Blocked", str(ve))
        # Register undo/redo for batch mark done
        new_tasks = list(self.app.tasks)
        new_lookup = dict(self.app.task_lookup)
        def undo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(old_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(old_lookup)
            self.app.update_all_filters()
        def redo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(new_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(new_lookup)
            self.app.update_all_filters()
        self.app.undo_manager.register(undo_action, redo_action)
        self.app.save_all()
        self.app.render_task_list()

    def clear_by_filter(self):
        to_clear = filter_tasks(self.app.tasks, self.app.filter_mode.get(), self.app.group_filter.get())
        if not to_clear:
            messagebox.showinfo("Clear by Filter", "No tasks match current filters.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(to_clear)} tasks?"):
            return
        # Capture pre-action state
        old_tasks = list(self.app.tasks)
        old_lookup = dict(self.app.task_lookup)
        for t in to_clear:
            if t in self.app.tasks:
                self.app.tasks.remove(t)
                self.app.task_lookup.pop(t.id, None)
        self.app.update_all_filters()
        # Register undo/redo for clear by filter
        new_tasks = list(self.app.tasks)
        new_lookup = dict(self.app.task_lookup)
        def undo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(old_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(old_lookup)
            self.app.update_all_filters()
        def redo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(new_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(new_lookup)
            self.app.update_all_filters()
        self.app.undo_manager.register(undo_action, redo_action)
        self.app.save_all()
        self.app.render_task_list()

    def batch_edit_tags(self):
        tasks = self.get_selected_tasks()
        if not tasks:
            messagebox.showinfo("Batch Edit Tags", "No tasks selected.")
            return
        tag = simpledialog.askstring("Batch Edit Tags", "Enter tag to add:")
        if not tag:
            return
        # Capture pre-action state
        old_tasks = list(self.app.tasks)
        old_lookup = dict(self.app.task_lookup)
        for t in tasks:
            if tag not in t.tags:
                t.tags.append(tag)
        # Register undo/redo for batch edit tags
        new_tasks = list(self.app.tasks)
        new_lookup = dict(self.app.task_lookup)
        def undo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(old_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(old_lookup)
            self.app.update_all_filters()
        def redo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(new_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(new_lookup)
            self.app.update_all_filters()
        self.app.undo_manager.register(undo_action, redo_action)
        self.app.save_all()
        self.app.render_task_list()

    def move_to_group(self):
        tasks = self.get_selected_tasks()
        if not tasks:
            messagebox.showinfo("Move to Group", "No tasks selected.")
            return
        group = simpledialog.askstring("Move to Group", "Enter new group name:")
        if not group:
            return
        # Capture pre-action state
        old_tasks = list(self.app.tasks)
        old_lookup = dict(self.app.task_lookup)
        for t in tasks:
            t.group = group.title().strip()
            result = validate_task_creation(
                t, self.app.task_lookup, {"strict_mode": self.app.settings.get("strict_mode", False)}
            )
            if result.get("block"):
                messagebox.showerror("Blocked", result["message"])
                return
        # Validate batch conflicts after group change
        if not validate_batch_conflicts(tasks):
            messagebox.showerror("Batch Conflict", "Conflicting high-priority tasks in selection after group change.")
            return
        self.app.update_all_filters()
        # Register undo/redo for move to group
        new_tasks = list(self.app.tasks)
        new_lookup = dict(self.app.task_lookup)
        def undo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(old_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(old_lookup)
            self.app.update_all_filters()
        def redo_action():
            self.app.tasks.clear()
            self.app.tasks.extend(new_tasks)
            self.app.task_lookup.clear()
            self.app.task_lookup.update(new_lookup)
            self.app.update_all_filters()
        self.app.undo_manager.register(undo_action, redo_action)
        self.app.save_all()
        self.app.render_task_list()
