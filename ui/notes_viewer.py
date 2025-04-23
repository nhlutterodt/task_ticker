import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from ui.components.note_editor import NoteEditor

class NotesViewer(tk.Toplevel):
    def __init__(self, master, task_id, notes_manager, save_all_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.task_id = task_id
        self.notes_manager = notes_manager
        self.save_all = save_all_callback

        self.title(f"Notes for Task {task_id[:6]}")
        self.geometry("600x400")

        # List of notes
        self.listbox = tk.Listbox(self, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0), pady=10)
        self.listbox.bind('<Double-Button-1>', self.edit_selected)

        # Buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="New Note", command=self.new_note).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Edit Note", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Note", command=self.delete_selected, fg="#f44336").pack(side=tk.LEFT)

        # Content preview
        self.preview = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.preview.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0,10), pady=10)

        self.refresh_list()

    def refresh_list(self):
        """Reload notes list and clear preview."""
        self.notes = self.notes_manager.get_notes_by_task(self.task_id)
        self.listbox.delete(0, tk.END)
        for note in self.notes:
            label = note.label or note.id[:6]
            self.listbox.insert(tk.END, f"{label} ({note.updated_at.strftime('%Y-%m-%d')})")
        self.preview.config(state=tk.NORMAL)
        self.preview.delete('1.0', tk.END)
        self.preview.config(state=tk.DISABLED)

    def get_selected_note(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showinfo("No selection", "Please select a note.")
            return None
        return self.notes[idx[0]]

    def new_note(self):
        def on_save(note):
            self.notes_manager.create_note(note.content, note.tags, note.label, task_id=self.task_id)
            self.save_all()
            messagebox.showinfo("Success", "Note created.")
            self.refresh_list()
        NoteEditor(self, note=type('Temp', (), {'id':None,'content':'','tags':[],'label':None})(), save_callback=on_save)

    def edit_selected(self, event=None):
        note = self.get_selected_note()
        if not note:
            return
        def on_save(updated):
            self.notes_manager.update_note(updated.id, updated.content, updated.tags, updated.label)
            self.save_all()
            messagebox.showinfo("Success", "Note updated.")
            self.refresh_list()
        NoteEditor(self, note, on_save)

    def delete_selected(self):
        note = self.get_selected_note()
        if not note:
            return
        if messagebox.askyesno("Confirm", "Delete this note?"):
            success = self.notes_manager.delete_note(note.id)
            if success:
                self.save_all()
                messagebox.showinfo("Deleted", "Note deleted.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete note.")