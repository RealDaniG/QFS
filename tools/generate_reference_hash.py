#!/usr/bin/env python3

"""
Generate canonical reference hash for determinism fuzzer.
This script generates the reference hash with 100k operations as required for QFS V13.5.
"""

import sys
import os
import json

# Add the src/tools directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools'))

from determinism_fuzzer import DeterminismFuzzer

def main():
    print("Generating canonical reference hash...")
    
    # Create fuzzer
    fuzzer = DeterminismFuzzer()
    
    # Run 100k operations to generate reference hash
    reference_hash = fuzzer.run_fuzz_test(100000)
    
    # Save to evidence directory
    os.makedirs("evidence", exist_ok=True)
    with open("evidence/phase2_fuzzer_ref.sha256", "w") as f:
        f.write(reference_hash)
    
    print(f"Reference hash generated: {reference_hash}")
    print("Saved to evidence/phase2_fuzzer_ref.sha256")

if __name__ == "__main__":
    main()