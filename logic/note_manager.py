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