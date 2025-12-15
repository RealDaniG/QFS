"""
Zero-Sim Test Suite Runner - QFS V13.8

Executes the subset of tests that must strictly adhere to Zero-Simulation invariants:
- No wall-clock time
- No random floats
- No external I/O
- Deterministic behavior

Targets: v13/tests
"""

import pytest
import sys
import os

def main():
    print(">> Running Zero-Sim Test Suite...")
    
    # Arguments for pytest
    # -v: verbose
    # -m zero_sim: (Optional) if we had markers, but for now we target specific critical files
    
    target_tests = [
        "tests/test_audit_integrity.py",
        "tests/test_artistic_signal.py",
        "tests/test_explain_this_performance.py"
        # Add other core tests as they are verified compliant
    ]
    
    # Check if files exist
    valid_targets = []
    for t in target_tests:
        if os.path.exists(t):
            valid_targets.append(t)
        else:
            print(f"Warning: Test file {t} not found, skipping.")
            
    if not valid_targets:
        print("No valid Zero-Sim tests found!")
        sys.exit(1)
        
    exit_code = pytest.main(["-v"] + valid_targets)
    
    if exit_code == 0:
        print("[OK] Zero-Sim Suite PASSED")
        sys.exit(0)
    else:
        print("[FAIL] Zero-Sim Suite FAILED")
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
