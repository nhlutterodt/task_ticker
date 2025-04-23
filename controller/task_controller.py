"""
Task Controller Module
This module provides the `TaskController` class to manage task-related operations, including fetching notes for specific tasks.

Classes:
    TaskController:
        Manages task-related operations and interacts with the NotesManager.

Functions:
    None

Constants:
    None

Dependencies:
    - notes.manager: Provides the NotesManager class for managing notes.

Author:
    Placeholder Author
"""

from notes.manager import NotesManager

class TaskController:
    def __init__(self, app):
        self.app = app
        self.notes_manager = NotesManager()

    def fetch_notes_for_task(self, task_id: str):
        """
        Fetch notes associated with a specific task ID.

        Args:
            task_id (str): The ID of the task to fetch notes for.

        Returns:
            list[Note]: List of notes linked to the task.
        """
        return self.notes_manager.get_notes_by_task(task_id)