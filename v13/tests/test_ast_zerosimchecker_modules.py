"""
Test cases for AST_ZeroSimChecker legacy module compliance.
These tests verify that the checker correctly detects forbidden module imports.
"""
import pytest
import tempfile
from v13.libs.AST_ZeroSimChecker import AST_ZeroSimChecker

def test_forbidden_module_imports():
    """Test that forbidden module imports are detected"""
    test_content = '\nimport random\nimport time\nimport datetime\nimport os\nimport sys\nimport math\nimport numpy\nimport scipy\nimport socket\nimport requests\nimport urllib\nimport threading\nimport asyncio\nimport queue\n\ndef test_function():\n    # This should be flagged\n    value = random.random()\n    current_time = time.time()\n    return value\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    try:
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(temp_file)
        assert len(violations) > 0
        forbidden_imports_found = [v for v in violations if v.violation_type == 'FORBIDDEN_IMPORT']
        assert len(forbidden_imports_found) > 0
        forbidden_calls_found = [v for v in violations if v.violation_type in ('FORBIDDEN_CALL', 'FORBIDDEN_MODULE_CALL')]
        assert len(forbidden_calls_found) > 0
    finally:
        os.unlink(temp_file)

def test_safe_module_imports():
    """Test that safe module imports are not flagged"""
    test_content = '\nimport json\nimport hashlib\nfrom typing import List, Dict\nfrom dataclasses import dataclass\n\ndef safe_function():\n    # These should be safe\n    data = json.dumps({"key": "value"})\n    hash_value = hashlib.sha256(b"test").hexdigest()\n    return data, hash_value\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    try:
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(temp_file)
        forbidden_imports_found = [v for v in violations if v.violation_type == 'FORBIDDEN_IMPORT']
        assert len(forbidden_imports_found) == 0
        forbidden_calls_found = [v for v in violations if v.violation_type in ('FORBIDDEN_CALL', 'FORBIDDEN_MODULE_CALL')]
        assert len(forbidden_calls_found) == 0
    finally:
        os.unlink(temp_file)

def test_deterministic_module_forbidden_imports():
    """Test that even safe modules are flagged in deterministic modules"""
    test_content = '\nimport json\nimport hashlib\nimport random  # This should be flagged even in economics\n\ndef economic_function(deterministic_timestamp, drv_packet_seq):\n    # This should be flagged\n    value = random.random()\n    return value\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=tempfile.gettempdir()) as f:
        f.write(test_content)
        temp_file = f.name
    try:
        econ_file = temp_file.replace('.py', '_economics_test.py')
        os.rename(temp_file, econ_file)
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(econ_file)
        forbidden_imports_found = [v for v in violations if v.violation_type == 'FORBIDDEN_IMPORT']
        forbidden_calls_found = [v for v in violations if v.violation_type in ('FORBIDDEN_CALL', 'FORBIDDEN_MODULE_CALL')]
        assert len(forbidden_calls_found) > 0
    finally:
        if os.path.exists(econ_file):
            os.unlink(econ_file)

def test_golden_files():
    """Test the static golden files for Zero-Sim compliance."""
    checker = AST_ZeroSimChecker()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    pass_file = os.path.join(project_root, 'compliance', 'golden_pass.py')
    assert os.path.exists(pass_file), f'Golden pass file not found at {pass_file}'
    violations = checker.scan_file(pass_file)
    assert len(violations) == 0, f'Golden pass file has violations: {violations}'
    fail_file = os.path.join(project_root, 'compliance', 'golden_fail.py')
    assert os.path.exists(fail_file), f'Golden fail file not found at {fail_file}'
    violations = checker.scan_file(fail_file)
    assert len(violations) > 0, f'Golden fail file has no violations (check if it was excluded?). Violations: {violations}'
    import_violations = [v for v in violations if v.violation_type == 'FORBIDDEN_IMPORT']
    call_violations = [v for v in violations if v.violation_type in ['FORBIDDEN_CALL', 'FORBIDDEN_MODULE_CALL']]
    assert len(import_violations) > 0, 'Golden fail file missing FORBIDDEN_IMPORT violation'
    assert len(call_violations) > 0, 'Golden fail file missing FORBIDDEN_CALL/MODULE_CALL violation'
    float_violations = [v for v in violations if v.violation_type == 'NONDETERMINISTIC_FLOAT']
    iter_violations = [v for v in violations if v.violation_type in ['NONDETERMINISTIC_ITERATION', 'NONDETERMINISTIC_COMP']]
    assert len(float_violations) > 0, 'Golden fail file missing NONDETERMINISTIC_FLOAT violation'
    assert len(iter_violations) > 0, 'Golden fail file missing NONDETERMINISTIC_ITERATION/COMP violation'
if __name__ == '__main__':
    pytest.main([__file__])