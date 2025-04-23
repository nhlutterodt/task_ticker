import tkinter as tk

class NoteDirtyTracker:
    def __init__(self, text_widget: tk.Text, save_button: tk.Button):
        self.text_widget = text_widget
        self.save_button = save_button
        self.is_dirty = False
        # Disable save initially
        self.save_button.config(state=tk.DISABLED)
        # Bind modified event
        self.text_widget.bind('<<Modified>>', self._on_modified)

    def _on_modified(self, event):
        # Reset Tk's modified flag
        self.text_widget.edit_modified(False)
        if not self.is_dirty:
            self.is_dirty = True
            self.save_button.config(state=tk.NORMAL)

    def reset(self):
        self.is_dirty = False
        self.save_button.config(state=tk.DISABLED)