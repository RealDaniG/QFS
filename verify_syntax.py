import os
import py_compile
import sys


def verify_dir(start_dir):
    print(f"Verifying syntax in {start_dir}")
    errors = []
    for root, dirs, files in os.walk(start_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    print(f"SYNTAX ERROR in {path}")
                    errors.append(path)
                except Exception as e:
                    print(f"ERROR verifying {path}: {e}")
                    errors.append(path)
    if errors:
        print(f"Found {len(errors)} syntax errors.")
        sys.exit(1)
    else:
        print("All files passed syntax check.")


if __name__ == "__main__":
    verify_dir("v13/tests/unit")
