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

def matches_any_pattern(rel_path: str, patterns: List[str]) -> bool:
    parts = Path(rel_path).parts
    base = os.path.basename(rel_path)

    for pattern in patterns:
        p = pattern

        # directory style pattern like foo/
        if p.endswith("/"):
            p = p[:-1]
            if any(part == p for part in parts):
                return True
            if rel_path.startswith(p + os.sep):
                return True

        # file name pattern
        if fnmatch.fnmatch(base, p):
            return True

        # path pattern
        if fnmatch.fnmatch(rel_path, p):
            return True

        # exact segment match
        if any(part == p for part in parts):
            return True

    return False

def generate_project_structure(root_dir: str = ".", output_file: str = "project_structure.txt"):
    gitignore_path = os.path.join(root_dir, ".gitignore")
    git_patterns = parse_gitignore(gitignore_path)

    lines: List[str] = []
    root_abs = os.path.abspath(root_dir)
    lines.append(f"project structure for: {root_abs}")
    lines.append("=" * 50)
    lines.append("")

    def should_skip(rel_path: str) -> bool:
        # always include the .gitignore file itself
        if rel_path.replace("\\", "/") == ".gitignore":
            return False
        # skip the output file
        if rel_path.replace("\\", "/") == output_file:
            return True
        # skip the .git folder
        if rel_path.startswith(".git/") or rel_path == ".git":
            return True
        # skip things matched by .gitignore patterns
        return matches_any_pattern(rel_path, git_patterns)

    def add_to_structure(current_path: str, prefix: str = ""):
        try:
            items = os.listdir(current_path)
        except PermissionError:
            return

        dirs: List[str] = []
        files: List[str] = []

        for item in items:
            item_path = os.path.join(current_path, item)
            rel = os.path.relpath(item_path, root_dir).replace("\\", "/")
            if should_skip(rel):
                continue
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)

        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        visible = dirs + files

        for idx, item in enumerate(visible):
            item_path = os.path.join(current_path, item)
            last_item = (idx == len(visible) - 1)

            connector = "└── " if last_item else "├── "
            next_prefix = prefix + ("    " if last_item else "│   ")

            label = item + ("/" if os.path.isdir(item_path) else "")
            lines.append(f"{prefix}{connector}{label}")

            if os.path.isdir(item_path):
                add_to_structure(item_path, next_prefix)

    add_to_structure(root_dir)

    with open(output_file, "w", encoding="utf8") as f:
        f.write("\n".join(lines))

    print(f"project structure saved to: {output_file}")

if __name__ == "__main__":
    generate_project_structure()
