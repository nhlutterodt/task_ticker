import unittest
from datetime import datetime
from models.task import Task
from models.note import Note
from storage.file_io import save_tasks, load_tasks

class TestIntegration(unittest.TestCase):

    def test_task_note_resolution(self):
        note = Note(id="note1", content="This is a note", created_at=datetime.now(), updated_at=datetime.now())
        task = Task(id="task1", title="Task with note", note_id="note1")

        # Mock saving and loading
        save_tasks([task])
        loaded_tasks = load_tasks()

        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0].note_id, "note1")
        self.assertEqual(loaded_tasks[0].notes, "This is a note")

if __name__ == "__main__":
    unittest.main()