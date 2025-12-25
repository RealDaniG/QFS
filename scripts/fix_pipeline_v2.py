"""
Consolidated pipeline fix based on diagnosis.
"""

import os
import sys


def fix_workflow_pythonpath():
    """Add PYTHONPATH to workflow."""
    workflow_path = ".github/workflows/v20_auth_pipeline.yml"

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if PYTHONPATH already exists
    if "PYTHONPATH:" in content:
        print("✅ PYTHONPATH already in workflow")
        return False

    # Add PYTHONPATH after CI: "true"
    # Note: Indentation matters in YAML. Assuming 2 spaces indentation for env vars.
    content = content.replace(
        'CI: "true"',
        'CI: "true"\n      PYTHONPATH: "${{ github.workspace }}:${{ github.workspace }}/v13"',
    )

    with open(workflow_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Added PYTHONPATH to workflow")
    return True


def fix_requirements_installation():
    """Ensure v15/requirements.txt is installed in all jobs."""
    workflow_path = ".github/workflows/v20_auth_pipeline.yml"

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace install steps to include v15/requirements.txt
    # We look for a common pattern "pip install -r requirements.txt" and "pytest-cov"

    # The pattern in the existing file seems to be:
    # pip install -r requirements.txt || true
    # pip install pytest pytest-cov pylint httpx mypy

    # We will replace the block globally or per job?
    # Simpler: Replace the generic "Install dependencies" block content if possible.
    # Since it might vary, let's try a robust replacement.

    updated = False

    # Block 1 replacement
    search_block = """run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pytest-cov pylint httpx mypy"""

    replacement_block = """run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f v15/requirements.txt ]; then pip install -r v15/requirements.txt; fi
          pip install pytest pytest-cov pylint httpx mypy"""

    if search_block in content:
        content = content.replace(search_block, replacement_block)
        updated = True

    # Also check variations
    # The actual file content might differ slightly.
    # Let's append the v15 requirements install to any pip install -r requirements.txt line

    lines = content.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "pip install -r requirements.txt" in line and "v15" not in line:
            # Add v15 install after this line, preserving indentation
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(
                f'{indent}if [ -f "v15/requirements.txt" ]; then pip install -r v15/requirements.txt; fi'
            )
            updated = True

    if updated:
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print("✅ Updated requirements installation")
        return True

    print("⏭️  Requirements installation already updated or pattern not found")
    return False


def main():
    print("=" * 60)
    print("PIPELINE FIX v2")
    print("=" * 60)

    changes = []

    # Apply fixes
    if fix_workflow_pythonpath():
        changes.append("PYTHONPATH")

    if fix_requirements_installation():
        changes.append("Requirements installation")

    if changes:
        print("\n" + "=" * 60)
        print(f"✅ Applied {len(changes)} fix(es)")
        print("=" * 60)
        for change in changes:
            print(f"  - {change}")
        return 0
    else:
        print("No changes applied.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
