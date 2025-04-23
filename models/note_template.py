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