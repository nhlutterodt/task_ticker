import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from models.note_template import NoteTemplate

class NotesEditor(tk.Toplevel):
    def __init__(self, master, note, save_callback, templates: list[NoteTemplate] = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.note = note
        self.save_callback = save_callback
        self.templates = templates or []

        self.title("🖋️ Edit Note")
        self.geometry("500x400")
        self.resizable(False, False)

        # Label
        tk.Label(self, text="Label:").pack(anchor="w", padx=10, pady=(5, 0))
        self.label_entry = tk.Entry(self)
        self.label_entry.insert(0, note.label or "")
        self.label_entry.pack(fill=tk.X, padx=10)

        # Tags
        tk.Label(self, text="Tags (comma-separated):").pack(anchor="w", padx=10, pady=(5, 0))
        self.tags_entry = tk.Entry(self)
        self.tags_entry.insert(0, ', '.join(note.tags) if note.tags else "")
        self.tags_entry.pack(fill=tk.X, padx=10)

        # Template
        if self.templates:
            self.template_var = tk.StringVar(value="Select Template")
            self.template_menu = tk.OptionMenu(self, self.template_var, *[t.name for t in self.templates], command=self.apply_template)
            self.template_menu.pack(pady=5)

        # Content
        tk.Label(self, text="Content:").pack(anchor="w", padx=10, pady=(5, 0))
        self.content_text = ScrolledText(self, wrap=tk.WORD)
        self.content_text.insert(tk.END, note.content)
        self.content_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Save Button
        self.save_button = tk.Button(self, text="💾 Save Note", bg="#4CAF50", fg="white", command=self.save_note)
        self.save_button.pack(pady=10)

        # Markdown toggle
        self.markdown_preview = tk.BooleanVar(value=False)
        self.preview_toggle = tk.Checkbutton(self, text="Toggle Markdown Preview", variable=self.markdown_preview, command=self.toggle_preview)
        self.preview_toggle.pack()

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_template(self, template_name):
        for template in self.templates:
            if template.name == template_name:
                self.content_text.delete("1.0", tk.END)
                self.content_text.insert(tk.END, template.content)
                break

    def save_note(self):
        self.note.label = self.label_entry.get().strip()
        self.note.tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        self.note.content = self.content_text.get("1.0", tk.END).strip()

        if not self.note.content:
            messagebox.showwarning("Empty Note", "Cannot save an empty note.")
            return

        try:
            self.save_callback(self.note)
            messagebox.showinfo("Saved", "Note saved successfully.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Failed", f"Error saving note: {e}")

    def toggle_preview(self):
        if self.markdown_preview.get():
            messagebox.showinfo("Markdown", "Live Markdown preview not yet implemented.")
        else:
            messagebox.showinfo("Markdown", "Preview disabled.")

    def on_close(self):
        if self.content_text.edit_modified():
            if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Close without saving?"):
                self.destroy()
        else:
            self.destroy()
