"""
Shared Tags Module
This module defines the `SharedTags` class, which manages a global set of tags shared across the application. It provides methods for adding new tags, removing existing tags, and retrieving all tags in sorted order.

Classes:
    SharedTags:
        Manages a global set of tags with methods for adding, removing, and retrieving tags.

Functions:
    add_tags(tags: list[str]):
        Adds a list of tags to the global set.
    remove_tag(tag: str):
        Removes a specific tag from the global set.
    get_all_tags() -> list[str]:
        Retrieves all tags in sorted order.

Constants:
    None

Dependencies:
    - typing: For type annotations.

Author:
    Placeholder Author
"""

from typing import List

class SharedTags:
    _tags = set()

    @classmethod
    def add_tags(cls, tags: list[str]):
        cls._tags.update(tags)

    @classmethod
    def remove_tag(cls, tag: str):
        cls._tags.discard(tag)

    @classmethod
    def get_all_tags(cls) -> list[str]:
        return sorted(cls._tags)