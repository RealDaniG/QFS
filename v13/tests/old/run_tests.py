#!/usr/bin/env python3
"""
Test Runner for CertifiedMath.py
"""

import subprocess
import sys
import os

def run_tests():
    """Run the CertifiedMath test suite"""
    print("Running CertifiedMath Test Suite...")
    print("=" * 50)
    
    # Change to the V13 directory
    v13_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(v13_dir)
    
    # Run the tests
    try:
        result = subprocess.run([sys.executable, "tests/test_certified_math.py"], 
                              capture_output=True, text=True, cwd=v13_dir)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)