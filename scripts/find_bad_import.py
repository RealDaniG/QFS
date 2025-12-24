import os

root_dir = r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"
target = "libs.economics"

print(f"Searching for '{target}' in {root_dir}...")

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".py"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if target in content:
                        print(f"FOUND in: {filepath}")
                        with open("results.txt", "a") as rf:
                            rf.write(f"FOUND in: {filepath}\n")
                        for i, line in enumerate(content.splitlines()):
                            if target in line:
                                print(f"  Line {i + 1}: {line.strip()}")
                                with open("results.txt", "a") as rf:
                                    rf.write(f"  Line {i + 1}: {line.strip()}\n")
            except Exception as e:
                print(f"Could not read {filepath}: {e}")
