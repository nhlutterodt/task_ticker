import uuid
from datetime import datetime
from typing import List, Optional
from models.note import Note
from storage.notes import load_notes, save_notes


def get_all_notes() -> List[Note]:
    """Return all stored notes."""
    return load_notes()


def get_note_by_id(note_id: str) -> Optional[Note]:
    """Retrieve a single Note by its ID."""
    notes = load_notes()
    for note in notes:
        if note.id == note_id:
            return note
    return None


def create_note(content: str, tags: Optional[List[str]] = None, label: Optional[str] = None) -> Note:
    """Create a new note, save it, and return it."""
    now = datetime.now()
    note = Note(
        id=str(uuid.uuid4()),
        content=content,
        created_at=now,
        updated_at=now,
        tags=tags or [],
        label=label,
        history=[]
    )
    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    return note


def update_note(note_id: str, content: Optional[str] = None, tags: Optional[List[str]] = None, label: Optional[str] = None) -> Note:
    """Update an existing note's content, tags, or label with history tracking."""
    notes = load_notes()
    updated_note = None
    for idx, note in enumerate(notes):
        if note.id == note_id:
            # Record old content in history
            note.history.append(note.content)
            if content is not None:
                note.content = content
            if tags is not None:
                note.tags = tags
            if label is not None:
                note.label = label
            note.updated_at = datetime.now()
            updated_note = note
            notes[idx] = note
            break
    if not updated_note:
        raise ValueError(f"Note with id {note_id} not found")
    save_notes(notes)
    return updated_note


def delete_note(note_id: str) -> bool:
    """Delete a note by its ID. Returns True if deleted."""
    notes = load_notes()
    filtered = [n for n in notes if n.id != note_id]
    if len(filtered) == len(notes):
        return False
    save_notes(filtered)
    return True


def delete_unlinked(notes: dict[str, Note], linked_ids: set[str]) -> dict[str, Note]:
    """
    Delete notes that are not linked to any task.

    Args:
        notes (dict[str, Note]): Dictionary of notes keyed by note ID.
        linked_ids (set[str]): Set of note IDs that are linked to tasks.

    Returns:
        dict[str, Note]: Updated dictionary of notes with unlinked notes removed.
    """
    return {note_id: note for note_id, note in notes.items() if note_id in linked_ids}