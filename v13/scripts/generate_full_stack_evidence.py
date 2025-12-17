"""
generate_full_stack_evidence.py - Nightly Evidence Generation

Runs the full stack determinism test and produces a signed JSON artifact.
"""
import subprocess
import json


def generate_evidence():
<<<<<<< HEAD
    print("Running Full Stack Determinism Test...")
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "v13/tests/integration/test_full_stack_determinism.py",
        "-v",
    ]

    start_time = (
        datetime.datetime.now().isoformat()
    )  # QODO:JUSTIFIED STYLE - Legacy boundary (review in P1)
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = (
        datetime.datetime.now().isoformat()
    )  # QODO:JUSTIFIED STYLE - Legacy boundary (review in P1)

    success = result.returncode == 0

    evidence = {
        "evidence_type": "FULL_STACK_DETERMINISM",
        "timestamp": end_time,
        "duration_seconds": (
            datetime.datetime.fromisoformat(end_time)
            - datetime.datetime.fromisoformat(start_time)
        ).total_seconds(),
        "status": "PASS" if success else "FAIL",
        "verification_suite": "v13/tests/integration/test_full_stack_determinism.py",
        "output_summary": result.stdout[-500:] if result.stdout else "No output",
        "error_summary": result.stderr[-500:] if result.stderr else "No errors",
        "environment": "CI/CD",
    }

    os.makedirs("v13/evidence/nightly", exist_ok=True)
    filename = f"v13/evidence/nightly/full_stack_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"Evidence generated: {filename}")

=======
    print('Running Full Stack Determinism Test...')
    cmd = [sys.executable, '-m', 'pytest', 'v13/tests/integration/test_full_stack_determinism.py', '-v']
    start_time = datetime.datetime.now().isoformat()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = datetime.datetime.now().isoformat()
    success = result.returncode == 0
    evidence = {'evidence_type': 'FULL_STACK_DETERMINISM', 'timestamp': end_time, 'duration_seconds': (datetime.datetime.fromisoformat(end_time) - datetime.datetime.fromisoformat(start_time)).total_seconds(), 'status': 'PASS' if success else 'FAIL', 'verification_suite': 'v13/tests/integration/test_full_stack_determinism.py', 'output_summary': result.stdout[-500:] if result.stdout else 'No output', 'error_summary': result.stderr[-500:] if result.stderr else 'No errors', 'environment': 'CI/CD'}
    os.makedirs('v13/evidence/nightly', exist_ok=True)
    filename = f"v13/evidence/nightly/full_stack_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f'Evidence generated: {filename}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
    if not success:
        print('Verification FAILED')
        raise ZeroSimAbort(1)
    else:
<<<<<<< HEAD
        print("Verification PASSED")
        sys.exit(0)


if __name__ == "__main__":
    generate_evidence()
=======
        print('Verification PASSED')
        raise ZeroSimAbort(0)
if __name__ == '__main__':
    generate_evidence()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
