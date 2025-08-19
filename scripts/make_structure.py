import os
import fnmatch
from pathlib import Path
from typing import List

def parse_gitignore(gitignore_path: str) -> List[str]:
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path: str, gitignore_patterns: List[str]) -> bool:
    path_parts = Path(path).parts
    for pattern in gitignore_patterns:
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if any(part == pattern for part in path_parts):
                return True
        elif fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
        elif fnmatch.fnmatch(path, pattern):
            return True
        elif any(part == pattern for part in path_parts):
            return True
    return False

def generate_project_structure(root_dir: str = '.', output_file: str = 'project_structure.txt'):
    gitignore_path = os.path.join(root_dir, '.gitignore')
    gitignore_patterns = parse_gitignore(gitignore_path)

    always_ignore = ['.git', '.gitignore', '.gitattributes', '.DS_Store', 'Thumbs.db']
    gitignore_patterns.extend(always_ignore)
    gitignore_patterns.append(os.path.basename(output_file))

    structure_lines = []
    root_abs = os.path.abspath(root_dir)
    structure_lines.append(f"project structure for: {root_abs}")
    structure_lines.append("=" * 50)
    structure_lines.append("")

    def add_to_structure(current_path: str, prefix: str = "", is_last: bool = True):
        try:
            items = os.listdir(current_path)
        except PermissionError:
            return

        visible_dirs = []
        visible_files = []
        for item in items:
            item_path = os.path.join(current_path, item)
            rel = os.path.relpath(item_path, root_dir)
            if not should_ignore(rel, gitignore_patterns):
                if os.path.isdir(item_path):
                    visible_dirs.append(item)
                else:
                    visible_files.append(item)

        visible_dirs.sort()
        visible_files.sort()
        visible_items = visible_dirs + visible_files

        for i, item in enumerate(visible_items):
            item_path = os.path.join(current_path, item)
            is_last_item = (i == len(visible_items) - 1)

            if is_last:
                connector = "└── "
                next_prefix = prefix + "    "
            else:
                connector = "├── "
                next_prefix = prefix + "│   "

            structure_lines.append(f"{prefix}{connector}{item}")

            if os.path.isdir(item_path):
                add_to_structure(item_path, next_prefix, is_last_item)

    add_to_structure(root_dir)

    with open(output_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(structure_lines))

    print(f"project structure saved to: {output_file}")

if __name__ == "__main__":
    generate_project_structure()
