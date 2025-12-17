import json
import os
import re

ROOT_DIR = os.getcwd()
INVENTORY_FILE = os.path.join(ROOT_DIR, "structure_analysis", "inventory.json")
OUTPUT_FILE = os.path.join(ROOT_DIR, "structure_analysis", "legacy_candidates.json")


def is_candidate(file_entry):
    path = file_entry["path"]
    size = file_entry["metadata"]["size"]
    first_line = file_entry["metadata"]["first_line"]

    filename = os.path.basename(path)

    # 1. Size/Content heuristic
    if size < 20:
        return "empty_or_tiny"
    if "pass" in first_line and size < 100:
        return "possible_stub"
    if first_line.strip() == "":
        return "empty_start"

    # 2. Name heuristic
    if any(
        x in filename.lower() for x in ["_old", "_backup", "tmp_", "temp_", "copy_of"]
    ):
        return "backup_name"
    if (
        filename.startswith("check_")
        or filename.startswith("scan_")
        or filename.startswith("fix_")
    ):
        # Root scripts often legacy one-offs
        if "/" not in path and "\\" not in path:  # Root only
            return "root_script_candidate"

    return None


def check_usage(target_path, all_files):
    """Check if target_path is referenced in other files."""
    target_name = os.path.basename(target_path)
    target_mod = os.path.splitext(target_name)[0]

    refs = 0
    ref_files = []

    # Simple grep - can be slow for 8000 files, but reasonable for python script
    # We'll optimize by skipping binary/large files

    for entry in all_files:
        path = entry["path"]
        if path == target_path:
            continue

        # Don't check large logs/json
        if entry["metadata"]["extension"] not in [".py", ".md", ".sh", ".bat", ".txt"]:
            continue
        if entry["metadata"]["size"] > 1000000:
            continue

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if target_name in content or (
                    target_mod in content and len(target_mod) > 3
                ):
                    refs += 1
                    ref_files.append(path)
                    if refs > 5:
                        break  # meaningful enough
        except:
            pass

    return refs, ref_files


def analyze():
    with open(INVENTORY_FILE, "r") as f:
        inventory = json.load(f)

    all_files = inventory["all_files"]
    candidates = []

    print(f"Analyzing {len(all_files)} files...")

    for entry in all_files:
        reason = is_candidate(entry)
        if reason:
            refs, ref_files = check_usage(entry["path"], all_files)

            status = "uncertain"
            if refs == 0:
                status = "unused_safe_to_delete"
            elif reason == "root_script_candidate" and refs < 2:
                # Scripts often have 0 refs because they are entry points.
                # But if they are 'fix_bignum.py', likely obsolete.
                status = (
                    "unused_safe_to_delete"
                    if "fix_" in entry["path"]
                    else "used_script"
                )
            else:
                status = "used_stub" if "stub" in reason else "used"

            candidates.append(
                {
                    "path": entry["path"],
                    "reason": reason,
                    "references": refs,
                    "ref_samples": ref_files[:3],
                    "status": status,
                }
            )

    with open(OUTPUT_FILE, "w") as f:
        json.dump(candidates, f, indent=2)

    print(f"Found {len(candidates)} candidates.")
    for c in candidates:
        if c["status"] == "unused_safe_to_delete":
            print(f"DELETE CANDIDATE: {c['path']} ({c['reason']})")


if __name__ == "__main__":
    analyze()
