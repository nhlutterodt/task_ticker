'''
storage/file_io.py - File I/O for Tasks
Author: Neils Haldane-Lutterodt
'''

import os
import json
import shutil
from models.task import Task

TASKS_FILE = "data/tasks.json"
BACKUP_FILE = "data/tasks_backup.json"


def save_tasks(tasks):
    """Save list of Task instances to JSON."""
    if os.path.exists(TASKS_FILE):
        shutil.copy(TASKS_FILE, BACKUP_FILE)

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in tasks], f, indent=4)


def load_tasks():
    """Load tasks from file, return list of Task instances."""
    if not os.path.exists(TASKS_FILE):
        return []

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Task.from_dict(item) for item in data]
    except Exception as e:
        print("[Recovery] Error loading tasks:", e)
        return []


def backup_exists():
    return os.path.exists(BACKUP_FILE)


def recover_from_backup():
    if backup_exists():
        shutil.copy(BACKUP_FILE, TASKS_FILE)
        return load_tasks()
    return []
