"""
Nightly E2E Runner for QFS V13.8

Executes the full suite of operational verification tests:
1. Zero-Mock Compliance Scan
2. Zero-Sim Test Suite
3. Explain-This Integrity Checks
4. AES Signal Verification
5. Performance Benchmarks

Usage: python nightly_e2e.py
"""
import subprocess
import json


def run_step(name, command):
<<<<<<< HEAD
    print(
        f"[{datetime.datetime.now()}] Running {name}..."
    )  # QODO:JUSTIFIED STYLE - Script logging (review in P1)
    start = (
        datetime.datetime.now()
    )  # QODO:JUSTIFIED STYLE - Script timing (review in P1)
    try:
        # Use shell=True for Windows compatibility with simple commands,
        # but list format is safer. Adjusting for python execution.
        if command[0] == "python":
            cmd = [sys.executable] + command[1:]
        else:
            cmd = command

        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = (datetime.datetime.now() - start).total_seconds()

        if result.returncode == 0:
            print(f"✅ {name} PASSED ({duration:.2f}s)")
            return {
                "step": name,
                "status": "PASS",
                "duration": duration,
                "output": result.stdout[:500] + "..."
                if len(result.stdout) > 500
                else result.stdout,
            }
=======
    print(f'[{datetime.datetime.now()}] Running {name}...')
    start = datetime.datetime.now()
    try:
        if command[0] == 'python':
            cmd = [sys.executable] + command[1:]
        else:
            cmd = command
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = (datetime.datetime.now() - start).total_seconds()
        if result.returncode == 0:
            print(f'✅ {name} PASSED ({duration:.2f}s)')
            return {'step': name, 'status': 'PASS', 'duration': duration, 'output': result.stdout[:500] + '...' if len(result.stdout) > 500 else result.stdout}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        else:
            print(f'❌ {name} FAILED ({duration:.2f}s)')
            print(result.stderr)
<<<<<<< HEAD
            return {
                "step": name,
                "status": "FAIL",
                "duration": duration,
                "error": result.stderr,
            }
=======
            return {'step': name, 'status': 'FAIL', 'duration': duration, 'error': result.stderr}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
    except Exception as e:
        print(f'❌ {name} CRASHED: {e}')
        return {'step': name, 'status': 'CRASH', 'error': str(e)}


def main():
<<<<<<< HEAD
    print("=== QFS V13.8 NIGHTLY E2E START ===")

    results = []

    # 0. Zero-Sim Suite (Strict Logic Verification)
    results.append(
        run_step("Zero-Sim Logic Suite", ["python", "scripts/run_zero_sim_suite.py"])
    )

    # 1. Zero-Mock Compliance (Static Scan)
    results.append(
        run_step("Zero-Mock Scan", ["python", "scripts/scan_zero_mock_compliance.py"])
    )

    # 2. Audit Integrity Tests
    results.append(
        run_step(
            "Audit Integrity",
            ["python", "-m", "pytest", "tests/test_audit_integrity.py"],
        )
    )

    # 3. Artistic Signal Tests
    results.append(
        run_step(
            "AES Signal Tests",
            ["python", "-m", "pytest", "tests/test_artistic_signal.py"],
        )
    )

    # 4. Performance Tests
    results.append(
        run_step(
            "Performance Benchmarks",
            ["python", "-m", "pytest", "tests/test_explain_this_performance.py"],
        )
    )

    # 5. Storage Explainability Tests (Integrated)
    # We don't have a specific test file for storage yet, assuming integrated or mock
    # results.append(run_step("Storage Explanation", ["python", "-m", "pytest", "tests/test_storage_explain.py"]))

    # Generate Evidence
    evidence = {
        "timestamp": datetime.datetime.now().isoformat(),
        "suite": "Nightly E2E V13.8",
        "results": results,
        "overall_status": "PASS"
        if all(r["status"] == "PASS" for r in results)
        else "FAIL",
    }

    # Save evidence
    os.makedirs("evidence/nightly", exist_ok=True)
    filename = (
        f"evidence/nightly/run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"=== FINISHED. Evidence saved to {filename} ===")

    if evidence["overall_status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
=======
    print('=== QFS V13.8 NIGHTLY E2E START ===')
    results = []
    results.append(run_step('Zero-Sim Logic Suite', ['python', 'scripts/run_zero_sim_suite.py']))
    results.append(run_step('Zero-Mock Scan', ['python', 'scripts/scan_zero_mock_compliance.py']))
    results.append(run_step('Audit Integrity', ['python', '-m', 'pytest', 'tests/test_audit_integrity.py']))
    results.append(run_step('AES Signal Tests', ['python', '-m', 'pytest', 'tests/test_artistic_signal.py']))
    results.append(run_step('Performance Benchmarks', ['python', '-m', 'pytest', 'tests/test_explain_this_performance.py']))
    evidence = {'timestamp': datetime.datetime.now().isoformat(), 'suite': 'Nightly E2E V13.8', 'results': results, 'overall_status': 'PASS' if all((r['status'] == 'PASS' for r in results)) else 'FAIL'}
    os.makedirs('evidence/nightly', exist_ok=True)
    filename = f"evidence/nightly/run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f'=== FINISHED. Evidence saved to {filename} ===')
    if evidence['overall_status'] == 'FAIL':
        raise ZeroSimAbort(1)
if __name__ == '__main__':
    main()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
