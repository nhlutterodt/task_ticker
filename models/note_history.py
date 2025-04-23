"""
Note History Module
This module defines the `NoteHistory` class, which manages the version history of notes. It provides methods for adding new versions, retrieving the history of a specific note, and computing differences between two versions of note content.

Classes:
    NoteHistory:
        Manages the version history of notes, including adding versions, retrieving history, and computing differences.

Functions:
    __init__():
        Initializes the NoteHistory instance with an empty history list.
    add_version(note_id: str, content: str):
        Adds a new version of a note to the history with a timestamp.
    get_history(note_id: str) -> List[Dict]:
        Retrieves the version history for a specific note ID.
    diff_versions(old_content: str, new_content: str) -> Dict:
        Computes the differences between two versions of note content.

Constants:
    None

Dependencies:
    - typing: For type annotations.
    - datetime: For handling timestamps.

Author:
    Placeholder Author
"""

from typing import List, Dict
from datetime import datetime

class NoteHistory:
    def __init__(self):
        self.history = []

    def add_version(self, note_id: str, content: str):
        self.history.append({"note_id": note_id, "content": content, "timestamp": datetime.now().isoformat()})

    def get_history(self, note_id: str) -> List[Dict]:
        return [entry for entry in self.history if entry["note_id"] == note_id]

    def diff_versions(self, old_content: str, new_content: str) -> Dict:
        return {
            "removed": [line for line in old_content.splitlines() if line not in new_content.splitlines()],
            "added": [line for line in new_content.splitlines() if line not in old_content.splitlines()]
        }