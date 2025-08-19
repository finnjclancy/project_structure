import os
import fnmatch
from pathlib import Path
from typing import List

def parse_gitignore(gitignore_path: str) -> List[str]:
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def should_ignore(rel_path: str, gitignore_patterns: List[str]) -> bool:
    parts = Path(rel_path).parts
    for pattern in gitignore_patterns:
        p = pattern
        if p.endswith("/"):
            p = p[:-1]
            if any(part == p for part in parts):
                return True
        elif fnmatch.fnmatch(os.path.basename(rel_path), p):
            return True
        elif fnmatch.fnmatch(rel_path, p):
            return True
        elif any(part == p for part in parts):
            return True
    return False

def generate_project_structure(root_dir: str = ".", output_file: str = "project_structure.txt"):
    gitignore_path = os.path.join(root_dir, ".gitignore")
    gitignore_patterns = parse_gitignore(gitignore_path)

    always_ignore = [".git", ".gitignore", ".gitattributes", ".DS_Store", "Thumbs.db"]
    gitignore_patterns.extend(always_ignore)
    gitignore_patterns.append(os.path.basename(output_file))

    lines: List[str] = []
    root_abs = os.path.abspath(root_dir)
    lines.append(f"project structure for: {root_abs}")
    lines.append("=" * 50)
    lines.append("")

    def add_to_structure(current_path: str, prefix: str = "", is_last: bool = True):
        try:
            items = os.listdir(current_path)
        except PermissionError:
            return

        dirs: List[str] = []
        files: List[str] = []

        for item in items:
            item_path = os.path.join(current_path, item)
            rel = os.path.relpath(item_path, root_dir)
            if should_ignore(rel, gitignore_patterns):
                continue
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)

        dirs.sort()
        files.sort()
        visible = dirs + files

        for i, item in enumerate(visible):
            item_path = os.path.join(current_path, item)
            last_item = (i == len(visible) - 1)

            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            label = item + ("/" if os.path.isdir(item_path) else "")
            lines.append(f"{prefix}{connector}{label}")

            if os.path.isdir(item_path):
                add_to_structure(item_path, next_prefix, last_item)

    add_to_structure(root_dir)

    with open(output_file, "w", encoding="utf8") as f:
        f.write("\n".join(lines))

    print(f"project structure saved to: {output_file}")

if __name__ == "__main__":
    generate_project_structure()