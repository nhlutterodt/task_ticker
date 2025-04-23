from models.note import Note
from models.note_history import NoteHistory
from storage.note_io import load_notes, save_notes
from datetime import datetime

class NotesManager:
    def __init__(self):
        self.notes = load_notes()
        self.history = NoteHistory()

    def create_note(self, content: str, tags: list = None, label: str = None, task_id: str = None) -> Note:
        note = Note.create(content, tags, label)
        note.task_id = task_id
        self.notes[note.id] = note
        save_notes(self.notes)
        return note

    def update_note(self, note_id: str, content: str = None, tags: list = None, label: str = None):
        note = self.notes.get(note_id)
        if not note:
            raise ValueError("Note not found")
        self.history.add_version(note_id, note.content)
        if content:
            note.content = content
        if tags:
            note.tags = tags
        if label:
            note.label = label
        note.updated_at = datetime.now()
        save_notes(self.notes)
        return note

    def delete_note(self, note_id: str):
        if note_id in self.notes:
            del self.notes[note_id]
            save_notes(self.notes)

    def get_notes_by_task(self, task_id: str):
        return [note for note in self.notes.values() if note.task_id == task_id]

    def export_notes(self, format: str = "json") -> str:
        from notes.utils import export_notes
        return export_notes(self.notes, format)

    def get_all_templates(self):
        """
        Retrieve all available note templates.

        Returns:
            list[NoteTemplate]: A list of NoteTemplate instances.
        """
        from models.note_template import NoteTemplate
        # Example templates; replace with actual logic if templates are stored elsewhere
        return [
            NoteTemplate(name="Meeting Notes", content="Meeting agenda:\n- ", tags=["meeting"]),
            NoteTemplate(name="Daily Log", content="Today's tasks:\n- ", tags=["daily", "log"])
        ]