"""
Undo Manager Module
This module provides the `UndoManager` class, which implements a stack-based mechanism to handle undo and redo functionality. It allows registering actions with corresponding undo and redo operations and provides methods to perform undo and redo actions while maintaining a configurable stack limit.

Classes:
    UndoManager:
        Manages undo and redo stacks with a configurable limit.

Functions:
    __init__(limit=20):
        Initializes the UndoManager with a specified stack limit.
    register(undo_action, redo_action):
        Registers an undo and redo action pair, maintaining the stack limit.
    can_undo() -> bool:
        Checks if there are actions available to undo.
    can_redo() -> bool:
        Checks if there are actions available to redo.
    undo() -> bool:
        Performs the last registered undo action and moves it to the redo stack.
    redo() -> bool:
        Reapplies the last undone action and moves it back to the undo stack.

Constants:
    None

Dependencies:
    None

Author:
    Placeholder Author
"""
class UndoManager:

    def __init__(self, limit=20):
        self.undo_stack = []
        self.redo_stack = []
        self.limit = limit

    def register(self, undo_action, redo_action):
        # Push a new action and clear redo stack
        self.undo_stack.append((undo_action, redo_action))
        if len(self.undo_stack) > self.limit:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def can_undo(self):
        return bool(self.undo_stack)

    def can_redo(self):
        return bool(self.redo_stack)

    def undo(self):
        if not self.can_undo():
            return False
        undo_action, redo_action = self.undo_stack.pop()
        undo_action()
        self.redo_stack.append((undo_action, redo_action))
        return True

    def redo(self):
        if not self.can_redo():
            return False
        undo_action, redo_action = self.redo_stack.pop()
        redo_action()
        self.undo_stack.append((undo_action, redo_action))
        return True
