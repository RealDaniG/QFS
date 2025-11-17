"""
AST-based Zero-Simulation Compliance Checker for QFS V13.

This tool scans Python files to ensure they comply with Zero-Simulation requirements
by checking for prohibited constructs like:
- random module usage
- time module functions
- native float operations
- other non-deterministic constructs
"""

import ast
import sys
import os
from typing import List, Tuple, Set, Optional

# Prohibited modules and functions
PROHIBITED_MODULES = {
    'random',
    'time',
    'datetime',
    'threading',
    'asyncio',
    'multiprocessing'
}

PROHIBITED_FUNCTIONS = {
    'time.time',
    'time.clock',
    'time.perf_counter',
    'time.process_time',
    'random.random',
    'random.randint',
    'random.uniform',
    'random.choice',
    'random.choices',
    'os.urandom'
}

PROHIBITED_BUILTINS = {
    'float'
}

class ZeroSimulationChecker(ast.NodeVisitor):
    """AST visitor to check for Zero-Simulation compliance."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.errors: List[Tuple[int, str]] = []
        self.imports: Set[str] = set()
    
    def visit_Import(self, node):
        """Check for prohibited module imports."""
        for alias in node.names:
            if alias.name in PROHIBITED_MODULES:
                self.errors.append((
                    node.lineno,
                    f"Prohibited module import: {alias.name}"
                ))
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Check for prohibited function imports."""
        if node.module in PROHIBITED_MODULES:
            self.errors.append((
                node.lineno,
                f"Prohibited module import: {node.module}"
            ))
        
        if node.module:
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                if full_name in PROHIBITED_FUNCTIONS:
                    self.errors.append((
                        node.lineno,
                        f"Prohibited function import: {full_name}"
                    ))
                self.imports.add(full_name)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check for prohibited function calls."""
        if isinstance(node.func, ast.Attribute):
            # Check for method calls on prohibited modules
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                if module_name in PROHIBITED_MODULES:
                    full_name = f"{module_name}.{node.func.attr}"
                    self.errors.append((
                        node.lineno,
                        f"Prohibited function call: {full_name}"
                    ))
        
        # Check for prohibited built-in functions
        if isinstance(node.func, ast.Name):
            if node.func.id in PROHIBITED_BUILTINS:
                self.errors.append((
                    node.lineno,
                    f"Prohibited built-in function call: {node.func.id}"
                ))
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Check for prohibited built-in names."""
        if node.id in PROHIBITED_BUILTINS:
            # Check if this is a type annotation or actual usage
            # This is a simple check - in practice, you might want more sophisticated analysis
            if isinstance(node.ctx, ast.Load):
                self.errors.append((
                    node.lineno,
                    f"Prohibited built-in usage: {node.id}"
                ))
        self.generic_visit(node)

def check_file(filename: str) -> List[Tuple[int, str]]:
    """Check a single Python file for Zero-Simulation compliance."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        return [(0, f"Error reading file {filename}: {e}")]
    
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error in {filename}: {e.msg}")]
    
    checker = ZeroSimulationChecker(filename)
    checker.visit(tree)
    return checker.errors

def check_directory(directory: str, exclude_dirs: Optional[List[str]] = None) -> dict:
    """Check all Python files in a directory for Zero-Simulation compliance."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    results = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                errors = check_file(filepath)
                if errors:
                    results[filepath] = errors
    
    return results

def main():
    """Main function to run the AST checker."""
    print("QFS V13 Zero-Simulation Compliance Checker")
    print("=" * 45)
    
    # Get the directory to check
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        # Default to the QFS V13 directory
        target = os.path.join(os.path.dirname(__file__), "..")
    
    # Normalize the path
    target = os.path.abspath(target)
    
    print(f"Checking: {target}")
    
    # Check for compliance
    if os.path.isfile(target) and target.endswith('.py'):
        errors = check_file(target)
        results = {target: errors} if errors else {}
    elif os.path.isdir(target):
        results = check_directory(target, exclude_dirs=['__pycache__', '.git', 'venv', 'env'])
    else:
        print(f"Error: {target} is not a valid file or directory")
        return 1
    
    # Report results
    if results:
        print("\n❌ Zero-Simulation Compliance Issues Found:")
        print("-" * 45)
        for filepath, errors in results.items():
            print(f"\nFile: {filepath}")
            for line, error in errors:
                print(f"  Line {line}: {error}")
        return 1
    else:
        print("\n✅ All files passed Zero-Simulation compliance check!")
        return 0

if __name__ == "__main__":
    sys.exit(main())