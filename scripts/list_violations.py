import os
import sys

# Import the main scanning logic (assuming it's importable or I'll just subprocess it)
# Actually, simply running specific check
import subprocess


def main():
    try:
        result = subprocess.run(
            ["python", "scripts/check_zero_sim.py"], capture_output=True, text=True
        )
        # Process output
        output = result.stdout
        lines = output.splitlines()
        current_file = None

        files_with_violations = {}

        for line in lines:
            if "[FAIL]" in line:
                # Extract filename
                # [FAIL] path/to/file
                parts = line.split("[FAIL]")
                if len(parts) > 1:
                    current_file = (
                        parts[1].strip().split(" ")[0]
                    )  # Handle cases where message is on same line?
                    # The output format is: [FAIL] relative/path
                    files_with_violations[current_file] = []
            elif "Line " in line and current_file:
                files_with_violations[current_file].append(line.strip())

        print(f"Found {len(files_with_violations)} files with violations:")
        for f, errs in files_with_violations.items():
            print(f"File: {f}")
            for e in errs:
                print(f"  {e}")
            print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
