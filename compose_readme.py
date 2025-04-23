"""
README Module Overview Composer
This script generates a structured "📘 Module Overview" section for the project's README.md file. 
It parses per-file summary JSON files (produced by `generate_summaries.py`) to collect module titles, 
descriptions, class names, function names, and inline notes. It supports both appending and replacing 
the section in the README.

Functions:
    load_summaries():
        Loads and groups summary files from the /summaries directory by top-level folder.
    format_markdown(grouped_summaries):
        Generates a formatted markdown section from the grouped summaries.
    update_readme(new_section, mode):
        Appends or replaces the module overview section in README.md based on the selected mode.
    __main__:
        CLI interface to choose append or replace behavior via --mode argument.

Constants:
    SUMMARY_DIR:
        Path to the directory containing summary JSON files.
    README_PATH:
        Path to the target README.md file.
    SECTION_HEADER:
        Markdown header that marks the module overview section in README.md.

Dependencies:
    - os: Interacts with the file system.
    - json: Parses and writes summary metadata.
    - argparse: Parses command-line arguments.
    - collections.defaultdict: Used to group summary data.
    - builtins: Standard file handling and string formatting.

Author:
    Neils Haldane-Lutterodt
"""
import os
import json
import argparse
from collections import defaultdict

SUMMARY_DIR = "summaries"
README_PATH = "README.md"
SECTION_HEADER = "## 📘 Module Overview"

def load_summaries():
    """Load and group all summary JSON files by their module (top-level folder)."""
    grouped = defaultdict(list)
    for file in os.listdir(SUMMARY_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SUMMARY_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("title"):  # skip empty summaries
                    grouped[data.get("module", "")].append(data)
    return dict(sorted(grouped.items()))

def format_markdown(grouped_summaries):
    """Generate markdown section from summaries."""
    lines = [SECTION_HEADER, ""]
    for module, entries in grouped_summaries.items():
        lines.append(f"### `{module}/`")
        for entry in sorted(entries, key=lambda x: x["file"]):
            relpath = entry["file"]
            title = entry.get("title", "").strip()
            desc = entry.get("description", "").strip().replace("\n", " ")
            classes = ", ".join(entry.get("classes", []))
            functions = ", ".join(entry.get("functions", []))
            lines.append(f"- [`{relpath}`]({relpath}): *{title}*  ")
            if desc:
                lines.append(f"  {desc}")
            if classes:
                lines.append(f"  **Classes**: `{classes}`")
            if functions:
                lines.append(f"  **Functions**: `{functions}`")
        lines.append("")  # spacing
    return "\n".join(lines).strip()

def update_readme(new_section, mode="append"):
    """Append or replace the module overview section in README.md."""
    if mode == "append" or not os.path.exists(README_PATH):
        with open(README_PATH, "a", encoding="utf-8") as f:
            f.write("\n\n" + new_section + "\n")
        print("✅ Appended module overview to README.md")
    elif mode == "replace":
        with open(README_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_section = False
        new_lines = []
        for line in lines:
            if line.strip() == SECTION_HEADER:
                in_section = True
                new_lines.append(new_section + "\n")
            elif in_section and line.startswith("## "):
                in_section = False
                new_lines.append(line)
            elif not in_section:
                new_lines.append(line)

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("🔁 Replaced module overview in README.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose README module overview from Python summaries.")
    parser.add_argument("--mode", choices=["append", "replace"], default="append", help="Append or replace overview section")
    args = parser.parse_args()

    summaries = load_summaries()
    markdown = format_markdown(summaries)
    update_readme(markdown, mode=args.mode)
    print("📘 Module overview section generated successfully.")