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
import pathlib
import sys
from typing import List, Tuple, Set, Optional
# Add the v13 directory to the path so we can import libs
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

try:
    from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
except ImportError:
    print('Warning: Could not import deterministic helpers')
    # Create dummy classes/functions for the checker
    class ZeroSimAbort(Exception):
        pass
    def det_time_now():
        pass
    def det_perf_counter():
        pass
    def det_random():
        pass
    def qnum(value):
        pass
# Modules that are prohibited in deterministic code paths
PROHIBITED_MODULES = {'random', 'time', 'datetime', 'threading', 'asyncio', 'multiprocessing', 'os', 'sys'}

# Specific functions that are prohibited
PROHIBITED_FUNCTIONS = {
    'time.time', 'time.clock', 'time.perf_counter', 'time.process_time', 
    'random.random', 'random.randint', 'random.uniform', 'random.choice', 'random.choices', 'os.urandom',
    'sys.exit', 'os._exit', 'os.system', 'os.popen'
}

# Built-in functions/types that are prohibited in deterministic code paths
PROHIBITED_BUILTINS = {'float'}

# Replacement suggestions for CI reports
REPLACEMENT_SUGGESTIONS = {
    'time.time': 'det_time_now()',
    'time.perf_counter': 'det_perf_counter()',
    'random.random': 'det_random()',
    'float': 'QAmount() or qnum()',
    'sys.exit': 'raise ZeroSimAbort()'
}

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
        
        # Check for prohibited attribute calls (e.g., time.time(), random.random())
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                if module_name in PROHIBITED_MODULES:
                    full_name = f'{module_name}.{node.func.attr}'
                    suggestion = REPLACEMENT_SUGGESTIONS.get(full_name, 'Use deterministic equivalent')
                    self.errors.append((node.lineno, f'Prohibited function call: {full_name} (suggest: {suggestion})'))
        
        # Check for prohibited built-in calls (e.g., float())
        if isinstance(node.func, ast.Name):
            if node.func.id in PROHIBITED_BUILTINS:
                suggestion = REPLACEMENT_SUGGESTIONS.get(node.func.id, 'Use QAmount() or qnum()')
                self.errors.append((node.lineno, f'Prohibited built-in function call: {node.func.id} (suggest: {suggestion})'))
        
        # Check for sys.exit calls specifically
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == 'sys' and node.func.attr == 'exit':
                self.errors.append((node.lineno, 'Prohibited sys.exit call (suggest: raise ZeroSimAbort())'))
        elif isinstance(node.func, ast.Name) and node.func.id == 'exit':
            self.errors.append((node.lineno, 'Prohibited exit call (suggest: raise ZeroSimAbort())'))
        
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

def check_directory(directory: str, exclude_dirs: Optional[List[str]]=None) -> dict:
    """Check all Python files in a directory for Zero-Simulation compliance."""
    if exclude_dirs is None:
        exclude_dirs = []
    results = {}
    path = pathlib.Path(directory)
    for filepath in path.rglob('*.py'):
        if not any((excluded in filepath.parts for excluded in exclude_dirs)):
            errors = check_file(str(filepath))
            if errors:
                results[str(filepath)] = errors
    return results

def main():
    """Main function to run the AST checker."""
    print('QFS V13 Zero-Simulation Compliance Checker')
    print('=' * 45)
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = str(pathlib.Path(__file__).parent.parent)
    target = str(pathlib.Path(target).resolve())
    print(f'Checking: {target}')
    target_path = pathlib.Path(target)
    if target_path.is_file() and target.endswith('.py'):
        errors = check_file(target)
        results = {target: errors} if errors else {}
    elif target_path.is_dir():
        results = check_directory(target, exclude_dirs=['__pycache__', '.git', 'venv', 'env'])
    else:
        print(f'Error: {target} is not a valid file or directory')
        return 1
    if results:
        print('\n❌ Zero-Simulation Compliance Issues Found:')
        print('-' * 45)
        for filepath, errors in results.items():
            print(f'\nFile: {filepath}')
            for line, error in sorted(errors):
                print(f'  Line {line}: {error}')
        return 1
    else:
        print('\n✅ All files passed Zero-Simulation compliance check!')
        return 0
if __name__ == '__main__':
    exit_code = main()
    # Don't raise an exception, just exit with the appropriate code
    sys.exit(exit_code)
