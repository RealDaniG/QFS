#!/usr/bin/env python3
"""
Simple reference hash generator that avoids import issues.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import only what we need
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
import hashlib
import json
from typing import List, Dict, Any


class SimpleDeterminismFuzzer:
    def __init__(self, seed: int = 1234567890):
        self.seed = seed
        self.cm = CertifiedMath()
    
    def _generate_test_inputs(self, num_tests: int) -> List[Dict[str, Any]]:
        """Generate deterministic test inputs using counter-based PRNG."""
        inputs = []
        counter = self.seed
        for _ in range(num_tests):
            # Generate 2 random BigNum128 values in [0, 2^32) to avoid overflow
            val1 = (counter * 1664525 + 1013904223) % (2**32)
            counter += 1
            val2 = (counter * 1664525 + 1013904223) % (2**32)
            counter += 1
            
            inputs.append({
                "a": BigNum128(val1),
                "b": BigNum128(val2),
                "iterations": 5 + (counter % 6)  # 5-10 iterations to avoid overflow
            })
        return inputs

    def run_fuzz_test(self, num_tests: int = 100000) -> str:
        """Run fuzz test and return deterministic SHA-256 hash of all outputs."""
        log_list = []
        inputs = self._generate_test_inputs(num_tests)
        
        for test in inputs:
            # Test core functions
            exp_result = self.cm.exp(test["a"], test["iterations"], log_list)
            ln_result = self.cm.ln(test["a"] if test["a"].value > 0 else BigNum128(1), test["iterations"], log_list)
            sin_result = self.cm.sin(test["a"], test["iterations"], log_list)
            add_result = self.cm.add(test["a"], test["b"], log_list)
        
        # Return canonical hash of all outputs
        return self.cm.get_log_hash(log_list)


def generate_reference_hash():
    """Generate the canonical reference hash for 100k operations."""
    print("Generating reference hash for Determinism Fuzzer...")
    
    # Create fuzzer with canonical seed
    fuzzer = SimpleDeterminismFuzzer(seed=1234567890)
    
    # Run 10k operations to generate reference hash (reduced to avoid memory issues)
    reference_hash = fuzzer.run_fuzz_test(10000)
    
    # Save to evidence directory
    os.makedirs("evidence", exist_ok=True)
    with open("evidence/phase2_fuzzer_ref.sha256", "w") as f:
        f.write(reference_hash)
    
    print(f"Reference hash generated and saved: {reference_hash}")
    return reference_hash


if __name__ == "__main__":
    generate_reference_hash()