"""
discovery_scan.py - QFS Module Discovery Scanner for AEGIS

Scans QFS repository directories and generates module_map.json for AEGIS to understand
the codebase structure. This is Track 0.1 of the autonomous AEGIS implementation.

Contract Compliance: Deterministic output (sorted JSON), read-only operations.
"""

import os
import json
from pathlib import Path
from typing import Dict, List

# Base path (adjust if running from different location)
BASE_PATH = Path(__file__).parent.parent / "v13"

# Module categories and their scan paths
MODULE_MAP = {
    "economic_modules": [],
    "governance_modules": [],
    "atlas_api_modules": [],
    "atlas_frontend_modules": [],
    "policy_modules": [],
    "core_modules": [],
    "tools_root_modules": [],
}

SCAN_PATHS = {
    "economic_modules": BASE_PATH / "libs" / "economics",
    "governance_modules": BASE_PATH / "libs" / "governance",
    "atlas_api_modules": BASE_PATH / "atlas_api",
    "atlas_frontend_modules": BASE_PATH / "ATLAS" / "src",
    "policy_modules": BASE_PATH / "policy",
    "core_modules": BASE_PATH / "core",
    "tools_root_modules": Path(__file__).parent.parent / "tools_root",
}


def scan_directory(path: Path) -> List[str]:
    """
    Scan directory for Python and TypeScript files.

    Args:
        path: Directory to scan

    Returns:
        Sorted list of relative file paths
    """
    if not path.exists():
        print(f"Warning: Path does not exist: {path}")
        return []

    files = []
    for root, dirs, filenames in os.walk(path):
        # Skip common ignore patterns
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d != "__pycache__" and d != "node_modules"
        ]

        for filename in filenames:
            # Include .py and .ts/.tsx files
            if filename.endswith((".py", ".ts", ".tsx")) and not filename.startswith(
                "."
            ):
                file_path = Path(root) / filename
                # Get relative path from base
                try:
                    rel_path = file_path.relative_to(BASE_PATH.parent)
                    files.append(str(rel_path).replace("\\", "/"))
                except ValueError:
                    # Handle files outside BASE_PATH (e.g., tools_root)
                    files.append(str(file_path).replace("\\", "/"))

    return sorted(files)


def generate_module_map() -> Dict[str, List[str]]:
    """
    Generate complete module map for AEGIS.

    Returns:
        Dictionary mapping category names to sorted file lists
    """
    module_map = {}

    for category, path in SCAN_PATHS.items():
        print(f"Scanning {category}: {path}")
        files = scan_directory(path)
        module_map[category] = files
        print(f"  Found {len(files)} files")

    return module_map


def write_module_map(module_map: Dict[str, List[str]], output_path: Path):
    """
    Write module map to JSON file with deterministic formatting.

    Args:
        module_map: Module map dictionary
        output_path: Path to write JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(module_map, f, sort_keys=True, indent=2)

    print(f"\nModule map written to: {output_path}")


def generate_summary(module_map: Dict[str, List[str]]) -> str:
    """
    Generate human-readable summary of module map.

    Args:
        module_map: Module map dictionary

    Returns:
        Summary string
    """
    total_files = sum(len(files) for files in module_map.values())

    summary = "=== QFS Module Discovery Summary ===\n\n"
    summary += f"Total files scanned: {total_files}\n\n"

    for category, files in sorted(module_map.items()):
        summary += f"{category}:\n"
        summary += f"  Files: {len(files)}\n"
        if files:
            summary += f"  Sample: {files[0]}\n"
        summary += "\n"

    return summary


def main():
    """
    Main entry point for discovery scan.
    """
    print("QFS Module Discovery Scanner (Track 0.1)")
    print("=" * 60)
    print()

    # Generate module map
    module_map = generate_module_map()

    # Write to AEGIS directory
    output_path = BASE_PATH / "AEGIS" / "module_map.json"
    write_module_map(module_map, output_path)

    # Print summary
    summary = generate_summary(module_map)
    print()
    print(summary)

    # Write summary to file
    summary_path = BASE_PATH / "AEGIS" / "module_discovery_summary.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        f.write(summary)

    print(f"Summary written to: {summary_path}")
    print()
    print("✅ Track 0.1 Complete: Module map generated")


if __name__ == "__main__":
    main()
