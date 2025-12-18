"""
Test Runner for CertifiedMath.py
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import subprocess

def run_tests():
    """Run the CertifiedMath test suite"""
    print('Running CertifiedMath Test Suite...')
    print('=' * 50)
    v13_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(v13_dir)
    try:
        result = subprocess.run([sys.executable, 'tests/test_certified_math.py'], capture_output=True, text=True, cwd=v13_dir)
        print(result.stdout)
        if result.stderr:
            print('STDERR:', result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f'Error running tests: {e}')
        return False
if __name__ == '__main__':
    success = run_tests()
    raise ZeroSimAbort(0 if success else 1)
