import os
import json
import logging
from typing import List
from models.note import Note

DATA_DIR = "data"
NOTES_STORE = os.path.join(DATA_DIR, "notes_records.json")


def ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_notes() -> List[Note]:
    """
    Load all notes from storage. Returns empty list if missing or corrupt.
    """
    ensure_data_dir()
    if not os.path.exists(NOTES_STORE):
        return []
    try:
        with open(NOTES_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Note.from_dict(item) for item in data]
    except Exception as e:
        logging.warning(f"[Notes Load Error] Failed to read or parse notes storage: {e}")
        return []


def save_notes(notes: List[Note]) -> None:
    """
    Save all notes to storage in JSON format.
    """
    ensure_data_dir()
    try:
        with open(NOTES_STORE, "w", encoding="utf-8") as f:
            json.dump([note.to_dict() for note in notes], f, indent=4)
    except Exception as e:
        logging.error(f"[Notes Save Error] Failed to write notes storage: {e}")


def get_notes_for_task(task_id: str) -> List[Note]:
    """
    Retrieve all notes linked to a specific task ID.
    """
    notes = load_notes()
    return [note for note in notes if note.task_id == task_id]