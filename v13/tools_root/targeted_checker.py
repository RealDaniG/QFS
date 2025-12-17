"""
Targeted AST checker to debug recursion issues
"""
import ast
import pathlib
from typing import List, Tuple, Set, Optional
PROHIBITED_MODULES = {'random', 'time', 'datetime', 'threading', 'asyncio', 'multiprocessing'}
PROHIBITED_FUNCTIONS = {'time.time', 'time.clock', 'time.perf_counter', 'time.process_time', 'random.random', 'random.randint', 'random.uniform', 'random.choice', 'random.choices', 'os.urandom'}
PROHIBITED_BUILTINS = {'float'}

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
        for alias in sorted(node.names):
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
            for alias in sorted(node.names):
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

def main():
    """Main function to run the targeted checker."""
    print('Targeted AST Checker')
    print('=' * 20)
    target_files = ['v13/tools_root/ast_checker.py', 'v13/tools_root/auto_fix_violations.py']
    for target_file in sorted(target_files):
        print(f'Checking: {target_file}')
        try:
            errors = check_file(target_file)
            if errors:
                print(f'  Found {len(errors)} errors:')
                for line, error in sorted(errors):
                    print(f'    Line {line}: {error}')
            else:
                print('  No errors found')
        except Exception as e:
            print(f'  Error checking file: {e}')
            import traceback
            traceback.print_exc()
if __name__ == '__main__':
    main()