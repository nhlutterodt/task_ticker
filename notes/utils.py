'''
Module: utils.py
Description:
    This module provides utility functions for handling notes. It includes 
    functionalities for parsing links, comparing notes, and exporting notes 
    in various formats. The utilities are designed to work with the `Note` 
    model and support operations such as extracting URLs, hashtags, and 
    mentions, identifying differences between notes, and exporting notes 
    in JSON or Markdown formats.
Functions:
    - parse_links(content: str) -> Dict[str, List[str]]:
        Extracts URLs, hashtags, and mentions from the given text content.
    - diff_notes(old: Note, new: Note) -> Dict[str, List[str]]:
        Compares two notes and returns the differences in their content, 
        tags, and labels.
    - export_notes(notes: List[Note], format: str = "json") -> str:
        Exports a list of notes to the specified format, either JSON or 
        Markdown. Raises a ValueError for unsupported formats.
Dependencies:
    - json
    - datetime
    - re
    - typing (List, Dict)
    - models.note (Note)
File: notes/utils.py
Author: Neils Haldane-Lutterodt
Description: Utility functions for handling notes, including parsing links, 
             comparing notes, and exporting notes in various formats.
'''

import json
from datetime import datetime   
import re
from typing import List, Dict
from models.note import Note

def parse_links(content: str) -> Dict[str, List[str]]:
    """
    Extract URLs, hashtags, and mentions from the given content.

    Args:
        content (str): The text content to parse.

    Returns:
        dict: A dictionary with keys 'urls', 'hashtags', and 'mentions'.
    """
    url_pattern = r'https?://\S+'
    hashtag_pattern = r'#[\w\d_]+'
    mention_pattern = r'@[\w\d_]+'

    urls = re.findall(url_pattern, content)
    hashtags = re.findall(hashtag_pattern, content)
    mentions = re.findall(mention_pattern, content)

    return {
        'urls': urls,
        'hashtags': hashtags,
        'mentions': mentions
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
    return diffs

def export_notes(notes: List[Note], format: str = "json") -> str:
    """Export notes to the specified format (JSON or Markdown)."""
    if format == "json":
        return json.dumps([note.__dict__ for note in notes], indent=4)
    elif format == "markdown":
        return "\n\n".join(f"# {note.label or 'Note'}\n{note.content}" for note in notes)
    else:
        raise ValueError("Unsupported format. Use 'json' or 'markdown'.")