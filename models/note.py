"""
Dataclass:
    Note:
Module: note
Filepath: task_ticker/models/note.py
This module defines the `Note` dataclass, which represents a note entity with 
attributes such as content, timestamps, tags, and history. It is designed to 
facilitate the management of notes in a task tracking or note-taking application.
Classes:
    - Note: A dataclass representing a note with metadata and content.
Attributes:
    id (str): A unique identifier for the note.
    content (str): The main content or body of the note.
    created_at (datetime): The timestamp when the note was created.
    updated_at (datetime): The timestamp when the note was last updated.
    tags (List[str]): A list of tags associated with the note for categorization.
    label (Optional[str]): An optional label for the note.
    history (List[str]): A list of historical changes or revisions of the note.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Note:
    id: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    label: Optional[str] = None
    history: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "tags": self.tags,
            "label": self.label,
            "history": self.history
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
            history=data.get("history", [])
        )