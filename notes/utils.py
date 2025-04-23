"""
Notes Utilities Module
This module provides utility functions for handling notes, including parsing links, comparing notes, and exporting notes in various formats. It also includes functionality for computing differences between note versions and fetching notes by task ID.

Classes:
    None

Functions:
    parse_links(content: str) -> Dict[str, List[str]]:
        Extracts URLs, hashtags, and mentions from the given text content.
    parse_mentions_hashtags_urls(content: str) -> Dict[str, List[str]]:
        Extracts URLs, hashtags, and mentions from the given text content.
    diff_notes(old: Note, new: Note) -> Dict[str, List[str]]:
        Compares two notes and returns the differences in their content, tags, labels, and updated_at timestamp.
    export_notes(notes: Dict[str, Note], format: str = "json") -> str:
        Exports a dictionary of notes to the specified format, either JSON or Markdown.
    get_notes_by_task_id(notes: dict[str, Note], task_id: str) -> list[Note]:
        Fetches notes associated with a specific task ID.
    diff_note_versions(old_content: str, new_content: str) -> dict:
        Computes the differences between two versions of note content.

Constants:
    None

Dependencies:
    - json: For JSON serialization.
    - datetime: For handling timestamps.
    - re: For regular expression operations.
    - typing: For type annotations.
    - models.note: Provides the Note model.

Author:
    Neils Haldane-Lutterodt
"""

import json
from datetime import datetime   
import re
from typing import List, Dict
from models.note import Note

def parse_links(content: str) -> dict:
    """
    Parse note text for clickable @mentions, #hashtags, and URLs.

    Args:
        content (str): The note content to parse.

    Returns:
        dict: A dictionary with lists of mentions, hashtags, and URLs.
    """
    mentions = re.findall(r"@\w+", content)
    hashtags = re.findall(r"#\w+", content)
    urls = re.findall(r"https?://\S+", content)

    return {
        "mentions": mentions,
        "hashtags": hashtags,
        "urls": urls
    }

def parse_mentions_hashtags_urls(content: str) -> dict:
    """
    Parse note text for clickable @mentions, #hashtags, and URLs.

    Args:
        content (str): The note content to parse.

    Returns:
        dict: A dictionary with lists of mentions, hashtags, and URLs.
    """
    mentions = re.findall(r"@\w+", content)
    hashtags = re.findall(r"#\w+", content)
    urls = re.findall(r"https?://\S+", content)

    return {
        "mentions": mentions,
        "hashtags": hashtags,
        "urls": urls
    }

def diff_notes(old: Note, new: Note) -> Dict[str, List[str]]:
    """Compare two notes and return the differences."""
    diffs = {}
    if old.content != new.content:
        diffs["content"] = [old.content, new.content]
    if old.tags != new.tags:
        diffs["tags"] = [old.tags, new.tags]
    if old.label != new.label:
        diffs["label"] = [old.label, new.label]
    if old.updated_at != new.updated_at:
        diffs["updated_at"] = [old.updated_at.isoformat(), new.updated_at.isoformat()]
    return diffs

def export_notes(notes: Dict[str, Note], format: str = "json") -> str:
    """Export notes to the specified format (JSON or Markdown)."""
    if format == "json":
        return json.dumps({note_id: note.to_dict() for note_id, note in notes.items()}, indent=4)
    elif format == "markdown":
        return "\n\n".join(f"# {note.label or 'Note'}\n{note.content}" for note in notes.values())
    else:
        raise ValueError("Unsupported format. Use 'json' or 'markdown'.")

def get_notes_by_task_id(notes: dict[str, Note], task_id: str) -> list[Note]:
    """
    Fetch notes associated with a specific task ID.

    Args:
        notes (dict[str, Note]): Dictionary of notes keyed by note ID.
        task_id (str): The task ID to filter notes by.

    Returns:
        list[Note]: List of notes linked to the given task ID.
    """
    return [note for note in notes.values() if note.task_id == task_id]

def diff_note_versions(old_content: str, new_content: str) -> dict:
    """
    Compute the differences between two versions of note content.

    Args:
        old_content (str): The original content of the note.
        new_content (str): The updated content of the note.

    Returns:
        dict: A dictionary with 'added' and 'removed' keys showing the differences.
    """
    return {
        "removed": [line for line in old_content.splitlines() if line not in new_content.splitlines()],
        "added": [line for line in new_content.splitlines() if line not in old_content.splitlines()]
    }