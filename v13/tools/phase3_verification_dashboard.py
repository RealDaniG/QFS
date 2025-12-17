#!/usr/bin/env python3
"""
Phase 3 Verification Dashboard
Tracks progress and runs verification checks.

Usage:
    python v13/tools/phase3_verification_dashboard.py

Outputs:
    - Console dashboard with current status
    - phase3_progress.json with detailed metrics
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def run_ast_check(root_dir: str = ".") -> dict:
    """Run AST checker and count violations"""
    try:
        result = subprocess.run(
            ["python", "v13/libs/AST_ZeroSimChecker.py", "v13/"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Parse output for violation count
        violations = 0
        for line in result.stdout.split("\n"):
            if "violations found" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "violations" in part and i > 0:
                        violations = int(parts[i - 1])
                        break

        return {
            "total": violations,
            "exit_code": result.returncode,
            "output": result.stdout[:500],  # First 500 chars
        }
    except subprocess.TimeoutExpired:
        return {"total": -1, "exit_code": -1, "output": "TIMEOUT"}
    except Exception as e:
        return {"total": -1, "exit_code": -1, "output": str(e)}


def run_tests(root_dir: str = ".") -> dict:
    """Run test suite"""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "v13/tests/", "-v", "--tb=short", "-x"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Parse output for test counts
        passed = failed = 0
        for line in result.stdout.split("\n"):
            if "passed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if "passed" in part.lower() and i > 0:
                        try:
                            passed = int(parts[i - 1])
                        except:
                            pass
            if "failed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if "failed" in part.lower() and i > 0:
                        try:
                            failed = int(parts[i - 1])
                        except:
                            pass

        return {
            "passed": passed,
            "failed": failed,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"passed": 0, "failed": -1, "exit_code": -1, "success": False}
    except Exception as e:
        return {"passed": 0, "failed": -1, "exit_code": -1, "success": False}


def count_print_statements(root_dir: str = ".") -> int:
    """Count remaining print() statements in tests"""
    test_dir = Path(root_dir) / "v13" / "tests"
    if not test_dir.exists():
        return -1

    count = 0
    for py_file in test_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Count print( but not in comments
                for line in content.split("\n"):
                    if "print(" in line and not line.strip().startswith("#"):
                        count += 1
        except:
            pass

    return count


def generate_report(root_dir: str = ".") -> dict:
    """Generate comprehensive progress report"""
    print(f"{Colors.BLUE}Running verification checks...{Colors.END}")

    # Run checks
    violations_data = run_ast_check(root_dir)
    tests_data = run_tests(root_dir)
    print_count = count_print_statements(root_dir)

    # Calculate metrics
    baseline_violations = 1616
    violations = violations_data["total"]

    if violations >= 0:
        violations_fixed = baseline_violations - violations
        compliance_percent = (violations_fixed / baseline_violations) * 100
    else:
        violations_fixed = 0
        compliance_percent = 0

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "baseline_violations": baseline_violations,
        "current_violations": violations,
        "violations_fixed": violations_fixed,
        "compliance_percent": compliance_percent,
        "tests": tests_data,
        "print_statements_remaining": print_count,
        "ast_check": violations_data,
    }

    # Print dashboard
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}PHASE 3 VERIFICATION DASHBOARD{Colors.END}")
    print("=" * 70)
    print(f"Timestamp: {report['timestamp']}")
    print()

    # Violations section
    print(f"{Colors.BOLD}Zero-Sim Compliance:{Colors.END}")
    if violations >= 0:
        color = (
            Colors.GREEN
            if violations == 0
            else Colors.YELLOW
            if violations < 500
            else Colors.RED
        )
        print(f"  Violations: {color}{violations}/{baseline_violations}{Colors.END}")
        print(f"  Fixed: {Colors.GREEN}{violations_fixed}{Colors.END}")
        print(f"  Compliance: {color}{compliance_percent:.1f}%{Colors.END}")
    else:
        print(f"  {Colors.RED}AST Check Failed{Colors.END}")
    print()

    # Tests section
    print(f"{Colors.BOLD}Test Suite:{Colors.END}")
    if tests_data["success"]:
        print(f"  Status: {Colors.GREEN}✅ PASSING{Colors.END}")
        print(f"  Passed: {Colors.GREEN}{tests_data['passed']}{Colors.END}")
    else:
        print(f"  Status: {Colors.RED}❌ FAILING{Colors.END}")
        print(f"  Passed: {tests_data['passed']}")
        print(f"  Failed: {Colors.RED}{tests_data['failed']}{Colors.END}")
    print()

    # Batch 1 specific
    print(f"{Colors.BOLD}Batch 1 Progress:{Colors.END}")
    if print_count >= 0:
        color = Colors.GREEN if print_count == 0 else Colors.YELLOW
        print(f"  print() statements: {color}{print_count}{Colors.END}")
    else:
        print(f"  {Colors.RED}Could not count print statements{Colors.END}")
    print()

    # Overall status
    print(f"{Colors.BOLD}Overall Status:{Colors.END}")
    if violations == 0 and tests_data["success"]:
        print(f"  {Colors.GREEN}🎉 PHASE 3 COMPLETE - ZERO-SIM VERIFIED!{Colors.END}")
    elif violations < baseline_violations and tests_data["success"]:
        print(
            f"  {Colors.YELLOW}⚙️  IN PROGRESS - {compliance_percent:.0f}% Complete{Colors.END}"
        )
    else:
        print(f"  {Colors.RED}⚠️  NEEDS ATTENTION{Colors.END}")

    print("=" * 70)

    # Save report
    report_path = Path(root_dir) / "phase3_progress.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Report saved to: {report_path}")

    return report


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    report = generate_report(root)

    # Exit with appropriate code
    if report["current_violations"] == 0 and report["tests"]["success"]:
        sys.exit(0)
    else:
        sys.exit(1)
