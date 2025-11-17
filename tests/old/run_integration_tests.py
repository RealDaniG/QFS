"""
Test runner for the integration tests.
"""

import subprocess
import sys
import os

def run_integration_tests():
    """Run the integration tests."""
    print("Running integration tests...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the integration test file
    test_file = os.path.join(script_dir, "tests", "certifiedmath", "integration", "test_certified_math_drv_integration.py")
    
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
            print("✓ Integration tests passed!")
            return True
        else:
            print("✗ Integration tests failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Integration tests timed out!")
        return False
    except Exception as e:
        print(f"✗ Error running integration tests: {e}")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)