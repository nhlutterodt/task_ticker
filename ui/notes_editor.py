import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from models.note_template import NoteTemplate
import markdown
from ui.components.note_dirty_tracker import NoteDirtyTracker

class NotesEditor(tk.Toplevel):
    def __init__(self, master, note, save_callback, templates: list[NoteTemplate] = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.note = note
        self.save_callback = save_callback
        self.templates = templates or []

        self.title("🖋️ Edit Note")
        self.geometry("500x400")
        self.resizable(False, False)

        # Track original values for dirty check
        self.original_label = note.label or ""
        self.original_tags = ', '.join(note.tags) if note.tags else ""
        self.original_content = note.content or ""
        self.is_dirty = False

        # Label
        tk.Label(self, text="Label:").pack(anchor="w", padx=10, pady=(5, 0))
        self.label_entry = tk.Entry(self)
        self.label_entry.insert(0, self.original_label)
        self.label_entry.pack(fill=tk.X, padx=10)

        # Tags
        tk.Label(self, text="Tags (comma-separated):").pack(anchor="w", padx=10, pady=(5, 0))
        self.tags_entry = tk.Entry(self)
        self.tags_entry.insert(0, self.original_tags)
        self.tags_entry.pack(fill=tk.X, padx=10)

        # Template
        if self.templates:
            self.template_var = tk.StringVar(value="Select Template")
            self.template_menu = tk.OptionMenu(self, self.template_var, *[t.name for t in self.templates], command=self.apply_template)
            self.template_menu.pack(pady=5)

        # Content
        tk.Label(self, text="Content:").pack(anchor="w", padx=10, pady=(5, 0))
        self.content_text = ScrolledText(self, wrap=tk.WORD)
        self.content_text.insert(tk.END, self.original_content)
        self.content_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Save Button
        self.save_button = tk.Button(self, text="💾 Save Note", bg="#4CAF50", fg="white", command=self.save_note)
        self.save_button.pack(pady=10)
        # Disable until valid and dirty
        self.save_button.config(state=tk.DISABLED)

        # Markdown preview setup
        self.preview_text = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack_forget()

        # Dirty tracking bindings
        self.label_entry.bind('<KeyRelease>', lambda e: self._check_dirty())
        self.tags_entry.bind('<KeyRelease>', lambda e: self._check_dirty())
        self.content_text.bind('<<Modified>>', lambda e: self._on_content_modified())

        # Markdown toggle
        self.markdown_preview = tk.BooleanVar(value=False)
        self.preview_toggle = tk.Checkbutton(self, text="Toggle Markdown Preview", variable=self.markdown_preview, command=self.toggle_preview)
        self.preview_toggle.pack()

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Shortcuts
        self.bind('<Control-s>', lambda e: self.save_note())
        self.bind('<Escape>', lambda e: self.on_close())

        # Focus label
        self.label_entry.focus_set()
        self.label_entry.select_range(0, tk.END)

    def _on_content_modified(self):
        # reset modified flag
        self.content_text.edit_modified(False)
        self._check_dirty()

    def _check_dirty(self):
        label = self.label_entry.get().strip()
        tags = self.tags_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        changed = (label != self.original_label or
                   tags != self.original_tags or
                   content != self.original_content)
        valid = bool(label and content)
        self.is_dirty = changed
        if changed and valid:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def apply_template(self, template_name):
        for template in self.templates:
            if template.name == template_name:
                self.content_text.delete("1.0", tk.END)
                self.content_text.insert(tk.END, template.content)
                break
        self._check_dirty()

    def save_note(self):
        label = self.label_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not label or not content:
            messagebox.showwarning("Missing Fields", "Label and Content cannot be empty.")
            return
        # Apply to note
        self.note.label = label
        self.note.tags = [t.strip() for t in self.tags_entry.get().split(',') if t.strip()]
        self.note.content = content

        try:
            self.save_callback(self.note)
            messagebox.showinfo("Saved", "Note saved successfully.")
            self.original_label = label
            self.original_tags = ', '.join(self.note.tags)
            self.original_content = content
            self.is_dirty = False
            self.save_button.config(state=tk.DISABLED)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Failed", f"Error saving note: {e}")

    def toggle_preview(self):
        if self.markdown_preview.get():
            # Render markdown to HTML-like text in preview
            md_content = self.content_text.get("1.0", tk.END)
            html = markdown.markdown(md_content)
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, html)
            self.preview_text.config(state=tk.DISABLED)
            # Swap views
            self.content_text.pack_forget()
            self.preview_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        else:
            # Swap back to editor
            self.preview_text.pack_forget()
            self.content_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def on_close(self):
        if self.is_dirty:
            resp = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before closing?")
            if resp:  # Yes
                self.save_note()
            elif resp is False:  # No
                self.destroy()
            # Cancel: do nothing
        else:
            self.destroy()
