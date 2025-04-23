"""
Core Task Operations Module
This module provides the core logic for managing tasks, including toggling task statuses, handling recurring tasks, filtering and sorting tasks, and validating dependencies.

Classes:
    None

Functions:
    toggle_status(task: Task, task_lookup: Dict[str, Task]) -> Optional[Task]:
        Toggles the status of a task and handles recurring tasks.
    complete_task(task: Task, task_lookup: Dict[str, Task]) -> Task:
        Marks a task as completed and generates a summary note.
    is_recurring(task: Task) -> bool:
        Checks if a task is recurring.
    clone_recurring_task(task: Task, task_lookup: Dict[str, Task]) -> Task:
        Clones a recurring task based on its recurrence settings.
    compute_next_due_date(current_due: str, frequency: str, interval: int) -> str:
        Computes the next due date for a recurring task.
    shallow_clone(task: Task, new_due: str) -> Task:
        Creates a shallow copy of a task.
    recursive_deep_clone(original: Task, lookup: Dict[str, Task], new_due: str, id_map: Dict[str, str]) -> Task:
        Recursively clones a task and its subtasks.
    filter_tasks(tasks: List[Task], status: str = "All", group: str = "All Groups") -> List[Task]:
        Filters tasks based on status and group.
    sort_tasks(tasks: List[Task], key: str = "due_date") -> List[Task]:
        Sorts tasks based on a specified key.
    validate_dependency(child: Task, parent: Task) -> bool:
        Validates the dependency between two tasks.
    create_task_lookup(tasks: List[Task]) -> Dict[str, Task]:
        Creates a lookup dictionary for tasks.

Constants:
    recurrence_structure:
        A dictionary defining recurrence presets for task scheduling.

Dependencies:
    - typing: For type annotations.
    - datetime: For handling timestamps and date calculations.
    - uuid: For generating unique task IDs.
    - copy: For deep copying task objects.
    - models.task: Provides the Task model.
    - notes.manager: Provides the NotesManager class for managing notes.

Author:
    Neils Haldane-Lutterodt
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from uuid import uuid4
import copy

from models.task import Task
from notes.manager import NotesManager
from debug import debug_trace


# ==============================
# Core Task Status Operations
# ==============================

def toggle_status(task: Task, task_lookup: Dict[str, Task]) -> Optional[Task]:
    """Toggle task status if allowed. Returns cloned task if recurring."""
    if task.is_blocked(task_lookup):
        raise ValueError("This task is blocked by another incomplete task.")

    if hasattr(task, "subtasks") and task.subtasks:
        if any(not task_lookup[sub_id].is_done() for sub_id in task.subtasks if sub_id in task_lookup):
            raise ValueError("This task has incomplete subtasks.")

    task.status = "done" if task.status != "done" else "pending"

    if task.status == "done" and is_recurring(task):
        return clone_recurring_task(task, task_lookup)

    return None


notes_manager = NotesManager()

@debug_trace
def complete_task(task, task_lookup):
    """
    Mark a task as completed and auto-generate a summary note.

    Args:
        task (Task): The task to mark as completed.
        task_lookup (dict): A dictionary of tasks for dependency checks.

    Returns:
        Task: The updated task.
    """
    task.status = "done"
    task.updated_at = datetime.now().isoformat()

    # Auto-generate a summary note
    summary_content = f"Task '{task.task}' was completed on {task.updated_at}."
    notes_manager.create_note(content=summary_content, task_id=task.id)

    return task


# ==============================
# Recurring Task Cloning Logic
# ==============================

def is_recurring(task: Task) -> bool:
    r = task.recurrence or {}
    return r.get("frequency", "none") != "none"


def clone_recurring_task(task: Task, task_lookup: Dict[str, Task]) -> Task:
    """Clone task depending on clone_type (shallow or deep)."""
    freq = task.recurrence.get("frequency", "none")
    interval = task.recurrence.get("interval", 1)
    clone_type = task.recurrence.get("clone_type", "shallow")
    new_due = compute_next_due_date(task.due_date, freq, interval)

    id_map = {}

    return (
        recursive_deep_clone(task, task_lookup, new_due, id_map)
        if clone_type == "deep"
        else shallow_clone(task, new_due)
    )


def compute_next_due_date(current_due: str, frequency: str, interval: int) -> str:
    """Compute next due date from recurrence info."""
    due_date = datetime.fromisoformat(current_due)

    if frequency == "daily":
        return (due_date + timedelta(days=interval)).date().isoformat()
    elif frequency == "weekly":
        return (due_date + timedelta(weeks=interval)).date().isoformat()
    elif frequency == "monthly":
        new_month = due_date.month - 1 + interval
        year = due_date.year + new_month // 12
        month = new_month % 12 + 1
        day = min(due_date.day, 28)
        return due_date.replace(year=year, month=month, day=day).date().isoformat()
    elif frequency == "yearly":
        return due_date.replace(year=due_date.year + interval).date().isoformat()
    return due_date.date().isoformat()


def shallow_clone(task: Task, new_due: str) -> Task:
    """Create a shallow copy of a task (no subtasks)."""
    return Task(
        task=task.task,
        group=task.group,
        due_date=new_due,
        priority=task.priority,
        status="pending",
        sequence=task.sequence,
        notes=task.notes,
        tags=list(task.tags),
        recurrence=None,
        task_id=str(uuid4()),
        created_at=datetime.now().isoformat(),
        depends_on=task.depends_on
    )


def recursive_deep_clone(original: Task, lookup: Dict[str, Task], new_due: str, id_map: Dict[str, str]) -> Task:
    """Recursively clone task and subtasks, mapping old IDs to new ones."""
    base_due = datetime.fromisoformat(original.due_date)
    delta = datetime.fromisoformat(new_due) - base_due

    def clone_task_recursive(task: Task, parent: Optional[Task]) -> Task:
        new_id = str(uuid4())
        id_map[task.id] = new_id

        cloned = Task(
            task=task.task,
            group=task.group,
            due_date=(datetime.fromisoformat(task.due_date) + delta).date().isoformat(),
            priority=task.priority,
            status="pending",
            sequence=task.sequence,
            notes=task.notes,
            tags=list(task.tags),
            recurrence=None,
            depends_on=id_map.get(task.depends_on),
            task_id=new_id,
            created_at=datetime.now().isoformat()
        )

        # Handle subtasks
        cloned.subtasks = []
        for sub_id in getattr(task, "subtasks", []):
            sub = lookup.get(sub_id)
            if sub:
                cloned_sub = clone_task_recursive(sub, cloned)
                cloned.subtasks.append(cloned_sub.id)

        return cloned

    return clone_task_recursive(original, None)

# ==============================
# Filtering / Sorting Helpers
# ==============================

def filter_tasks(tasks: List[Task], status: str = "All", group: str = "All Groups") -> List[Task]:
    return [
        t for t in tasks
        if (status == "All" or t.status == status.lower())
        and (group == "All Groups" or t.group == group)
    ]


def sort_tasks(tasks: List[Task], key: str = "due_date") -> List[Task]:
    fallback = "9999-12-31" if key == "due_date" else 9999
    return sorted(tasks, key=lambda t: getattr(t, key, fallback) or fallback)


def validate_dependency(child: Task, parent: Task) -> bool:
    return child.due_date >= parent.due_date


def create_task_lookup(tasks: List[Task]) -> Dict[str, Task]:
    return {t.id: t for t in tasks}


# ==============================
# UI: Recurrence Preset Options
# ==============================

recurrence_structure = {
    "None": {
        "frequency": "none",
        "interval": 0,
        "clone_type": "shallow",
        "count": None,
        "end_date": None
    },
    "Daily": {
        "frequency": "daily",
        "interval": 1,
        "clone_type": "shallow",
        "count": None,
        "end_date": None
    },
    "Weekly": {
        "frequency": "weekly",
        "interval": 1,
        "clone_type": "shallow",
        "count": None,
        "end_date": None
    },
    "Monthly": {
        "frequency": "monthly",
        "interval": 1,
        "clone_type": "shallow",
        "count": None,
        "end_date": None
    },
    "Yearly": {
        "frequency": "yearly",
        "interval": 1,
        "clone_type": "shallow",
        "count": None,
        "end_date": None
    },
    "Weekly (Deep Clone)": {
        "frequency": "weekly",
        "interval": 1,
        "clone_type": "deep",
        "count": None,
        "end_date": None
    }
}
