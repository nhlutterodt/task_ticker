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
