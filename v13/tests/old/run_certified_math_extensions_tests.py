"""
Test runner for the CertifiedMath extensions.
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import subprocess

def run_certified_math_extensions_tests():
    """Run the CertifiedMath extensions tests."""
    print('Running CertifiedMath extensions tests...')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, 'tests', 'test_certified_math_extensions.py')
    try:
        result = subprocess.run([sys.executable, test_file], cwd=script_dir, capture_output=True, text=True, timeout=30)
        print('STDOUT:')
        print(result.stdout)
        if result.stderr:
            print('STDERR:')
            print(result.stderr)
        if result.returncode == 0:
            print('✓ CertifiedMath extensions tests passed!')
            return True
        else:
            print('✗ CertifiedMath extensions tests failed!')
            return False
    except subprocess.TimeoutExpired:
        print('✗ CertifiedMath extensions tests timed out!')
        return False
    except Exception as e:
        print(f'✗ Error running CertifiedMath extensions tests: {e}')
        return False
if __name__ == '__main__':
    success = run_certified_math_extensions_tests()
    raise ZeroSimAbort(0 if success else 1)
