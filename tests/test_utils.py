import unittest
from datetime import datetime
from notes.utils import parse_links, diff_notes, export_notes
from models.note import Note

class TestUtils(unittest.TestCase):

    def test_parse_links(self):
        content = "Check this out: https://example.com #hashtag @task123"
        result = parse_links(content)
        self.assertEqual(result["urls"], ["https://example.com"])
        self.assertEqual(result["hashtags"], ["#hashtag"])
        self.assertEqual(result["task_refs"], ["@task123"])

    def test_diff_notes(self):
        old_note = Note(id="1", content="Old content", created_at=datetime.now(), updated_at=datetime.now())
        new_note = Note(id="1", content="New content", created_at=datetime.now(), updated_at=datetime.now(), tags=["tag1"])
        diffs = diff_notes(old_note, new_note)
        self.assertIn("content", diffs)
        self.assertIn("tags", diffs)

    def test_export_notes_json(self):
        notes = [
            Note(id="1", content="Note 1", created_at=datetime.now(), updated_at=datetime.now()),
            Note(id="2", content="Note 2", created_at=datetime.now(), updated_at=datetime.now())
        ]
        result = export_notes(notes, format="json")
        self.assertTrue(result.startswith("[") and result.endswith("]"))

    def test_export_notes_markdown(self):
        notes = [
            Note(id="1", content="Note 1", created_at=datetime.now(), updated_at=datetime.now(), label="Label 1"),
            Note(id="2", content="Note 2", created_at=datetime.now(), updated_at=datetime.now())
        ]
        result = export_notes(notes, format="markdown")
        self.assertIn("# Label 1", result)
        self.assertIn("Note 2", result)

if __name__ == "__main__":
    unittest.main()