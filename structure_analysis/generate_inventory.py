import os
import json

ROOT_DIR = os.getcwd()
OUTPUT_FILE = os.path.join(ROOT_DIR, "structure_analysis", "inventory.json")

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".vscode",
    ".github",
    "node_modules",
    "dist",
    "build",
    ".coverage",
}
IGNORE_EXTS = {
    ".pyc",
    ".pyd",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".obj",
    ".o",
    ".a",
    ".lib",
    ".iso",
    ".img",
}


def get_file_metadata(filepath):
    """Get metadata for a single file."""
    try:
        stat = os.stat(filepath)
        size = stat.st_size
        _, ext = os.path.splitext(filepath)
        first_line = ""

        # Try reading first line for text files
        if ext in [
            ".py",
            ".md",
            ".txt",
            ".json",
            ".sh",
            ".bat",
            ".ps1",
            ".yml",
            ".yaml",
            ".toml",
            ".cfg",
            ".ini",
        ]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    line = f.readline()
                    first_line = line.strip()
            except Exception:
                pass

        return {"size": size, "extension": ext, "first_line": first_line}
    except Exception as e:
        return {"error": str(e)}


def classify_root_item(filename, extension, first_line):
    """Heuristic classification for root items."""
    if (
        filename.startswith("v13")
        or filename == "src"
        or filename == "ATLAS"
        or filename == "AEGIS"
    ):
        return "core_structure"
    if filename in ["tests", "tests_root"]:
        return "tests"
    if filename in ["tools_root", "scripts", "docs"]:
        return filename  # self-describing
    if extension == ".md":
        return "docs"
    if extension in [".py", ".sh", ".bat", ".ps1"]:
        # Check content or name for tooling
        if "test" in filename:
            return "misplaced_test"
        if (
            "check" in filename
            or "scan" in filename
            or "run" in filename
            or "fix" in filename
        ):
            return "tooling"
        return "script_or_tool"
    if extension in [".json", ".toml", ".cfg", ".ini", ".yaml", ".yml"]:
        return "config"
    if filename in ["requirements.txt", "setup.py"]:
        return "config"
    return "legacy_or_unknown"


def scan_repo():
    inventory = {"root_files": [], "directories": {}, "all_files": []}

    for root, dirs, files in os.walk(ROOT_DIR):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        rel_root = os.path.relpath(root, ROOT_DIR)

        if rel_root == ".":
            # Root files
            for f in files:
                if any(f.endswith(ext) for ext in IGNORE_EXTS):
                    continue

                path = os.path.join(root, f)
                meta = get_file_metadata(path)
                classification = classify_root_item(
                    f, meta.get("extension", ""), meta.get("first_line", "")
                )

                entry = {
                    "path": f,  # Relative to root
                    "metadata": meta,
                    "classification": classification,
                }
                inventory["root_files"].append(entry)
                inventory["all_files"].append(entry)
        else:
            # Subdirectory files
            dir_files = []
            for f in files:
                if any(f.endswith(ext) for ext in IGNORE_EXTS):
                    continue

                path = os.path.join(root, f)
                rel_path = os.path.join(rel_root, f).replace("\\", "/")
                meta = get_file_metadata(path)

                entry = {"path": rel_path, "metadata": meta}
                dir_files.append(entry)
                inventory["all_files"].append(entry)

            inventory["directories"][rel_root.replace("\\", "/")] = dir_files

    with open(OUTPUT_FILE, "w") as f:
        json.dump(inventory, f, indent=2)

    print(f"Inventory generated at {OUTPUT_FILE}")
    print(f"Root files: {len(inventory['root_files'])}")
    print(f"Total files: {len(inventory['all_files'])}")


if __name__ == "__main__":
    scan_repo()
