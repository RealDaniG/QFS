#!/usr/bin/env python3

"""
Zero-Simulation AST Checker (Python Version)

This script performs structural analysis of Python code files to detect and ban
non-deterministic constructs that violate the Zero-Simulation mandate.

It uses AST (Abstract Syntax Tree) parsing to structurally identify:
- random functions and modules
- time-based functions
- floating-point literals
- os/system functions that could introduce non-determinism

Usage: python zero-sim-ast.py --file <filepath>
"""

import ast
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any


class ZeroSimChecker(ast.NodeVisitor):
    """AST visitor to check for Zero-Simulation violations in Python code."""
    
    # Forbidden imports and functions
    FORBIDDEN_IMPORTS = {
        'random': 'Import of random module is forbidden - violates Zero-Simulation mandate',
        'time': 'Import of time module is forbidden - use DRV_ClockService instead',
        'datetime': 'Import of datetime module is forbidden - use DRV_ClockService instead',
        'threading': 'Import of threading module is forbidden - violates Zero-Simulation mandate',
        'multiprocessing': 'Import of multiprocessing module is forbidden - violates Zero-Simulation mandate',
        'asyncio': 'Import of asyncio module is forbidden - violates Zero-Simulation mandate',
    }
    
    FORBIDDEN_FUNCTIONS = {
        'random.random': 'Use of random.random is forbidden - violates Zero-Simulation mandate',
        'random.randint': 'Use of random.randint is forbidden - violates Zero-Simulation mandate',
        'random.choice': 'Use of random.choice is forbidden - violates Zero-Simulation mandate',
        'time.time': 'Use of time.time is forbidden - use DRV_ClockService instead',
        'time.sleep': 'Use of time.sleep is forbidden - violates Zero-Simulation mandate',
        'datetime.now': 'Use of datetime.now is forbidden - use DRV_ClockService instead',
        'os.urandom': 'Use of os.urandom is forbidden - violates Zero-Simulation mandate',
    }
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: List[Dict[str, Any]] = []
        
    def visit_Import(self, node):
        """Check for forbidden imports."""
        for alias in node.names:
            if alias.name in self.FORBIDDEN_IMPORTS:
                self.violations.append({
                    'type': 'FORBIDDEN_IMPORT',
                    'message': self.FORBIDDEN_IMPORTS[alias.name],
                    'line': node.lineno,
                    'column': node.col_offset,
                    'import': alias.name
                })
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Check for forbidden from imports."""
        if node.module in self.FORBIDDEN_IMPORTS:
            self.violations.append({
                'type': 'FORBIDDEN_IMPORT',
                'message': self.FORBIDDEN_IMPORTS[node.module],
                'line': node.lineno,
                'column': node.col_offset,
                'import': node.module
            })
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Check for forbidden function calls."""
        if isinstance(node.func, ast.Attribute):
            # Handle method calls like random.random()
            module = None
            if isinstance(node.func.value, ast.Name):
                module = node.func.value.id
            function_name = f"{module}.{node.func.attr}" if module else node.func.attr
            
            if function_name in self.FORBIDDEN_FUNCTIONS:
                self.violations.append({
                    'type': 'FORBIDDEN_FUNCTION',
                    'message': self.FORBIDDEN_FUNCTIONS[function_name],
                    'line': node.lineno,
                    'column': node.col_offset,
                    'function': function_name
                })
        elif isinstance(node.func, ast.Name):
            # Handle direct function calls
            function_name = node.func.id
            if function_name in self.FORBIDDEN_FUNCTIONS:
                self.violations.append({
                    'type': 'FORBIDDEN_FUNCTION',
                    'message': self.FORBIDDEN_FUNCTIONS[function_name],
                    'line': node.lineno,
                    'column': node.col_offset,
                    'function': function_name
                })
        self.generic_visit(node)
        
    def visit_Num(self, node):
        """Check for floating-point literals (Python < 3.8)."""
        if isinstance(node.n, float):
            self.violations.append({
                'type': 'FLOATING_POINT',
                'message': 'Use of floating-point literals is forbidden - use CertifiedMath fixed-point instead',
                'line': node.lineno,
                'column': node.col_offset,
                'value': node.n
            })
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        """Check for floating-point literals (Python >= 3.8)."""
        if isinstance(node.value, float):
            self.violations.append({
                'type': 'FLOATING_POINT',
                'message': 'Use of floating-point literals is forbidden - use CertifiedMath fixed-point instead',
                'line': node.lineno,
                'column': node.col_offset,
                'value': node.value
            })
        self.generic_visit(node)
        
    def print_violations(self):
        """Print violations in a structured format."""
        if not self.violations:
            print(f"✅ No Zero-Simulation violations found in {self.filepath}")
            return
            
        print(f"❌ {len(self.violations)} Zero-Simulation violations found in {self.filepath}:")
        for i, violation in enumerate(self.violations, 1):
            print(f"  {i}. {violation['type']}: {violation['message']}")
            print(f"     Location: Line {violation['line']}, Column {violation['column']}")
            if 'import' in violation:
                print(f"     Import: {violation['import']}")
            if 'function' in violation:
                print(f"     Function: {violation['function']}")
            if 'value' in violation:
                print(f"     Value: {violation['value']}")
            print()
            
    def generate_report(self) -> Dict[str, Any]:
        """Generate machine-readable report."""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'file': self.filepath,
            'violations': self.violations,
            'passed': len(self.violations) == 0
        }


def check_file(filepath: str) -> Dict[str, Any]:
    """Check a file for Zero-Simulation violations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
            
        tree = ast.parse(source)
        checker = ZeroSimChecker(filepath)
        checker.visit(tree)
        checker.print_violations()
        
        return checker.generate_report()
    except SyntaxError as e:
        violation = {
            'type': 'PARSE_ERROR',
            'message': f'Failed to parse file: {e.msg}',
            'line': e.lineno,
            'column': e.offset
        }
        print(f"❌ Parse error in {filepath}: {violation['message']}")
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'file': filepath,
            'violations': [violation],
            'passed': False
        }
    except Exception as e:
        violation = {
            'type': 'GENERAL_ERROR',
            'message': f'Error checking file: {str(e)}',
            'line': 0,
            'column': 0
        }
        print(f"❌ Error checking {filepath}: {violation['message']}")
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'file': filepath,
            'violations': [violation],
            'passed': False
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Zero-Simulation AST Checker')
    parser.add_argument('--file', required=True, help='Path to the file to check')
    args = parser.parse_args()
    
    # Check if file exists
    try:
        with open(args.file, 'r'):
            pass
    except FileNotFoundError:
        print(f"Error: File {args.file} does not exist")
        sys.exit(1)
        
    # Run the checker
    report = check_file(args.file)
    
    # Write report to file
    report_file = args.file.rsplit('.', 1)[0] + '_zero_sim_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()