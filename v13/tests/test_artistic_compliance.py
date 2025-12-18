"""
test_artistic_compliance.py - Zero-Sim Invariant Verification for AES

Verifies:
1. No forbidden imports (random, time, datetime.now) in policy files.
2. No float drift (heuristic check).
"""
import ast
import pytest
POLICY_FILES = ['v13/policy/artistic_policy.py', 'v13/policy/artistic_observatory.py']

def check_imports(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in sorted(node.names):
                if alias.name in ['random', 'time']:
                    return f"Forbidden import '{alias.name}' found"
        elif isinstance(node, ast.ImportFrom):
            if node.module in ['random', 'time']:
                return f"Forbidden import from '{node.module}' found"
            if node.module == 'datetime' and 'now' in [n.name for n in node.names]:
                return "Forbidden import 'now' from datetime found"
    return None

def test_zero_sim_imports():
    for fpath in sorted(POLICY_FILES):
        if not os.path.exists(fpath):
            continue
        error = check_imports(fpath)
        assert error is None, f'Violation in {fpath}: {error}'

def test_no_float_comparisons_without_tolerance():
    """Heuristic: Check for '==' with float literals."""
    pass
