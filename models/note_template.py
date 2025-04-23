"""
Note Template Module
This module defines the `NoteTemplate` class, which represents a template for notes. It includes attributes for the template's name, content, and associated tags, as well as methods for serialization and deserialization.

Classes:
    NoteTemplate:
        Represents a note template with attributes for name, content, and tags.

Functions:
    to_dict() -> dict:
        Converts the NoteTemplate instance into a dictionary for serialization.
    from_dict(data: dict) -> NoteTemplate:
        Creates a NoteTemplate instance from a dictionary.

Constants:
    None

Dependencies:
    - typing: For type annotations.

Author:
    Placeholder Author
"""

from typing import List

class NoteTemplate:
    def __init__(self, name: str, content: str, tags: List[str] = None):
        self.name = name
        self.content = content
        self.tags = tags or []

    def to_dict(self):
        return {"name": self.name, "content": self.content, "tags": self.tags}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(name=data["name"], content=data["content"], tags=data.get("tags", []))