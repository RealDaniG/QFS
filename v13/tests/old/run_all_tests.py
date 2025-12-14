"""
Comprehensive test runner for all QFS V13 tests.
"""

import subprocess
import sys
import os

def run_tests(test_name, test_file):
    """Run a specific test file."""
    print(f"Running {test_name}...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the test file
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
            print(f"✓ {test_name} passed!")
            return True
        else:
            print(f"✗ {test_name} failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {test_name} timed out!")
        return False
    except Exception as e:
        print(f"✗ Error running {test_name}: {e}")
        return False

def run_all_tests():
    """Run all QFS V13 tests."""
    print("Running all QFS V13 tests...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of test files to run
    test_files = [
        ("CertifiedMath extensions tests", os.path.join(script_dir, "tests", "test_certified_math_extensions.py")),
        ("CertifiedMath DRV integration tests", os.path.join(script_dir, "tests", "test_certified_math_drv_integration.py")),
        ("DRV Packet tests", os.path.join(script_dir, "tests", "test_drv_packet.py")),
        ("CertifiedMath tests", os.path.join(script_dir, "tests", "test_certified_math.py")),
    ]
    
    # Run each test file
    all_passed = True
    for test_name, test_file in test_files:
        if os.path.exists(test_file):
            success = run_tests(test_name, test_file)
            if not success:
                all_passed = False
        else:
            print(f"Skipping {test_name} - test file not found: {test_file}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎉 All QFS V13 tests passed!")
    else:
        print("\n❌ Some QFS V13 tests failed!")
    sys.exit(0 if success else 1)