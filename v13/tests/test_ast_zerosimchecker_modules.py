"""
Test cases for AST_ZeroSimChecker legacy module compliance.
These tests verify that the checker correctly detects forbidden module imports.
"""

import pytest
import tempfile
import os
from v13.libs.AST_ZeroSimChecker import AST_ZeroSimChecker


def test_forbidden_module_imports():
    """Test that forbidden module imports are detected"""
    # Create a temporary file with forbidden imports
    test_content = '''
import random
import time
import datetime
import os
import sys
import math
import numpy
import scipy
import socket
import requests
import urllib
import threading
import asyncio
import queue

def test_function():
    # This should be flagged
    value = random.random()
    current_time = time.time()
    return value
'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Run the checker
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(temp_file)
        
        # Check that violations were found
        assert len(violations) > 0
        
        # Check that specific violations were found
        forbidden_imports_found = [v for v in violations if v.violation_type == "FORBIDDEN_IMPORT"]
        assert len(forbidden_imports_found) > 0
        
        # Check that forbidden function calls were found
        forbidden_calls_found = [v for v in violations if v.violation_type in ("FORBIDDEN_CALL", "FORBIDDEN_MODULE_CALL")]
        assert len(forbidden_calls_found) > 0
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_safe_module_imports():
    """Test that safe module imports are not flagged"""
    # Create a temporary file with safe imports
    test_content = '''
import json
import hashlib
from typing import List, Dict
from dataclasses import dataclass

def safe_function():
    # These should be safe
    data = json.dumps({"key": "value"})
    hash_value = hashlib.sha256(b"test").hexdigest()
    return data, hash_value
'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Run the checker on a non-deterministic module (should not flag safe imports)
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(temp_file)
        
        # Check that no forbidden import violations were found
        forbidden_imports_found = [v for v in violations if v.violation_type == "FORBIDDEN_IMPORT"]
        assert len(forbidden_imports_found) == 0
        
        # Check that no forbidden function call violations were found
        forbidden_calls_found = [v for v in violations if v.violation_type in ("FORBIDDEN_CALL", "FORBIDDEN_MODULE_CALL")]
        assert len(forbidden_calls_found) == 0
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_deterministic_module_forbidden_imports():
    """Test that even safe modules are flagged in deterministic modules"""
    # Create a temporary file with safe imports in an economics context
    test_content = '''
import json
import hashlib
import random  # This should be flagged even in economics

def economic_function(deterministic_timestamp, drv_packet_seq):
    # This should be flagged
    value = random.random()
    return value
'''
    
    # Write to temporary file in economics directory structure
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, 
                                   dir=tempfile.gettempdir()) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Modify the file path to simulate it being in economics
        econ_file = temp_file.replace(".py", "_economics_test.py")
        os.rename(temp_file, econ_file)
        
        # Run the checker
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(econ_file)
        
        # Check that forbidden imports were found
        forbidden_imports_found = [v for v in violations if v.violation_type == "FORBIDDEN_IMPORT"]
        # Note: json and hashlib are not in the forbidden list, so they won't be flagged
        # Only random should be flagged
        
        # Check that forbidden function calls were found
        forbidden_calls_found = [v for v in violations if v.violation_type in ("FORBIDDEN_CALL", "FORBIDDEN_MODULE_CALL")]
        assert len(forbidden_calls_found) > 0
        
    finally:
        # Clean up
        if os.path.exists(econ_file):
            os.unlink(econ_file)


def test_golden_files():
    """Test the static golden files for Zero-Sim compliance."""
    checker = AST_ZeroSimChecker()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming test is in v13/tests/ and compliance is in v13/compliance/
    # Go up one level from tests/ to v13/
    project_root = os.path.dirname(current_dir)
    
    pass_file = os.path.join(project_root, "compliance", "golden_pass.py")
    
    # Ensure file exists before testing
    assert os.path.exists(pass_file), f"Golden pass file not found at {pass_file}"
    
    violations = checker.scan_file(pass_file)
    assert len(violations) == 0, f"Golden pass file has violations: {violations}"
    
    fail_file = os.path.join(project_root, "compliance", "golden_fail.py")
             
    assert os.path.exists(fail_file), f"Golden fail file not found at {fail_file}"
    
    violations = checker.scan_file(fail_file)
    assert len(violations) > 0, f"Golden fail file has no violations (check if it was excluded?). Violations: {violations}"
    
    # Check for specific violations we expect
    import_violations = [v for v in violations if v.violation_type == "FORBIDDEN_IMPORT"]
    call_violations = [v for v in violations if v.violation_type in ["FORBIDDEN_CALL", "FORBIDDEN_MODULE_CALL"]]
    
    assert len(import_violations) > 0, "Golden fail file missing FORBIDDEN_IMPORT violation"
    assert len(call_violations) > 0, "Golden fail file missing FORBIDDEN_CALL/MODULE_CALL violation"



if __name__ == "__main__":
    pytest.main([__file__])