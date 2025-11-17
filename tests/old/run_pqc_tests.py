"""
Test runner for the PQC library.
"""

import subprocess
import sys
import os


def run_pqc_tests():
    """Run the PQC tests."""
    print("Running PQC tests...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the PQC test file
    test_file = os.path.join(script_dir, "tests", "test_pqc.py")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✓ PQC tests passed!")
            return True
        else:
            print("✗ PQC tests failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ PQC tests timed out!")
        return False
    except Exception as e:
        print(f"✗ Error running PQC tests: {e}")
        return False


if __name__ == "__main__":
    success = run_pqc_tests()
    sys.exit(0 if success else 1)