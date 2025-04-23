'''
models/task.py - Task Data Model
Author: Neils Haldane-Lutterodt
'''

import uuid
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class TaskMeta:
    group: str = "General"
    due_date: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"
    sequence: int = 1
    depends_on: Optional[str] = None
    notes: str = ""
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
        self.notes      = m.notes.strip()
        self.tags       = m.tags
        self.recurrence = m.recurrence
        self.parent_id  = m.parent_id
        self.subtasks   = m.subtasks

    def to_dict(self) -> dict:
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
            "notes": self.notes,
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
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            recurrence=data.get("recurrence"),
            parent_id=data.get("parent_id"),
            subtasks=data.get("subtasks", []),
            task_id=data.get("id"),
            created_at=data.get("created_at")
        )
        return cls(task=data.get("task", ""), meta=meta)

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

    def __str__(self):
        return f"[{self.sequence}] {'✔' if self.is_done() else ''} {self.task} (Due: {self.due_date})"
