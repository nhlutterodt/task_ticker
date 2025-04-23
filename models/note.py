"""
Note Model Module
This module defines the `Note` dataclass, which represents a note entity with attributes such as content, timestamps, tags, and history. It is designed to facilitate the management of notes in a task tracking or note-taking application.

Classes:
    Note:
        A dataclass representing a note with metadata and content.

Functions:
    to_dict() -> dict:
        Converts the Note instance into a dictionary for serialization.
    from_dict(data: dict) -> Note:
        Creates a Note instance from a dictionary.
    create(content: str, tags: Optional[list] = None, label: Optional[str] = None) -> Note:
        Creates a new Note instance with a unique ID and timestamps.

Attributes:
    id (str):
        A unique identifier for the note.
    content (str):
        The main content or body of the note.
    created_at (datetime):
        The timestamp when the note was created.
    updated_at (datetime):
        The timestamp when the note was last updated.
    tags (List[str]):
        A list of tags associated with the note for categorization.
    label (Optional[str]):
        An optional label for the note.
    history (List[str]):
        A list of historical changes or revisions of the note.
    task_id (Optional[str]):
        An optional identifier linking the note to a task.

Constants:
    None

Dependencies:
    - dataclasses: For defining the Note dataclass.
    - datetime: For handling timestamps.
    - typing: For type annotations.
    - uuid: For generating unique identifiers.

Author:
    Placeholder Author
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass
class Note:
    id: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    label: Optional[str] = None
    history: List[str] = field(default_factory=list)
    task_id: Optional[str] = None  # Link to associated task, if any

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "tags": self.tags,
            "label": self.label,
            "history": self.history,
            "task_id": self.task_id  # Ensure task_id is serialized
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data["id"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at"),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at"),
            tags=data.get("tags", []),
            label=data.get("label"),
            history=data.get("history", []),
            task_id=data.get("task_id")  # Ensure task_id is deserialized
        )

    @classmethod
    def create(cls, content: str, tags: Optional[list] = None, label: Optional[str] = None):
        """
        Create a new Note instance with a unique ID and timestamps.
        """
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            created_at=now,
            updated_at=now,
            tags=tags or [],
            label=label,
            history=[],
            task_id=None
        )