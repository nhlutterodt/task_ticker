"""
File I/O Module for Tasks and Notes Management
This module provides functionality for managing tasks and notes, including saving and loading data to/from JSON files, ensuring the data directory structure, creating backups, and recovering from file corruption or missing files.

Classes:
    None

Functions:
    ensure_data_dir():
        Ensures the existence of the data directory.
    save_tasks(tasks: List[Task]) -> None:
        Saves a list of tasks to a JSON file, creating a backup of the previous file.
    load_notes() -> List[Note]:
        Loads notes from a JSON file. Returns an empty list if the file is missing or corrupt.
    load_tasks() -> List[Task]:
        Loads tasks from a JSON file. Links tasks to their associated notes if applicable. Returns an empty list if the file is missing or corrupt.
    backup_exists() -> bool:
        Checks if a backup file exists.
    recover_from_backup() -> List[Task]:
        Recovers tasks from a backup file if available. Returns the loaded list or an empty list.

Constants:
    DATA_DIR:
        The directory where data files are stored.
    TASKS_FILE:
        The path to the tasks JSON file.
    BACKUP_FILE:
        The path to the backup JSON file for tasks.
    NOTES_FILE:
        The path to the notes JSON file.

Dependencies:
    - os: For file and directory operations.
    - json: For reading and writing JSON files.
    - shutil: For file backup and recovery operations.
    - logging: For logging errors and warnings.
    - typing: For type annotations.
    - models.task: Provides the Task class for task management.
    - models.note: Provides the Note class for note management.
    - logic.note_manager: Provides the get_note_by_id function for linking notes to tasks.

Author:
    Neils Haldane-Lutterodt
"""

import os
import json
import shutil
import logging
from typing import List
from models.task import Task
from models.note import Note
from logic.note_manager import get_note_by_id

DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
BACKUP_FILE = os.path.join(DATA_DIR, "tasks_backup.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")


def ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_tasks(tasks: List[Task]) -> None:
    """
    Save tasks to JSON file. Auto-backs up the previous file first.
    """
    ensure_data_dir()

    if os.path.exists(TASKS_FILE):
        try:
            shutil.copy(TASKS_FILE, BACKUP_FILE)
        except Exception as e:
            logging.warning(f"[Backup Error] Could not backup task file: {e}")

    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in tasks], f, indent=4)
    except Exception as e:
        logging.error(f"[Save Error] Failed to write tasks: {e}")


def load_notes() -> List[Note]:
    """
    Load notes from file. If file is missing or corrupt, returns an empty list.
    """
    ensure_data_dir()

    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Note(**item) for item in data]
    except Exception as e:
        logging.warning(f"[Load Error] Failed to read or parse notes file: {e}")
        return []


def load_tasks() -> List[Task]:
    """
    Load tasks from file. If file is missing or corrupt, returns an empty list.
    """
    ensure_data_dir()

    if not os.path.exists(TASKS_FILE):
        return []

    # Load standalone notes for linking
    # Note: load standalone Note records for existing tasks
    # load_notes from storage.file_io.load_notes isn't for Note records; use note_manager
    # Use get_note_by_id for linking
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = [Task.from_dict(item) for item in data]
        for task in tasks:
            if task.note_id:
                note = get_note_by_id(task.note_id)
                if note:
                    task.notes = note
        return tasks
    except Exception as e:
        logging.warning(f"[Load Error] Failed to read or parse tasks file: {e}")
        return []


def backup_exists() -> bool:
    """Returns True if a backup file exists."""
    return os.path.exists(BACKUP_FILE)


def recover_from_backup() -> List[Task]:
    """
    Recover task list from backup if available. Returns loaded list or empty.
    """
    if backup_exists():
        try:
            shutil.copy(BACKUP_FILE, TASKS_FILE)
            return load_tasks()
        except Exception as e:
            logging.error(f"[Recovery Error] Failed to recover from backup: {e}")
    return []
