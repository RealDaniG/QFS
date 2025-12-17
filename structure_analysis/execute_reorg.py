import json
import os
import shutil

ROOT_DIR = os.getcwd()
PLAN_FILE = os.path.join(ROOT_DIR, "structure_analysis", "reorg_plan.json")


def execute():
    try:
        with open(PLAN_FILE, "r") as f:
            plan = json.load(f)
    except FileNotFoundError:
        print("Plan file not found.")
        return

    moves = plan.get("moves", [])
    deletions = plan.get("deletions", [])
    dirs_to_clean = plan.get("directories_to_clean", [])

    print(f"Executing {len(moves)} moves and {len(deletions)} deletions...")

    # Moves
    for move in moves:
        src = os.path.join(ROOT_DIR, move["from"])
        dst = os.path.join(ROOT_DIR, move["to"])

        if not os.path.exists(src):
            print(f"SKIP: Source not found {src}")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        try:
            shutil.move(src, dst)
            print(f"MOVED: {move['from']} -> {move['to']}")
        except Exception as e:
            print(f"ERROR moving {move['from']}: {e}")

    # Deletions
    for delete in deletions:
        path = os.path.join(ROOT_DIR, delete["path"])
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"DELETED: {delete['path']}")
            except Exception as e:
                print(f"ERROR deleting {path}: {e}")

    # Clean empty dirs
    for d in dirs_to_clean:
        path = os.path.join(ROOT_DIR, d)
        if os.path.exists(path):
            # Only remove if empty or we moved everything
            try:
                # check if empty
                if not os.listdir(path):
                    os.rmdir(path)
                    print(f"REMOVED DIR: {d}")
                else:
                    print(f"DIR NOT EMPTY: {d} - Contents: {os.listdir(path)}")
            except Exception as e:
                print(f"ERROR removing dir {d}: {e}")


if __name__ == "__main__":
    execute()
