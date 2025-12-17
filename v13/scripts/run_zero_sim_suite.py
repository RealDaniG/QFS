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

def main():
    print('>> Running Zero-Sim Test Suite...')
    target_tests = ['v13/tests/test_audit_integrity.py', 'v13/tests/test_artistic_signal.py', 'v13/tests/test_explain_this_performance.py', 'v13/ATLAS/src/tests/test_explain_this_e2e.py']
    valid_targets = []
    for t in sorted(target_tests):
        if os.path.exists(t):
            valid_targets.append(t)
        else:
            print(f'Warning: Test file {t} not found, skipping.')
    if not valid_targets:
        print('No valid Zero-Sim tests found!')
        raise ZeroSimAbort(1)
    exit_code = pytest.main(['-v'] + valid_targets)
    if exit_code == 0:
        print('[OK] Zero-Sim Suite PASSED')
        raise ZeroSimAbort(0)
    else:
        print('[FAIL] Zero-Sim Suite FAILED')
        raise ZeroSimAbort(exit_code)
if __name__ == '__main__':
    main()