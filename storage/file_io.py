'''
storage/file_io.py - File I/O for Tasks
Author: Neils Haldane-Lutterodt
'''

import os
import json
import shutil
import logging
from typing import List
from models.task import Task

DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
BACKUP_FILE = os.path.join(DATA_DIR, "tasks_backup.json")


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


def load_tasks() -> List[Task]:
    """
    Load tasks from file. If file is missing or corrupt, returns an empty list.
    """
    ensure_data_dir()

    if not os.path.exists(TASKS_FILE):
        return []

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Task.from_dict(item) for item in data]
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
