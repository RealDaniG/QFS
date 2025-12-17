"""
Comprehensive AST checker for QFS V13 with proper exclusion handling
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import ast
import pathlib
from typing import List, Tuple, Set, Optional
PROHIBITED_MODULES = {'random', 'time', 'datetime', 'threading', 'asyncio', 'multiprocessing'}
PROHIBITED_FUNCTIONS = {'time.time', 'time.clock', 'time.perf_counter', 'time.process_time', 'random.random', 'random.randint', 'random.uniform', 'random.choice', 'random.choices', 'os.urandom'}
PROHIBITED_BUILTINS = {'float'}
EXCLUDED_DIRS = {'__pycache__', '.git', 'venv', 'env', '.pytest_cache', '.vscode', '.idea'}
EXCLUDED_FILES = {'deterministic_helpers.py', 'ast_checker.py', 'targeted_checker.py', 'simple_checker.py'}

class ZeroSimulationChecker(ast.NodeVisitor):
    """AST visitor to check for Zero-Simulation compliance."""

    def __init__(self, filename: str):
        self.filename = filename
        self.errors: List[Tuple[int, str]] = []
        self.imports: Set[str] = set()
        self.visit_count = 0
        self.max_visits = 10000

    def visit_Import(self, node):
        """Check for prohibited module imports."""
        if self.visit_count >= self.max_visits:
            return
        self.visit_count += 1
        for alias in node.names:
            if alias.name in PROHIBITED_MODULES:
                self.errors.append((node.lineno, f'Prohibited module import: {alias.name}'))
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check for prohibited function imports."""
        if self.visit_count >= self.max_visits:
            return
        self.visit_count += 1
        if node.module in PROHIBITED_MODULES:
            self.errors.append((node.lineno, f'Prohibited module import: {node.module}'))
        if node.module:
            for alias in node.names:
                full_name = f'{node.module}.{alias.name}'
                if full_name in PROHIBITED_FUNCTIONS:
                    self.errors.append((node.lineno, f'Prohibited function import: {full_name}'))
                self.imports.add(full_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        """Check for prohibited function calls."""
        if self.visit_count >= self.max_visits:
            return
        self.visit_count += 1
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                if module_name in PROHIBITED_MODULES:
                    full_name = f'{module_name}.{node.func.attr}'
                    self.errors.append((node.lineno, f'Prohibited function call: {full_name}'))
        if isinstance(node.func, ast.Name):
            if node.func.id in PROHIBITED_BUILTINS:
                self.errors.append((node.lineno, f'Prohibited built-in function call: {node.func.id}'))
        self.generic_visit(node)

    def visit_Name(self, node):
        """Check for prohibited built-in names."""
        if self.visit_count >= self.max_visits:
            return
        self.visit_count += 1
        if node.id in PROHIBITED_BUILTINS:
            if isinstance(node.ctx, ast.Load):
                self.errors.append((node.lineno, f'Prohibited built-in usage: {node.id}'))
        self.generic_visit(node)

def check_file(filename: str) -> List[Tuple[int, str]]:
    """Check a single Python file for Zero-Simulation compliance."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        return [(0, f'Error reading file {filename}: {e}')]
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as e:
        return [(e.lineno or 0, f'Syntax error in {filename}: {e.msg}')]
    checker = ZeroSimulationChecker(filename)
    checker.visit(tree)
    return checker.errors

def should_exclude_file(filepath: pathlib.Path) -> bool:
    """Check if a file should be excluded from checking."""
    if any((excluded_dir in filepath.parts for excluded_dir in EXCLUDED_DIRS)):
        return True
    if filepath.name in EXCLUDED_FILES:
        return True
    return False

def check_directory(directory: str) -> dict:
    """Check all Python files in a directory for Zero-Simulation compliance."""
    results = {}
    path = pathlib.Path(directory)
    for filepath in path.rglob('*.py'):
        if not should_exclude_file(filepath):
            errors = check_file(str(filepath))
            if errors:
                results[str(filepath)] = errors
    return results

def main():
    """Main function to run the comprehensive checker."""
    print('QFS V13 Zero-Simulation Compliance Checker')
    print('=' * 45)
    target = 'v13'
    print(f'Checking: {target}')
    results = check_directory(target)
    if results:
        print('\n❌ Zero-Simulation Compliance Issues Found:')
        print('-' * 45)
        for filepath, errors in results.items():
            print(f'\nFile: {filepath}')
            for line, error in errors:
                print(f'  Line {line}: {error}')
        return 1
    else:
        print('\n✅ All files passed Zero-Simulation compliance check!')
        return 0
if __name__ == '__main__':
    
    raise ZeroSimAbort(main())