#!/usr/bin/env python3
"""
Simple AST checker for QFS V13 to identify forbidden imports and constructs.
"""

import ast
import sys
from pathlib import Path

# Prohibited modules and functions
PROHIBITED_MODULES = {
    'sys', 'os', 'time', 'datetime', 'threading', 'asyncio', 'multiprocessing', 'uuid', 'random'
}

PROHIBITED_FUNCTIONS = {
    'sys.exit', 'os.system', 'os.popen', 'time.time', 'time.clock', 'time.perf_counter',
    'time.process_time', 'random.random', 'random.randint', 'random.uniform',
    'random.choice', 'random.choices', 'os.urandom'
}

PROHIBITED_BUILTINS = {'float'}

def check_file_for_violations(filepath):
    """Check a single Python file for AST violations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []
    
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []
    
    violations = []
    
    # Walk the AST
    for node in ast.walk(tree):
        # Check for prohibited imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in PROHIBITED_MODULES:
                    violations.append(f"Line {node.lineno}: Prohibited import '{alias.name}'")
        
        # Check for prohibited from imports
        if isinstance(node, ast.ImportFrom):
            if node.module in PROHIBITED_MODULES:
                violations.append(f"Line {node.lineno}: Prohibited from import '{node.module}'")
        
        # Check for prohibited function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    full_name = f"{node.func.value.id}.{node.func.attr}"
                    if full_name in PROHIBITED_FUNCTIONS:
                        violations.append(f"Line {node.lineno}: Prohibited function call '{full_name}'")
            
            # Check for prohibited built-in calls
            if isinstance(node.func, ast.Name):
                if node.func.id in PROHIBITED_BUILTINS:
                    violations.append(f"Line {node.lineno}: Prohibited built-in call '{node.func.id}'")
        
        # Check for prohibited built-in names (usage)
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load) and node.id in PROHIBITED_BUILTINS:
                # Check if this is actually a usage vs. declaration
                violations.append(f"Line {node.lineno}: Prohibited built-in usage '{node.id}'")
    
    return violations

def main():
    """Main function to check files."""
    if len(sys.argv) < 2:
        print("Usage: python simple_ast_checker.py <directory_or_file>")
        return 1
    
    target = Path(sys.argv[1])
    
    if target.is_file() and target.suffix == '.py':
        files = [target]
    elif target.is_dir():
        files = list(target.rglob('*.py'))
    else:
        print(f"Error: {target} is not a valid file or directory")
        return 1
    
    total_violations = 0
    
    for filepath in files:
        # Skip certain directories
        if any(skip_dir in str(filepath) for skip_dir in ['__pycache__', '.git', 'venv', 'env']):
            continue
            
        violations = check_file_for_violations(filepath)
        if violations:
            print(f"\nViolations in {filepath}:")
            for violation in violations:
                print(f"  {violation}")
            total_violations += len(violations)
    
    if total_violations > 0:
        print(f"\n❌ Found {total_violations} violations")
        return 1
    else:
        print("\n✅ All files passed AST compliance check!")
        return 0

if __name__ == "__main__":
    sys.exit(main())