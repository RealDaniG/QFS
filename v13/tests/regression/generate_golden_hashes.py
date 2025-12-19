import sys
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

try:
    from v13.tests.regression.phase_v14_social_full import run_scenario
except ImportError:
    print("Error: Could not import phase_v14_social_full")
    sys.exit(1)


def generate_golden_hashes():
    print("Generating v14 Golden Regression Hash...")

    # Run scenario and get hash
    # Note: run_scenario now returns the hash string
    current_hash = run_scenario()

    if not current_hash:
        print("Error: No hash returned from regression test")
        sys.exit(1)

    print(f"Captured Hash: {current_hash}")

    golden_data = {
        "v14_social_layer": {
            "hash": current_hash,
            "description": "Canonical v14 social layer regression hash",
            "test_file": "v13/tests/regression/phase_v14_social_full.py",
        }
    }

    output_path = Path("v13/tests/regression/golden_hashes.json")
    with open(output_path, "w") as f:
        json.dump(golden_data, f, indent=2)

    print(f"Golden hashes saved to {output_path}")


if __name__ == "__main__":
    generate_golden_hashes()
