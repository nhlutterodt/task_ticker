"""
Note Model Tests Module
This module contains unit tests for the `Note` model, ensuring proper initialization and handling of optional fields.

Classes:
    TestNoteModel:
        Contains test cases for the `Note` model, including initialization and optional field handling.

Functions:
    None

Constants:
    None

Dependencies:
    - unittest: For creating and running test cases.
    - datetime: For handling date and time in test data.
    - models.note: Provides the Note model.

Author:
    Placeholder Author
"""

import unittest
from datetime import datetime
from models.note import Note

class TestNoteModel(unittest.TestCase):

    def test_note_initialization(self):
        note = Note(id="1", content="Test content", created_at=datetime.now(), updated_at=datetime.now())
        self.assertEqual(note.tags, [])
        self.assertIsNone(note.label)
        self.assertEqual(note.history, [])

    def test_note_with_optional_fields(self):
        note = Note(
            id="2",
            content="Another test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["tag1", "tag2"],
            label="Important",
            history=["Initial content"]
        )
        self.assertEqual(note.tags, ["tag1", "tag2"])
        self.assertEqual(note.label, "Important")
        self.assertEqual(note.history, ["Initial content"])

if __name__ == "__main__":
    unittest.main()