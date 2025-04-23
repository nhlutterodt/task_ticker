"""
Task Validation Logic Module
This module contains functions and logic to validate tasks and task graphs. It ensures tasks adhere to defined rules, checks for dependency issues, detects cycles, and validates group-based constraints such as unique task names and priority exclusivity.

Classes:
    None

Functions:
    validate_task_creation(task: Task, task_lookup: Dict[str, Task], rules: Optional[Dict] = None) -> dict:
        Validates a single task against rules during creation.
    validate_task_graph(tasks: List[Task], rules: Optional[Dict] = None) -> Dict:
        Validates a collection of tasks for structural and rule-based issues.
    validate_batch_conflicts(tasks: List[Task]) -> bool:
        Checks for conflicting high-priority tasks in a batch.
    validate_note_link(note_id: str, linked_ids: set[str]) -> bool:
        Validates the integrity of task-note references.

Constants:
    DEFAULT_RULES:
        A dictionary of default validation rules.

Dependencies:
    - typing: For type annotations.
    - datetime: For handling timestamps.
    - logging: For logging validation issues.
    - models.task: Provides the Task model.

Author:
    Neils Haldane-Lutterodt
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging
from models.task import Task


DEFAULT_RULES = {
    "strict_mode": False,
    "dependency_order": True,
    "group_priority_exclusive": True,
    "group_unique_names": True,
}


def validate_task_creation(task: Task, task_lookup: Dict[str, Task], rules: Optional[Dict] = None) -> dict:
    """Validate a single task on creation based on configured rules."""
    rules = rules or DEFAULT_RULES.copy()
    warn, block = False, False
    message = ""

    # Rule 1: Prevent self-dependency
    if task.depends_on == task.id:
        return {"warn": True, "block": True, "message": "Task cannot depend on itself."}

    # Rule 2: Due date must follow dependency
    if rules.get("dependency_order", True) and task.depends_on:
        parent = task_lookup.get(task.depends_on)
        if parent and task.due_date < parent.due_date:
            message = "Task is due before its dependency."
            warn = True
            block = rules.get("strict_mode", False)

    # Rule 3: Task name must be unique within group
    if rules.get("group_unique_names", False):
        duplicates = [
            t for t in task_lookup.values()
            if t.task == task.task and t.group == task.group and t.id != task.id
        ]
        if duplicates:
            message = f"Task '{task.task}' already exists in group '{task.group}'."
            warn = True
            block = rules.get("strict_mode", False)

    # Rule 4: Only one high-priority task per group
    if rules.get("group_priority_exclusive", False) and task.priority == "high":
        conflicts = [
            t for t in task_lookup.values()
            if t.group == task.group and t.priority == "high" and t.id != task.id
        ]
        if conflicts:
            message = f"Another high-priority task already exists in group '{task.group}'."
            warn = True
            block = rules.get("strict_mode", False)

    return {"warn": warn, "block": block, "message": message}


def validate_task_graph(tasks: List[Task], rules: Optional[Dict] = None) -> Dict:
    """Validate task graph for cycles, missing links, and group-based rules."""
    rules = rules or DEFAULT_RULES.copy()
    task_lookup = {t.id: t for t in tasks}
    visited = set()
    stack = set()

    errors = []
    warnings = []

    def dfs(task: Task, path: List[str]):
        if task.id in stack:
            cycle_path = path[path.index(task.id):] + [task.id]
            errors.append("Cycle detected: " + " → ".join(cycle_path))
            return
        if task.id in visited:
            return

        stack.add(task.id)
        visited.add(task.id)

        # Dependency checks
        if task.depends_on:
            dep = task_lookup.get(task.depends_on)
            if not dep:
                errors.append(f"{task.task} depends on missing task ID {task.depends_on}")
            else:
                if rules.get("dependency_order", True) and task.due_date < dep.due_date:
                    errors.append(f"{task.task} is due before dependency {dep.task}")
                dfs(dep, path + [task.id])

        # Subtask checks
        for sub_id in getattr(task, "subtasks", []):
            if sub_id not in task_lookup:
                warnings.append(f"{task.task} has missing subtask ID {sub_id}")
            else:
                dfs(task_lookup[sub_id], path + [task.id])

        stack.remove(task.id)

    for task in tasks:
        if task.id not in visited:
            dfs(task, [])

    # Rule: Only one high-priority task per group
    if rules.get("group_priority_exclusive", False):
        high_priority_seen = {}
        for t in tasks:
            if t.priority == "high":
                if t.group in high_priority_seen:
                    errors.append(f"Multiple high-priority tasks in group '{t.group}'")
                else:
                    high_priority_seen[t.group] = t.id

    # Rule: Unique task names within group
    if rules.get("group_unique_names", False):
        seen_names = set()
        for t in tasks:
            key = (t.group, t.task)
            if key in seen_names:
                errors.append(f"Duplicate task '{t.task}' in group '{t.group}'")
            seen_names.add(key)

    # Build final report
    report = {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validated_at": datetime.now().isoformat(),
        "affected_tasks": list(visited),
    }

    for issue in errors + warnings:
        logging.warning(f"Validation issue: {issue}")

    if rules.get("strict_mode", False) and errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors))

    return report


def validate_batch_conflicts(tasks: List[Task]) -> bool:
    """
    Ensure no conflicting high-priority tasks exist in the batch selection.
    Returns True if valid, False if conflicts detected.
    """
    seen = {}
    for t in tasks:
        if t.priority == "high":
            if t.group in seen:
                return False
            seen[t.group] = True
    return True


def validate_note_link(note_id: str, linked_ids: set[str]) -> bool:
    """
    Validate if a note ID is linked to any task.

    Args:
        note_id (str): The ID of the note to validate.
        linked_ids (set[str]): Set of note IDs that are linked to tasks.

    Returns:
        bool: True if the note ID is linked, False otherwise.
    """
    return note_id in linked_ids
