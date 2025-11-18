#!/usr/bin/env python3
"""
Generate the canonical reference hash for Determinism Fuzzer.
This script generates the reference hash that will be used to verify cross-runtime determinism.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from tools.determinism_fuzzer import DeterminismFuzzer


def generate_reference_hash():
    """Generate the canonical reference hash for 100k operations."""
    print("Generating reference hash for Determinism Fuzzer...")
    
    # Create fuzzer with canonical seed
    fuzzer = DeterminismFuzzer(seed=1234567890)
    
    # Run 100k operations to generate reference hash
    reference_hash = fuzzer.run_fuzz_test(100000)
    
    # Save to evidence directory
    os.makedirs("evidence/phase2_fuzzer", exist_ok=True)
    with open("evidence/phase2_fuzzer_ref.sha256", "w") as f:
        f.write(reference_hash)
    
    print(f"Reference hash generated and saved: {reference_hash}")
    return reference_hash


if __name__ == "__main__":
    generate_reference_hash()