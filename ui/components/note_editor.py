import tkinter as tk
from tkinter import messagebox
from models.note import Note
from notes.utils import diff_notes
from datetime import datetime
from typing import Optional, List

class NoteEditor:
    """
    A reusable widget for editing a Note instance. Presents fields for content, label, and tags,
    and invokes a save callback with the updated Note.
    """
    def __init__(self, parent, note: Note, save_callback):
        self.note = note
        self.save_callback = save_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Edit Note")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()

        # Track original values
        self.original_label = note.label or ""
        self.original_tags = ",".join(note.tags)
        self.original_content = note.content
        self.is_dirty = False

        # Label field
        tk.Label(self.window, text="Label:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.label_var = tk.StringVar(value=self.original_label)
        self.label_entry = tk.Entry(self.window, textvariable=self.label_var, width=50)
        self.label_entry.pack(fill=tk.X, padx=10)

        # Tags field
        tk.Label(self.window, text="Tags (comma-separated):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.tags_var = tk.StringVar(value=self.original_tags)
        self.tags_entry = tk.Entry(self.window, textvariable=self.tags_var, width=50)
        self.tags_entry.pack(fill=tk.X, padx=10)

        # Content text area
        tk.Label(self.window, text="Content:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.text_area = tk.Text(self.window, wrap=tk.WORD)
        self.text_area.insert(tk.END, self.original_content)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0,10))

        # Buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        self.save_button = tk.Button(btn_frame, text="Save", command=self.on_save, bg="#4CAF50", fg="white")
        self.save_button.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # Disable save until changes and fields valid
        self.save_button.config(state=tk.DISABLED)
        # Bind events for dirty tracking and validation
        self.label_var.trace_add('write', lambda *args: self._check_dirty())
        self.tags_var.trace_add('write', lambda *args: self._check_dirty())
        self.text_area.bind('<KeyRelease>', lambda e: self._check_dirty())

        # Handle close with unsaved changes
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        # Keyboard shortcuts
        self.window.bind('<Control-s>', lambda e: self.on_save())
        self.window.bind('<Escape>', lambda e: self.on_close())

        # Focus label entry
        self.label_entry.focus_set()
        self.label_entry.select_range(0, tk.END)

    def _check_dirty(self):
        label = self.label_var.get().strip()
        content = self.text_area.get("1.0", tk.END).strip()
        current_tags = self.tags_var.get().strip()
        changed = (label != self.original_label or
                   content != self.original_content or
                   current_tags != self.original_tags)
        valid = bool(label and content)
        self.is_dirty = changed
        if changed and valid:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def on_close(self):
        if self.is_dirty:
            resp = messagebox.askyesnocancel("Unsaved Changes", "Save changes before closing?")
            if resp:  # Yes
                self.on_save()
            elif resp is False:  # No
                self.window.destroy()
            # Cancel does nothing
        else:
            self.window.destroy()

    def on_save(self):
        # Validate fields
        label = self.label_var.get().strip()
        content = self.text_area.get("1.0", tk.END).strip()
        if not label or not content:
            messagebox.showwarning("Missing Fields", "Label and Content cannot be empty.")
            return

        # Gather tags
        tags = [t.strip() for t in self.tags_var.get().split(",") if t.strip()]

        # Apply updates to note
        self.note.label = label
        self.note.tags = tags
        self.note.content = content

        try:
            # Persist via callback
            self.save_callback(self.note)
            messagebox.showinfo("Saved", "Note saved successfully.")
            self.original_label = label
            self.original_tags = ",".join(tags)
            self.original_content = content
            self.is_dirty = False
            self.save_button.config(state=tk.DISABLED)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save note: {e}")

def edit_note(note: Note, new_content: str, new_label: Optional[str] = None, new_tags: Optional[List[str]] = None, preview_diff: bool = False) -> Note:
    """
    Edit a note's content, label, and tags with an optional diff preview.

    Args:
        note (Note): The note to edit.
        new_content (str): The new content for the note.
        new_label (Optional[str]): The new label for the note.
        new_tags (Optional[List[str]]): The new tags for the note.
        preview_diff (bool): Whether to preview the diff before saving.

    Returns:
        Note: The updated note.
    """
    updated_note = Note(
        id=note.id,
        content=new_content,
        created_at=note.created_at,
        updated_at=datetime.now(),
        tags=new_tags or note.tags,
        label=new_label or note.label,
        history=note.history + [note.content]
    )

    if preview_diff:
        diffs = diff_notes(note, updated_note)
        print("Preview of changes:")
        for field, change in diffs.items():
            print(f"{field}: {change[0]} -> {change[1]}")

    return updated_note