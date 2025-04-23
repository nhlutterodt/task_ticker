"""
Note I/O Module
This module provides functionality for managing notes stored in a JSON file. It includes methods for loading notes, saving notes, and retrieving notes associated with specific tasks.

Classes:
    None

Functions:
    ensure_data_dir():
        Ensures the existence of the data directory for storing notes.
    load_notes() -> dict[str, Note]:
        Loads notes from a JSON file as a dictionary of Note instances keyed by note ID.
    save_notes(notes: dict[str, Note]) -> None:
        Saves notes to a JSON file as a dictionary keyed by note ID.
    get_notes_for_task(task_id: str) -> list[Note]:
        Retrieves all notes associated with a specific task ID.

Constants:
    DATA_DIR:
        The directory where the notes JSON file is stored.
    NOTES_FILE:
        The path to the notes JSON file.

Dependencies:
    - os: For file and directory operations.
    - json: For reading and writing JSON files.
    - logging: For logging errors and warnings.
    - models.note: Provides the Note class for note management.

Author:
    Placeholder Author
"""

import os
import json
import logging
from models.note import Note

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_notes() -> dict[str, Note]:
    """
    Load notes from JSON file as a dictionary of Note instances keyed by note.id.
    """
    ensure_data_dir()
    if not os.path.exists(NOTES_FILE):
        return {}
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {note_id: Note.from_dict(note_data) for note_id, note_data in data.items()}
    except Exception as e:
        logging.warning(f"[Notes Load Error] Failed to read or parse notes storage: {e}")
        return {}

def save_notes(notes: dict[str, Note]) -> None:
    """
    Save notes to JSON file as a dictionary keyed by note.id.
    """
    ensure_data_dir()
    try:
        data = {note_id: note.to_dict() for note_id, note in notes.items()}
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"[Notes Save Error] Failed to write notes storage: {e}")

def get_notes_for_task(task_id: str) -> list[Note]:
    """
    Retrieve all notes associated with a specific task ID.
    """
    notes = load_notes()
    return [note for note in notes.values() if note.task_id == task_id]
