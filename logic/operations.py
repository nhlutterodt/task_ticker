'''
logic/operations.py - Core Task Operations
Author: Neils Haldane-Lutterodt
'''

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import copy
from uuid import uuid4
from models.task import Task


def toggle_status(task: Task, task_lookup: Dict[str, Task]) -> Optional[Task]:
    """Toggle between 'done' and 'pending' if dependencies allow. Return next recurrence if applicable."""
    if task.is_blocked(task_lookup):
        raise ValueError("This task is blocked by another incomplete task.")
    
    if task.subtasks:
        if task.is_parent_blocked(task_lookup):
            raise ValueError("This task has incomplete subtasks.")
    
    task.status = "done" if task.status != "done" else "pending"

    if task.status == "done" and is_recurring(task):
        return clone_recurring_task(task, task_lookup)

    return None


def is_recurring(task: Task) -> bool:
    r = task.recurrence
    return r is not None and r.get("frequency", "none") != "none"


def clone_recurring_task(task: Task, task_lookup: Dict[str, Task]) -> Task:
    """
    Clone a recurring task and its subtasks recursively, adjusting IDs and due dates.
    Returns the new parent task.
    """
    freq = task.recurrence.get("frequency", "none")
    interval = task.recurrence.get("interval", 1)
    clone_type = task.recurrence.get("clone_type", "shallow")
    new_due = compute_next_due_date(task.due_date, freq, interval)

    id_map = {}

    if clone_type == "deep":
        new_parent = recursive_deep_clone(task, task_lookup, new_due, id_map)
    else:
        new_parent = shallow_clone(task, new_due)

    return new_parent


def compute_next_due_date(current_due: str, frequency: str, interval: int) -> str:
    """Compute the next due date for a recurring task."""
    due_date = datetime.fromisoformat(current_due)
    
    if frequency == "daily":
        next_due = due_date + timedelta(days=interval)
    elif frequency == "weekly":
        next_due = due_date + timedelta(weeks=interval)
    elif frequency == "monthly":
        month = due_date.month - 1 + interval
        year = due_date.year + month // 12
        month = month % 12 + 1
        day = min(due_date.day, 28)
        next_due = due_date.replace(year=year, month=month, day=day)
    elif frequency == "yearly":
        next_due = due_date.replace(year=due_date.year + interval)
    else:
        next_due = due_date

    return next_due.date().isoformat()


def shallow_clone(task: Task, new_due: str) -> Task:
    """Clone a single task (no subtasks)."""
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
        parent_id=task.parent_id,
        depends_on=task.depends_on,
        subtasks=[],
        task_id=str(uuid4()),
        created_at=datetime.now().isoformat()
    )


def recursive_deep_clone(original: Task, lookup: Dict[str, Task], new_due: str, id_map: Dict[str, str]) -> Task:
    """
    Recursively clone a task and all its subtasks with updated relationships.
    """
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
            parent_id=parent.id if parent else None,
            depends_on=id_map.get(task.depends_on) if task.depends_on else None,
            subtasks=[],
            task_id=new_id,
            created_at=datetime.now().isoformat()
        )

        for sub_id in task.subtasks:
            subtask = lookup.get(sub_id)
            if subtask:
                cloned_sub = clone_task_recursive(subtask, cloned)
                cloned.subtasks.append(cloned_sub.id)

        return cloned

    return clone_task_recursive(original, None)


def filter_tasks(tasks: List[Task], status: str = "All", group: str = "All Groups") -> List[Task]:
    """Filter by status and group."""
    return [
        t for t in tasks
        if (status == "All" or t.status == status.lower())
        and (group == "All Groups" or t.group == group)
    ]


def sort_tasks(tasks: List[Task], key: str = "due_date") -> List[Task]:
    """Sort tasks based on a chosen key."""
    fallback = "9999-12-31" if key == "due_date" else 9999
    return sorted(tasks, key=lambda t: getattr(t, key, fallback) or fallback)


def validate_dependency(child: Task, parent: Task) -> bool:
    """Ensure child task has due date after its dependency."""
    return child.due_date >= parent.due_date


def create_task_lookup(tasks: List[Task]) -> Dict[str, Task]:
    """Returns a dictionary of tasks indexed by their ID."""
    return {t.id: t for t in tasks}
# -----------------------------------
# Recurrence Presets for UI Dropdown
# -----------------------------------
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
