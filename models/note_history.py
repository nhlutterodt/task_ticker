from typing import List, Dict
from datetime import datetime

class NoteHistory:
    def __init__(self):
        self.history = []

    def add_version(self, note_id: str, content: str):
        self.history.append({"note_id": note_id, "content": content, "timestamp": datetime.now().isoformat()})

    def get_history(self, note_id: str) -> List[Dict]:
        return [entry for entry in self.history if entry["note_id"] == note_id]

    def diff_versions(self, old_content: str, new_content: str) -> Dict:
        return {
            "removed": [line for line in old_content.splitlines() if line not in new_content.splitlines()],
            "added": [line for line in new_content.splitlines() if line not in old_content.splitlines()]
        }