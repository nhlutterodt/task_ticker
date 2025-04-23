import json
from models.task import Task
from models.note import Note
from typing import List, Dict

def export_notes_grouped_by_task(tasks: List[Task], notes: Dict[str, Note], format: str = "json") -> str:
    """
    Export notes grouped by task metadata.

    Args:
        tasks (List[Task]): List of tasks.
        notes (Dict[str, Note]): Dictionary of notes keyed by note ID.
        format (str): Export format, either 'json' or 'markdown'.

    Returns:
        str: Exported notes in the specified format.
    """
    grouped_notes = {}
    for task in tasks:
        task_notes = [note.to_dict() for note in notes.values() if note.task_id == task.id]
        grouped_notes[task.id] = {
            "task": task.to_dict(),
            "notes": task_notes
        }

    if format == "json":
        return json.dumps(grouped_notes, indent=4)
    elif format == "markdown":
        markdown_output = []
        for task_id, data in grouped_notes.items():
            task_info = data["task"]
            markdown_output.append(f"## Task: {task_info['task']}\nGroup: {task_info['group']}\nDue: {task_info['due_date']}")
            for note in data["notes"]:
                markdown_output.append(f"### Note: {note['label'] or 'Untitled'}\n{note['content']}")
        return "\n\n".join(markdown_output)
    else:
        raise ValueError("Unsupported format. Use 'json' or 'markdown'.")