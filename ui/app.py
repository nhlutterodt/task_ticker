'''
"""
Task Ticker GUI Application Module
This module implements the main graphical user interface (GUI) for the Task Ticker application. It provides functionality for managing tasks, including adding, editing, filtering, sorting, and performing batch operations. The application supports features such as strict mode, recurrence, dependency validation, and undo/redo functionality.

Classes:
    TaskTickerApp:
        The main application class that initializes and manages the GUI, task data, and user interactions.

Functions:
    __init__(root):
        Initializes the application, loads tasks and settings, and sets up the GUI components.
    build_ui():
        Constructs the graphical user interface, including menus, controls, and task list display.
    toggle_strict_mode():
        Toggles the strict mode setting and saves the updated configuration.
    add_task():
        Adds a new task to the task list after validating input and dependencies.
    render_task_list():
        Updates the task list display based on the current filters and sorting options.
    edit_notes_for_selected(event):
        Opens a notes editor for the selected task in the task list.
    open_notes_editor(task):
        Displays a separate window for editing the notes of a specific task.
    toggle_selected_task():
        Toggles the completion status of the selected task and handles undo/redo registration.
    delete_task():
        Deletes the selected task from the task list and handles undo/redo registration.
    perform_undo():
        Performs an undo operation for the last action.
    perform_redo():
        Performs a redo operation for the last undone action.
    update_group_filter():
        Updates the group filter dropdown menu with available groups.
    update_tag_filter():
        Updates the tag filter dropdown menu with available tags.
    update_dependency_dropdown():
        Updates the dependency dropdown menu with available tasks.
    update_all_filters():
        Updates all filter dropdown menus (group, tag, dependency).
    save_all():
        Saves the current tasks and settings to persistent storage.
    mark_all_done():
        Marks all tasks as done using the controller's batch operation.
    clear_by_filter():
        Clears tasks based on the current filter using the controller's batch operation.
    batch_edit_tags():
        Opens the batch edit tags operation via the controller.
    move_to_group():
        Moves tasks to a specified group using the controller.

Constants:
    ALL_GROUPS_LABEL:
        Label for the "All Groups" option in the group filter dropdown.
    ALL_TAGS_LABEL:
        Label for the "All Tags" option in the tag filter dropdown.

Dependencies:
    - tkinter: Provides the GUI framework.
    - tkcalendar: Used for date entry widgets.
    - uuid: Generates unique identifiers for tasks.
    - datetime: Handles date and time operations.
    - models.task: Defines the Task and TaskMeta classes.
    - logic.operations: Provides task-related operations such as filtering, sorting, and validation.
    - logic.validation: Validates task creation rules.
    - storage.file_io: Handles loading and saving tasks to persistent storage.
    - storage.settings: Manages application settings.
    - ui.controller: Provides batch operation functionality.
    - ui.undo: Implements undo/redo functionality.
    - models.note: Defines the Note class.
    - logic.note_manager: Manages note creation and updates.
    - ui.components.note_editor: Provides the NoteEditor component.
    - ui.notes_editor: Provides the NotesEditor component.
    - notes.manager: Manages notes for tasks.

Author:
    Neils Haldane-Lutterodt
"""
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
from models.note import Note
from logic.note_manager import create_note, update_note
from ui.components.note_editor import NoteEditor
from ui.notes_editor import NotesEditor
from ui.notes_viewer import NotesViewer
from notes.manager import NotesManager

ALL_GROUPS_LABEL = "All Groups"
ALL_TAGS_LABEL = "All Tags"
NO_SELECTION_TITLE = "No Selection"
NO_SELECTION_MSG = "Please select a task."

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
        self.notes_manager = NotesManager()

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
        # Keyboard shortcuts for notes operations
        self.root.bind("<Control-Shift-n>", lambda _: self.context_menu_add_note())
        self.root.bind("<Control-Shift-v>", lambda _: self.context_menu_view_notes())

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
        options_menu.add_checkbutton(
            label="Show Only Tasks with Notes",
            variable=tk.BooleanVar(value=self.settings.get("filter_with_notes", False)),
            command=self.toggle_filter_with_notes
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
        tk.OptionMenu(control, self.sort_key, "due_date", "created_at", "priority", "sequence", command=lambda _: self.render_task_list()).grid(row=1, column=1)
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
        self.task_listbox.bind("<Button-3>", self.show_context_menu)
        scrollbar = tk.Scrollbar(list_frame, command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Add Note", command=self.context_menu_add_note)
        self.context_menu.add_command(label="View Notes", command=self.context_menu_view_notes)

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

    def _get_filtered_tasks(self):
        """
        Return tasks filtered by status, group, tag, and notes filter, then sorted.
        """
        tasks = filter_tasks(self.tasks, self.filter_mode.get(), self.group_filter.get())
        tag = self.tag_filter.get()
        if tag != ALL_TAGS_LABEL:
            tasks = [t for t in tasks if tag in t.tags]
        tasks = sort_tasks(tasks, self.sort_key.get())
        if self.settings.get("filter_with_notes", False):
            tasks = [t for t in tasks if len(self.notes_manager.get_notes_by_task(t.id)) > 0]
        return tasks

    def _format_task_display(self, t):
        """Return formatted display string for a task."""
        blocked = "⛔" if t.is_blocked(self.task_lookup) else ""
        tags = f" 🏷️ {', '.join(t.tags)}" if t.tags else ""
        recur = f" 🔁 {t.recurrence['frequency'].capitalize()}" if t.recurrence.get("frequency") != "none" else ""
        notes_count = len(self.notes_manager.get_notes_by_task(t.id))
        notes_icon = f" 📝({notes_count})" if notes_count > 0 else ""
        return f"[{t.sequence}] {'✔' if t.is_done() else ''} {t.task} [{t.group}] (Due: {t.due_date}){tags}{recur}{notes_icon} {blocked}"

    def render_task_list(self):
        try:
            selected_idx = self.task_listbox.curselection()[0]
        except IndexError:
            selected_idx = None

        self.visible_tasks = self._get_filtered_tasks()
        self.task_listbox.delete(0, tk.END)
        for t in self.visible_tasks:
            self.task_listbox.insert(tk.END, self._format_task_display(t))

        if selected_idx is not None and selected_idx < len(self.visible_tasks):
            self.task_listbox.select_set(selected_idx)

    def toggle_filter_with_notes(self):
        self.settings["filter_with_notes"] = not self.settings.get("filter_with_notes", False)
        self.save_all()
        self.render_task_list()

    def edit_notes_for_selected(self, event):
        """
        Open the NotesViewer for the selected task on double-click.
        """
        try:
            idx = self.task_listbox.nearest(event.y)
            task = self.visible_tasks[idx]
            self.open_notes_viewer(task)
        except IndexError:
            pass

    def open_notes_editor(self, task):
        # Prepare Note instance: convert raw notes if needed
        if isinstance(task.notes, Note):
            note = task.notes
        else:
            note = create_note(task.notes)
            task.notes = note
            task.note_id = note.id

        def save_callback(updated_note):
            # Persist changes to storage via note_manager
            try:
                persisted = update_note(
                    note_id=updated_note.id,
                    content=updated_note.content,
                    tags=updated_note.tags,
                    label=updated_note.label
                )
            except Exception as e:
                messagebox.showerror("Note Save Failed", str(e))
                return
            # Register undo/redo actions for note content changes
            old_content = note.content
            new_content = persisted.content
            def undo_action():
                update_note(persisted.id, content=old_content)
                note.content = old_content
                self.save_all()
            def redo_action():
                update_note(persisted.id, content=new_content)
                note.content = new_content
                self.save_all()
            self.undo_manager.register(undo_action, redo_action)
            # Update task's note reference and persist tasks
            task.notes = persisted
            task.note_id = persisted.id
            self.save_all()

        # Launch reusable NoteEditor component
        NoteEditor(self.root, note, save_callback)

    def open_notes_viewer(self, task):
        """
        Launch the NotesViewer for the given task.
        """
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return

        # Open the aggregated NotesViewer
        NotesViewer(self.root, task.id, self.notes_manager, self.save_all)

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
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)

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
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)

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

    def show_context_menu(self, event):
        try:
            self.task_listbox.selection_clear(0, tk.END)
            idx = self.task_listbox.nearest(event.y)
            self.task_listbox.selection_set(idx)
            self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def add_note_to_selected_task(self):
        selected_idx = self.task_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)
            return
        task = self.visible_tasks[selected_idx[0]]
        self.open_notes_editor(task)

    def view_notes_for_selected_task(self):
        selected_idx = self.task_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)
            return
        task_id = self.visible_tasks[selected_idx[0]].id
        notes = self.notes_manager.get_notes_by_task(task_id)
        if not notes:
            messagebox.showinfo("No Notes", "No notes found for the selected task.")
        else:
            # Placeholder for future notes browser implementation
            messagebox.showinfo("Notes", f"Found {len(notes)} note(s) for the task.")
    
    def context_menu_add_note(self):
        selected = self.controller.get_selected_tasks()
        if not selected:
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)
            return
        task = selected[0]
        self.open_notes_editor(task)

    def context_menu_view_notes(self):
        selected = self.controller.get_selected_tasks()
        if not selected:
            messagebox.showinfo(NO_SELECTION_TITLE, NO_SELECTION_MSG)
            return
        task = selected[0]
        # Open aggregated notes viewer
        self.open_notes_viewer(task)