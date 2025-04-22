'''
models/task.py - Task Data Model
Author: Neils Haldane-Lutterodt
'''

import uuid
from datetime import datetime


class Task:
    def __init__(
        self,
        task: str,
        group: str = "General",
        due_date: str = None,
        priority: str = "normal",
        status: str = "pending",
        sequence: int = 1,
        depends_on: str = None,
        notes: str = "",
        tags: list = None,
        recurrence: dict = None,
        task_id: str = None,
        created_at: str = None
    ):
        self.id = task_id or str(uuid.uuid4())
        self.task = task.strip()
        self.group = group.title().strip() or "General"
        self.due_date = due_date or datetime.now().date().isoformat()
        self.created_at = created_at or datetime.now().isoformat()
        self.priority = priority.lower()
        self.status = status.lower()
        self.sequence = sequence
        self.depends_on = depends_on
        self.notes = notes.strip()
        self.tags = tags if tags is not None else []
        self.recurrence = recurrence or {
            "frequency": "none",
            "interval": 1,
            "count": None,
            "end_date": None,
            "clone_type": "shallow"
        }

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
            "recurrence": self.recurrence
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            task=data.get("task", ""),
            group=data.get("group", "General"),
            due_date=data.get("due_date"),
            priority=data.get("priority", "normal"),
            status=data.get("status", "pending"),
            sequence=data.get("sequence", 1),
            depends_on=data.get("depends_on"),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            recurrence=data.get("recurrence"),
            task_id=data.get("id"),
            created_at=data.get("created_at")
        )

    def is_done(self) -> bool:
        return self.status == "done"

    def is_blocked(self, task_lookup: dict) -> bool:
        if not self.depends_on:
            return False
        dep = task_lookup.get(self.depends_on)
        return dep is not None and not dep.is_done()

    def __str__(self):
        return f"[{self.sequence}] {'✔' if self.is_done() else ''} {self.task} (Due: {self.due_date})"
