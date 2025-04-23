'''
logic/validation.py - Task Validation Logic
Author: Neils Haldane-Lutterodt
'''

from typing import List, Dict
from datetime import datetime
import logging
from models.task import Task


def validate_task_creation(task: Task, task_lookup: Dict[str, Task], strict: bool = False) -> dict:
    """
    Validates a single task during creation.
    Returns a dict with:
    {
        "warn": bool,
        "block": bool,
        "message": str
    }
    """
    msg = ""
    block = False
    warn = False

    # Prevent due before dependency
    if task.depends_on:
        parent = task_lookup.get(task.depends_on)
        if parent and task.due_date < parent.due_date:
            msg = "Task is due before its dependency."
            warn = True
            block = strict

    # Prevent self-dependency
    if task.depends_on == task.id:
        msg = "Task cannot depend on itself."
        block = True

    # Future checks: cycle detection, same-sequence duplication, etc.

    return {"warn": warn, "block": block, "message": msg}


def validate_task_graph(tasks: List[Task], strict: bool = False) -> Dict:
    """
    Validates task relationships: cycles, dependency order, and missing links.
    Returns a validation report.
    """
    task_lookup = {t.id: t for t in tasks}
    visited = set()
    stack = set()
    cycles = []
    missing = []
    date_conflicts = []

    def dfs(task: Task, path: List[str]):
        if task.id in stack:
            cycle_path = path[path.index(task.id):] + [task.id]
            cycles.append(" → ".join(cycle_path))
            return
        if task.id in visited:
            return

        stack.add(task.id)
        visited.add(task.id)

        # Dependency validation
        if task.depends_on and task.depends_on not in task_lookup:
            missing.append(f"{task.task} depends on missing task ID {task.depends_on}")
        elif task.depends_on:
            dep = task_lookup[task.depends_on]
            if task.due_date < dep.due_date:
                date_conflicts.append(f"{task.task} is due before dependency {dep.task}")

        # Subtask validation
        for sub_id in getattr(task, 'subtasks', []):
            if sub_id not in task_lookup:
                missing.append(f"{task.task} has missing subtask ID {sub_id}")
            else:
                dfs(task_lookup[sub_id], path + [task.id])

        # Check dependency path
        if task.depends_on and task.depends_on in task_lookup:
            dfs(task_lookup[task.depends_on], path + [task.id])

        stack.remove(task.id)

    for task in tasks:
        if task.id not in visited:
            dfs(task, [])

    errors = cycles + missing + date_conflicts
    report = {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": [],
        "validated_at": datetime.now().isoformat(),
        "affected_tasks": list(visited),
    }

    for e in errors:
        logging.warning(f"Validation issue: {e}")

    if strict and errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors))

    return report
