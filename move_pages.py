import os
import shutil
from pathlib import Path

EVAL_DIR_NAMES = {"Effectiveness evaluation", "Usefulness evaluation"}
TARGET_NAME = "pages"
BACKUP_ROOT = Path(r"C:\Users\23314\Desktop\backup")


def safe_name_from_relpath(rel: Path) -> str:
    """
    Turn a relative path into a filesystem-safe single folder name.
    Example: "a/b/c" -> "a__b__c"
    """
    # Use double underscore to keep it readable
    parts = [p for p in rel.parts if p not in (".", "")]
    return "__".join(parts)


def find_pages_dirs(project_root: Path) -> list[Path]:
    """
    Find all 'pages' directories that are inside any directory whose name
    is in EVAL_DIR_NAMES.
    """
    pages_dirs: list[Path] = []

    # Walk the tree once; when we hit an eval dir, search under it for pages
    for dirpath, dirnames, _filenames in os.walk(project_root):
        current = Path(dirpath)

        if current.name in EVAL_DIR_NAMES:
            # Search under this eval directory for "pages" directories
            for subdirpath, subdirnames, _ in os.walk(current):
                if TARGET_NAME in subdirnames:
                    pages_dirs.append(Path(subdirpath) / TARGET_NAME)

            # Important: don't keep walking deeper from the outer loop,
            # since we've already handled this subtree.
            dirnames.clear()

    return pages_dirs


def move_dir(src: Path, project_root: Path, backup_root: Path) -> Path:
    """
    Move src directory to backup_root with a unique name derived from its relative path.
    """
    rel = src.relative_to(project_root)
    dest_name = safe_name_from_relpath(rel)
    dest = backup_root / dest_name

    # Ensure uniqueness if needed
    if dest.exists():
        i = 1
        while True:
            candidate = backup_root / f"{dest_name}__dup{i}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    return Path(shutil.move(str(src), str(dest)))


def main() -> None:
    project_root = Path.cwd()
    backup_root = BACKUP_ROOT
    backup_root.mkdir(parents=True, exist_ok=True)

    pages_dirs = find_pages_dirs(project_root)

    if not pages_dirs:
        print("No matching 'pages' directories found under the evaluation folders.")
        return

    print(f"Project root: {project_root}")
    print(f"Backup root : {backup_root}")
    print(f"Found {len(pages_dirs)} 'pages' directories. Moving...\n")

    moved = 0
    for src in pages_dirs:
        if not src.exists():
            continue  # in case something already moved it
        try:
            dest = move_dir(src, project_root, backup_root)
            print(f"[OK]  {src}  ->  {dest}")
            moved += 1
        except Exception as e:
            print(f"[ERR] {src}  ({e})")

    print(f"\nDone. Moved {moved}/{len(pages_dirs)} directories.")


if __name__ == "__main__":
    main()
