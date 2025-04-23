import os
import ast
import json
import tokenize
from io import StringIO
import argparse

# Ensure the summaries directory exists
SUMMARIES_DIR = "summaries"
os.makedirs(SUMMARIES_DIR, exist_ok=True)

# Updated extract_metadata to pass content to _extract_inline_comments
def extract_metadata(file_path):
    """Extract metadata from a Python file."""
    content = _read_file(file_path)
    tree = ast.parse(content, filename=file_path)

    title, description = _extract_docstring(tree)
    classes = _extract_classes(tree)
    functions = _extract_functions(tree)
    notes = _extract_inline_comments(content)  # Pass raw content here

    return {
        "file": os.path.relpath(file_path),
        "title": title,
        "description": description,
        "classes": classes,
        "functions": functions,
        "notes": notes,
    }

def _read_file(file_path):
    """Read the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def _extract_docstring(tree):
    """Extract the module-level docstring."""
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        lines = module_docstring.split("\n")
        title = lines[0].strip() if lines else ""
        description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        return title, description
    return "", ""

def _extract_classes(tree):
    """Extract top-level classes."""
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]

def _extract_functions(tree):
    """Extract top-level functions."""
    return [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]

# Updated _extract_inline_comments to use tokenize for extracting # comments
def _extract_inline_comments(source_code):
    """Extract actual # comments from source."""
    comments = []
    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for token_type, token_string, *_ in tokens:
        if token_type == tokenize.COMMENT:
            comments.append(token_string.lstrip("# ").strip())
    return comments

# Updated process_files to support CLI filtering and exclude unnecessary folders
def process_files(only=None):
    """Process all .py files in the project."""
    for root, _, files in os.walk("."):
        # Exclude unnecessary folders
        if any(part in {"venv", ".venv", "__pycache__", ".git"} for part in root.split(os.sep)):
            continue

        files.sort()  # Deterministic order helps with debugging and consistent summaries

        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)

                # Skip files not in the specified folder if --only is used
                if only and only not in file_path:
                    continue

                metadata = extract_metadata(file_path)

                # Encode relative path into the filename to avoid clashes
                relpath = os.path.relpath(file_path).replace(os.sep, "__")
                summary_file = os.path.join(SUMMARIES_DIR, f"{relpath}.json")

                # Write metadata to a JSON file
                with open(summary_file, "w", encoding="utf-8") as json_file:
                    json.dump(metadata, json_file, indent=4)

                # Add verbose logging
                print(f"✔ Processed {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate summaries for Python files.")
    parser.add_argument("--only", type=str, help="Process only files in the specified folder.")
    args = parser.parse_args()

    process_files(only=args.only)