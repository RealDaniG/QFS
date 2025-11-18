# determinism_fuzzer.py

import hashlib
import json
from typing import List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs.CertifiedMath import CertifiedMath, BigNum128


class DeterminismFuzzer:
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

    def compare_with_reference(self, reference_hash: str, num_tests: int = 100000) -> bool:
        """Compare against known-good hash from reference runtime."""
        actual_hash = self.run_fuzz_test(num_tests)
        return actual_hash == reference_hash


# Test function
def test_determinism_fuzzer():
    """Test the DeterminismFuzzer implementation."""
    print("Testing DeterminismFuzzer...")
    
    # Create fuzzer
    fuzzer = DeterminismFuzzer()
    
    # Run a small test
    test_hash = fuzzer.run_fuzz_test(1000)
    print(f"Test hash (1000 ops): {test_hash}")
    
    # Compare with reference (will fail since we don't have a reference)
    is_same = fuzzer.compare_with_reference(test_hash, 1000)
    print(f"Self-comparison: {is_same}")
    
    print("✓ DeterminismFuzzer test completed!")


def main():
    """Main function to run the DeterminismFuzzer with command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='QFS V13.5 Determinism Fuzzer')
    parser.add_argument('--mode', choices=['dev', 'pre-release', 'release'], default='dev',
                        help='Audit mode (default: dev)')
    parser.add_argument('--runtime', default='python',
                        help='Target runtime (default: python)')
    parser.add_argument('--runs', type=int, 
                        help='Number of operations to run')
    parser.add_argument('--out', 
                        help='Output file path')
    parser.add_argument('--test_mode', choices=['true', 'false'], default='false',
                        help='Test mode (default: false)')
    
    args = parser.parse_args()
    
    # Set runs based on mode if not explicitly set
    if args.runs is None:
        if args.mode == 'dev':
            runs = 5000
        elif args.mode == 'pre-release':
            runs = 25000
        elif args.mode == 'release':
            runs = 100000
        else:
            runs = 1000
    else:
        runs = args.runs
    
    print(f"Running Determinism Fuzzer - Mode: {args.mode}, Runtime: {args.runtime}, Runs: {runs}")
    
    # Create fuzzer
    fuzzer = DeterminismFuzzer()
    
    # Run fuzz test
    hash_result = fuzzer.run_fuzz_test(runs)
    
    # Output result
    result = {
        'runtime': args.runtime,
        'mode': args.mode,
        'runs': runs,
        'hash': hash_result
    }
    
    if args.out:
        import json
        with open(args.out, 'w') as f:
            json.dump(result, f)
        print(f"Results saved to {args.out}")
    else:
        print(f"Hash: {hash_result}")
    
    return hash_result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        test_determinism_fuzzer()