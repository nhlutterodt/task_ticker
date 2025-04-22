'''
logic/operations.py - Core Task Operations
Author: Neils Haldane-Lutterodt
'''

from typing import List
from models.task import Task


def toggle_status(task: Task, task_lookup: dict):
    """Toggle between 'done' and 'pending' if dependencies allow."""
    if task.depends_on:
        parent = task_lookup.get(task.depends_on)
        if parent and not parent.is_done():
            raise ValueError(f"Cannot mark task done. Dependency '{parent.task}' not completed.")
    task.status = "done" if task.status != "done" else "pending"


def filter_tasks(tasks: List[Task], status: str = "All", group: str = "All Groups"):
    filtered = tasks
    if status != "All":
        filtered = [t for t in filtered if t.status == status.lower()]
    if group != "All Groups":
        filtered = [t for t in filtered if t.group == group]
    return filtered


def sort_tasks(tasks: List[Task], key: str = "due_date"):
    fallback = "9999-12-31" if key == "due_date" else 9999
    return sorted(tasks, key=lambda t: getattr(t, key, fallback) or fallback)


def validate_dependency(child: Task, parent: Task):
    """Warn if child depends on parent but has an earlier due date."""
    if child.due_date < parent.due_date:
        return False
    return True


def create_task_lookup(tasks: List[Task]):
    return {t.id: t for t in tasks}
