'''
storage/settings.py - Application Settings Management
Author: Neils Haldane-Lutterodt
'''

import os
import json

SETTINGS_FILE = "data/settings.json"
DEFAULT_SETTINGS = {
    "auto_sort": False,
    "default_sort": "due_date"
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("[Warning] Could not load settings:", e)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
