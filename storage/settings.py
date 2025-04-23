"""
Settings Manager Module
This module provides functionality for managing application settings, including loading, saving, and validating settings against a predefined schema. It ensures that settings are consistent and automatically fixes missing or invalid entries.

Classes:
    None

Functions:
    _default_settings() -> dict:
        Returns a dictionary of default settings based on the schema.
    _validate(settings: dict) -> tuple[dict, bool]:
        Validates the settings against the schema and auto-fixes missing or invalid entries.
    _validate_nested(settings: dict, schema_defaults: dict) -> tuple[dict, bool]:
        Validates nested dictionary settings and auto-fixes missing or invalid entries.
    load_settings() -> dict:
        Loads settings from a file or returns defaults if the file is missing or invalid.
    save_settings(settings: dict) -> None:
        Saves validated settings to a file.

Constants:
    SETTINGS_FILE:
        The path to the settings JSON file.
    SETTINGS_SCHEMA:
        The schema defining the structure, types, and default values for settings.

Dependencies:
    - os: For file and directory operations.
    - json: For reading and writing JSON files.
    - logging: For logging errors and warnings.

Author:
    Neils Haldane-Lutterodt
"""

import os
import json
import logging

SETTINGS_FILE = "data/settings.json"

# ✅ Central schema for all settings
SETTINGS_SCHEMA = {
    "auto_sort": {"type": bool, "default": False},
    "default_sort": {"type": str, "default": "due_date"},
    "default_group": {"type": str, "default": "All Groups"},
    "ui_preferences": {
        "type": dict,
        "default": {
            "strict_mode": False,
            "dark_mode": False
        }
    }
}

def _default_settings():
    """Returns a fresh dict of all defaults."""
    return {key: val["default"] for key, val in SETTINGS_SCHEMA.items()}


def _validate(settings):
    """Ensures settings match schema and auto-fixes missing or invalid ones."""
    updated = False
    validated = {}

    for key, meta in SETTINGS_SCHEMA.items():
        expected_type = meta["type"]
        if key not in settings or not isinstance(settings[key], expected_type):
            validated[key] = meta["default"]
            updated = True
            logging.warning(f"Setting '{key}' missing or invalid. Reset to default: {meta['default']}")
        else:
            if isinstance(meta["default"], dict):  # Handle nested dictionaries
                validated[key], nested_updated = _validate_nested(settings[key], meta["default"])
                updated = updated or nested_updated
            else:
                validated[key] = settings[key]

    return validated, updated


def _validate_nested(settings, schema_defaults):
    """Validate nested dictionary settings."""
    updated = False
    validated = {}

    for key, default_value in schema_defaults.items():
        if key not in settings or not isinstance(settings[key], type(default_value)):
            validated[key] = default_value
            updated = True
            logging.warning(f"Nested setting '{key}' missing or invalid. Reset to default: {default_value}")
        else:
            validated[key] = settings[key]

    return validated, updated


def load_settings():
    """Load settings from file or return defaults with validation."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            validated, corrected = _validate(raw)
            if corrected:
                save_settings(validated)
            return validated
        except Exception as e:
            logging.error(f"[Settings] Failed to load: {e}")
    return _default_settings()


def save_settings(settings):
    """Save settings to file after validation."""
    validated, _ = _validate(settings)
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(validated, f, indent=4)
    logging.info("[Settings] Settings saved successfully.")