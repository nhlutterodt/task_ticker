# Task Ticker 📝

Task Ticker is a robust task management application designed to help users organize, track, and manage their tasks efficiently. It features a graphical user interface (GUI) built with Tkinter and provides advanced functionalities such as strict mode, recurrence, dependency validation, undo/redo operations, and batch task management.

## Features

### Core Functionality

- **Task Management**: Add, edit, delete, and toggle tasks with ease.
- **Notes Integration**: Attach detailed notes to tasks for additional context.
- **Filtering and Sorting**: Filter tasks by status, group, or tags, and sort them by due date, priority, or sequence.
- **Dependency Validation**: Ensure tasks respect dependencies and validate task creation rules.
- **Recurrence Support**: Define recurring tasks with customizable rules.

### Advanced Features

- **Strict Mode**: Enforce stricter rules for task creation and management.
- **Undo/Redo**: Seamlessly undo or redo actions with a stack-based mechanism.
- **Batch Operations**: Perform batch updates, such as marking tasks as done, editing tags, or moving tasks to a group.
- **Backup and Recovery**: Automatically back up task data and recover from backups if needed.

## Application Structure

### 1. **Main Application**

- **File**: `main.py`
- Entry point for the application. Initializes the GUI and logs application events.

### 2. **Models**

- **File**: `models/note.py`
  - Defines the `Note` dataclass for managing note content, tags, and history.
- **File**: `models/task.py`
  - Defines the `Task` and `TaskMeta` classes for managing tasks, including serialization, dependency checks, and recurrence.

### 3. **Storage**

- **File**: `storage/file_io.py`
  - Handles saving and loading tasks and notes to/from JSON files, ensuring data integrity with backups.
- **File**: `storage/settings.py`
  - Manages application settings with validation against a schema.

### 4. **Utilities**

- **File**: `notes/utils.py`
  - Provides utility functions for parsing links, comparing notes, and exporting notes in JSON or Markdown formats.

### 5. **User Interface**

- **File**: `ui/app.py`
  - Implements the main GUI for the application, including task list rendering, filters, and user interactions.
- **File**: `ui/undo.py`
  - Provides the `UndoManager` class for managing undo and redo operations.
- **File**: `ui/controller.py`
  - Handles batch operations and task-related interactions, such as editing tags or moving tasks to groups.

## 📘 Module Overview

### `archive_v9.py`
- [`archive_v9.py`](archive_v9.py): *Task Ticker v9 - Task Dependencies and Sequencing*  
  **Classes**: `TaskTickerApp`

### `export.py`
- [`export.py`](export.py): *Export Module*  
  This module provides functionality to export notes grouped by task metadata in various formats such as JSON and Markdown.  
  **Functions**: `export_notes_grouped_by_task`

### `main.py`
- [`main.py`](main.py): *Task Ticker Main Module*  
  This module serves as the entry point for the Task Ticker application. It initializes the application, sets up logging, and ensures the logs directory exists.

### `models/`
- [`models/note.py`](models/note.py): *Note Model Module*  
  Defines the `Note` dataclass, representing a note entity with attributes such as content, timestamps, tags, and history.  
  **Classes**: `Note`

- [`models/note_history.py`](models/note_history.py): *Note History Module*  
  Manages the version history of notes, including adding versions, retrieving history, and computing differences.  
  **Classes**: `NoteHistory`

- [`models/note_template.py`](models/note_template.py): *Note Template Module*  
  Represents a template for notes with attributes for name, content, and tags.  
  **Classes**: `NoteTemplate`

- [`models/shared_tags.py`](models/shared_tags.py): *Shared Tags Module*  
  Manages a global set of tags shared across the application.  
  **Classes**: `SharedTags`

- [`models/task.py`](models/task.py): *Task Model Module*  
  Defines the `Task` and `TaskMeta` classes for managing tasks, including serialization, dependency checks, and recurrence handling.  
  **Classes**: `TaskMeta`, `Task`

### `storage/`
- [`storage/file_io.py`](storage/file_io.py): *File I/O Module for Tasks and Notes Management*  
  Provides functionality for managing tasks and notes, including saving and loading data to/from JSON files, ensuring the data directory structure, creating backups, and recovering from file corruption.  
  **Functions**: `ensure_data_dir`, `save_tasks`, `load_notes`, `load_tasks`, `backup_exists`, `recover_from_backup`

## Debugging & Introspection Framework

Task Ticker includes a modular debug framework for robust logging, diagnostics, and event tracing across all modules.

### Features
- **Centralized Logging**: Timestamped logs with configurable levels (DEBUG, INFO, etc.), output as pretty text, JSON, or both.
- **Non-Invasive Decorators**: Use `@debug_trace` to automatically log function calls, arguments, return values, and exceptions.
- **Ad Hoc Tracing**: Use `trace()` for contextual, on-demand debug messages anywhere in the codebase.
- **Configurable Output**: Logs can be sent to the console, to `logs/task_ticker.log`, or both. Control via environment variables or `debug/config.py`.
- **Minimal Overhead**: When disabled, the framework adds negligible runtime cost.

### Usage Examples

```python
from debug import debug_trace, trace

@debug_trace
def validate_task(task):
    # ... task validation logic ...
    return True

trace("Main window loaded", context="ui")
```

#### Environment Variables
- `DEBUG=1` — Enable debug logging
- `DEBUG_LEVEL=DEBUG` — Set log level
- `DEBUG_FORMAT=both` — Output format: `pretty`, `json`, or `both`
- `DEBUG_LOGFILE=logs/task_ticker.log` — Log file path (default: logs/task_ticker.log)

#### Example: Enabling Debug Logging
```bash
set DEBUG=1
set DEBUG_FORMAT=both
python main.py
```

### Integration Points
- Decorate functions in `logic/`, `models/`, or `storage/` for automatic tracing.
- Use `trace()` in `ui/app.py` or controllers to log UI and user events.
- All logs are human-readable and machine-parseable for future analysis or visualization.

---

## How It Works

1. **Task Management**: Users can create tasks with metadata such as due dates, priorities, tags, and dependencies. Tasks can also have associated notes for additional details.
2. **Filtering and Sorting**: Tasks can be filtered by status, group, or tags and sorted by various criteria.
3. **Batch Operations**: Perform operations on multiple tasks at once, such as marking them as done or moving them to a new group.
4. **Undo/Redo**: Every action is tracked, allowing users to undo or redo changes as needed.
5. **Data Persistence**: Tasks and notes are saved to JSON files, with automatic backups to prevent data loss.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required libraries: `tkinter`, `tkcalendar`

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/task-ticker.git
   cd task-ticker
   ```

2. Install dependencies:

   ```bash
   pip install tkcalendar
   ```

### Running the Application

Run the main script to start the application:

```bash
python main.py
```

## File Overview

| File/Directory         | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `main.py`              | Entry point for the application.                                           |
| `models/`              | Contains data models for tasks and notes.                                  |
| `storage/`             | Handles file I/O and settings management.                                  |
| `notes/utils.py`       | Utility functions for notes, including parsing and exporting.              |
| `ui/`                  | Implements the GUI, undo/redo functionality, and task controllers.         |

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
