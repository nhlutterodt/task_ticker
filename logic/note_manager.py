"""
Note Manager Logic Module
This module provides utility functions for managing notes by delegating operations to the `NotesManager` class. It includes functions for creating, updating, deleting, and retrieving notes.

Classes:
    None

Functions:
    get_all_notes() -> list[Note]:
        Returns all stored notes.
    get_note_by_id(note_id: str) -> Note:
        Retrieves a single note by its ID.
    create_note(content: str, tags: list = None, label: str = None, task_id: str = None) -> Note:
        Creates a new note via the NotesManager.
    update_note(note_id: str, content: str = None, tags: list = None, label: str = None) -> Note:
        Updates an existing note via the NotesManager.
    delete_note(note_id: str) -> bool:
        Deletes a note by its ID via the NotesManager.
    delete_unlinked(linked_ids: set[str]) -> dict[str, Note]:
        Deletes notes not linked to any task via the NotesManager.

Constants:
    None

Dependencies:
    - notes.manager: Provides the NotesManager class for managing notes.

Author:
    Placeholder Author
"""

from notes.manager import NotesManager

# Delegate note operations to centralized manager
manager = NotesManager()

def get_all_notes():
    """Return all stored notes."""
    return manager.get_all_notes()

def get_note_by_id(note_id: str):
    """Retrieve a single Note by its ID."""
    return manager.get_note(note_id)

def create_note(content: str, tags: list = None, label: str = None, task_id: str = None):
    """Create a new note via NotesManager."""
    return manager.create_note(content, tags, label, task_id)

def update_note(note_id: str, content: str = None, tags: list = None, label: str = None):
    """Update an existing note via NotesManager."""
    return manager.update_note(note_id, content, tags, label)

def delete_note(note_id: str) -> bool:
    """Delete a note by its ID via NotesManager."""
    return manager.delete_note(note_id)

def delete_unlinked(linked_ids: set[str]):
    """Delete notes not linked to any task via NotesManager."""
    return manager.delete_unlinked(linked_ids)