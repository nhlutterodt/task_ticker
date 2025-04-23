import tkinter as tk
from tkinter import messagebox
from models.note import Note

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

        # Label field
        tk.Label(self.window, text="Label:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.label_var = tk.StringVar(value=self.note.label or "")
        tk.Entry(self.window, textvariable=self.label_var, width=50).pack(fill=tk.X, padx=10)

        # Tags field
        tk.Label(self.window, text="Tags (comma-separated):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        tags_str = ",".join(self.note.tags)
        self.tags_var = tk.StringVar(value=tags_str)
        tk.Entry(self.window, textvariable=self.tags_var, width=50).pack(fill=tk.X, padx=10)

        # Content text area
        tk.Label(self.window, text="Content:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.text_area = tk.Text(self.window, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0,10))
        self.text_area.insert(tk.END, self.note.content)

        # Buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Save", command=self.on_save, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def on_save(self):
        # Gather updated fields
        content = self.text_area.get("1.0", tk.END).strip()
        label = self.label_var.get().strip() or None
        tags = [t.strip() for t in self.tags_var.get().split(",") if t.strip()]

        if not content:
            messagebox.showwarning("Empty Content", "Note content cannot be empty.")
            return

        # Apply updates to note
        updated_note = Note(
            id=self.note.id,
            content=content,
            created_at=self.note.created_at,
            updated_at=self.note.updated_at,
            tags=tags,
            label=label,
            history=list(self.note.history)
        )
        # Invoke callback
        try:
            self.save_callback(updated_note)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save note: {e}")
            return

        self.window.destroy()