'''
"""
================================
This module defines the `Task` and `TaskMeta` classes for managing tasks in the Task Ticker application.
Classes:
--------
- TaskMeta:
    Encapsulates metadata for a task, including:
    - Group: Categorization of the task.
    - Due Date: Deadline for the task.
    - Priority: Importance level (e.g., normal, high).
    - Status: Current state of the task (e.g., pending, done).
    - Sequence: Order of the task in a list.
    - Dependencies: Tasks that must be completed before this one.
    - Notes: Additional information about the task.
    - Tags: Labels for categorization.
    - Recurrence: Rules for repeating tasks.
    - Parent ID: Identifier for the parent task (if any).
    - Subtasks: List of IDs for dependent subtasks.
    - Task ID: Unique identifier for the task.
    - Created At: Timestamp of task creation.
- Task:
    Represents a task with the following features:
    - Serialization to and from dictionary format.
    - Dependency checks to determine if a task is blocked.
    - Status updates and checks (e.g., is_done).
    - Parent task blocking checks based on subtasks.
Methods:
--------
- Task.to_dict():
    Serializes the `Task` object into a dictionary.
- Task.from_dict(data: dict):
    Creates a `Task` object from a dictionary.
- Task.is_done() -> bool:
    Checks if the task's status is marked as "done".
- Task.is_blocked(task_lookup: dict) -> bool:
    Determines if the task is blocked by an incomplete dependency.
- Task.is_parent_blocked(task_lookup: dict) -> bool:
    Checks if the task is blocked due to any incomplete subtasks.
- Task.__str__():
    Returns a string representation of the task, including its sequence, status, and due date.
"""
models/task.py - Task Data Model
Author: Neils Haldane-Lutterodt

This module defines the Task and TaskMeta classes for managing tasks in the Task Ticker application.
- TaskMeta: Encapsulates metadata for a task, including priority, status, tags, and recurrence.
- Task: Represents a task with methods for serialization, dependency checks, and status updates.
'''

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Union
from dataclasses import dataclass, field
from models.note import Note


@dataclass
class TaskMeta:
    group: str = "General"
    due_date: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"
    sequence: int = 1
    depends_on: Optional[str] = None
    notes: Union[str, Note] = ""
    tags: List[str] = field(default_factory=list)
    recurrence: Dict = field(default_factory=lambda: {
        "frequency": "none", "interval": 1, "count": None, "end_date": None, "clone_type": "shallow"
    })
    parent_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    task_id: Optional[str] = None
    created_at: Optional[str] = None


class Task:
    def __init__(self, task: str, meta: Optional[TaskMeta] = None):
        m = meta or TaskMeta()
        self.id         = m.task_id or str(uuid.uuid4())
        self.task       = task.strip()
        self.group      = m.group.title().strip() or "General"
        self.due_date   = m.due_date or datetime.now().date().isoformat()
        self.created_at = m.created_at or datetime.now().isoformat()
        self.priority   = m.priority.lower()
        self.status     = m.status.lower()
        self.sequence   = m.sequence
        self.depends_on = m.depends_on
        # Support both raw string notes and Note instances
        if isinstance(m.notes, Note):
            self.notes = m.notes
        else:
            self.notes = m.notes.strip()
        self.note_id    = None  # New field for decoupling notes
        self.tags       = m.tags
        self.recurrence = m.recurrence
        self.parent_id  = m.parent_id
        self.subtasks   = m.subtasks

    def to_dict(self) -> dict:
        # Serialize task; include raw notes content or placeholder and correct note_id
        notes_value = self.notes.content if isinstance(self.notes, Note) else self.notes
        note_id_value = self.notes.id if isinstance(self.notes, Note) else self.note_id
        return {
            "id": self.id,
            "task": self.task,
            "group": self.group,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "priority": self.priority,
            "status": self.status,
            "sequence": self.sequence,
            "depends_on": self.depends_on,
            "notes": notes_value,
            "note_id": note_id_value,
            "tags": self.tags,
            "recurrence": self.recurrence,
            "parent_id": self.parent_id,
            "subtasks": self.subtasks
        }

    @classmethod
    def from_dict(cls, data: dict):
        meta = TaskMeta(
            group=data.get("group", "General"),
            due_date=data.get("due_date"),
            priority=data.get("priority", "normal"),
            status=data.get("status", "pending"),
            sequence=data.get("sequence", 1),
            depends_on=data.get("depends_on"),
            notes=data.get("notes", ""),  # May be raw string initially
            tags=data.get("tags", []),
            recurrence=data.get("recurrence"),
            parent_id=data.get("parent_id"),
            subtasks=data.get("subtasks", []),
            task_id=data.get("id"),
            created_at=data.get("created_at")
        )
        task = cls(task=data.get("task", ""), meta=meta)
        task.note_id = data.get("note_id")  # Load note_id if present
        return task

    def is_done(self) -> bool:
        return self.status == "done"

    def is_blocked(self, task_lookup: dict) -> bool:
        if not self.depends_on:
            return False
        dep = task_lookup.get(self.depends_on)
        return dep is not None and not dep.is_done()

    def is_parent_blocked(self, task_lookup: dict) -> bool:
        """Returns True if any subtask is not done."""
        for sub_id in self.subtasks:
            subtask = task_lookup.get(sub_id)
            if subtask and not subtask.is_done():
                return True
        return False

    def link_note(self, note: Note):
        self.notes = note
        self.note_id = note.id
        note.task_id = self.id

    def __str__(self):
        return f"[{self.sequence}] {'✔' if self.is_done() else ''} {self.task} (Due: {self.due_date})"
