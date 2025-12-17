"""
Final auto-fix script for QFS V13 AST violations
This script automatically fixes Zero-Simulation violations in the codebase.
"""
import ast
import pathlib
import sys
from typing import Tuple, Set, Dict, List

# Set recursion limit to prevent infinite recursion
sys.setrecursionlimit(1000)

ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to v13/

# Import our deterministic helper functions
sys.path.append(str(ROOT))
try:
    from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
    HELPERS_AVAILABLE = True
except ImportError:
    print("[WARN] Could not import deterministic helpers, will skip adding imports")
    HELPERS_AVAILABLE = False

PROHIBITED_IMPORTS: Set[str] = {
    "sys", "os", "time", "datetime", "random", "threading", "asyncio",
}

PROHIBITED_BUILTINS: Set[str] = {"float"}

PROHIBITED_ATTR_CALLS: Set[Tuple[str, str]] = {
    ("sys", "exit"),
    ("time", "time"),
    ("time", "perf_counter"),
    ("random", "random"),
}

# Map prohibited attr calls to project helpers
ATTR_REPLACEMENTS: Dict[Tuple[str, str], str] = {
    ("sys", "exit"): "ZeroSimAbort",          # implemented in your core
    ("time", "time"): "det_time_now",         # deterministic clock
    ("time", "perf_counter"): "det_perf_counter",
    ("random", "random"): "det_random",
}

# Replacement for float(...)
SAFE_FLOAT_FN = "qnum"  # or safe_decimal, etc.


def classify_mode(path: pathlib.Path) -> str:
    parts = path.parts
    if "legacy_root" in parts and "archive" in parts:
        return "legacy"
    if "tests" in parts or "tests_root" in parts:
        return "tests"
    return "core"


class ViolationFixer(ast.NodeTransformer):
    def __init__(self, mode: str):
        self.mode = mode
        self.visit_count = 0
        self.max_visits = 10000  # Prevent infinite recursion
        self.needs_imports = False

    # --- imports ---

    def visit_Import(self, node: ast.Import):
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        node = self.generic_visit(node)
        new_names = [
            n for n in node.names
            if n.name.split(".")[0] not in PROHIBITED_IMPORTS
        ]
        if not new_names:
            return None
        node.names = new_names
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        node = self.generic_visit(node)
        if node.module and node.module.split(".")[0] in PROHIBITED_IMPORTS:
            return None
        return node

    # --- call transformations ---

    def visit_Call(self, node: ast.Call):
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        node = self.generic_visit(node)

        # sys.exit(), time.time(), random.random(), etc.
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            mod = node.func.value.id
            attr = node.func.attr
            key = (mod, attr)

            if key in PROHIBITED_ATTR_CALLS:
                repl = ATTR_REPLACEMENTS.get(key)
                self.needs_imports = True

                # sys.exit -> raise ZeroSimAbort(...)
                if key == ("sys", "exit"):
                    # treat as raising a project-specific fatal exception
                    exc_call = ast.Call(
                        func=ast.Name(id=repl, ctx=ast.Load()),
                        args=node.args,
                        keywords=node.keywords,
                    )
                    return ast.Raise(exc=exc_call, cause=None)

                # deterministic helpers for time/random
                return ast.Call(
                    func=ast.Name(id=repl, ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                )

        # float(...) -> SAFE_FLOAT_FN(...)
        if isinstance(node.func, ast.Name) and node.func.id in PROHIBITED_BUILTINS:
            self.needs_imports = True
            return ast.Call(
                func=ast.Name(id=SAFE_FLOAT_FN, ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords,
            )

        return node


def add_imports_if_needed(source: str, needs_imports: bool) -> str:
    """Add necessary imports to the top of the file if needed"""
    if not needs_imports or not HELPERS_AVAILABLE:
        return source
    
    # Check if imports are already present
    if "from libs.deterministic_helpers import" in source:
        return source
    
    # Add imports after the module docstring if present
    lines = source.split('\n')
    insert_pos = 0
    
    # Find position to insert imports (after module docstring if present)
    if lines and lines[0].startswith('"""') or lines[0].startswith("'''"):
        # Look for end of docstring
        for i, line in enumerate(lines):
            if (line.endswith('"""') or line.endswith("'''")) and i > 0:
                insert_pos = i + 1
                break
    
    # Insert the import statement
    import_line = "from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum"
    lines.insert(insert_pos, import_line)
    
    return '\n'.join(lines)


def transform_file(path: pathlib.Path, dry_run: bool = True) -> bool:
    try:
        src = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[SKIP] unicode decode error in {path}")
        return False
    except Exception as e:
        print(f"[SKIP] read error in {path}: {e}")
        return False
    
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        print(f"[SKIP] syntax error in {path}")
        return False
    except RecursionError:
        print(f"[SKIP] recursion error in {path}")
        return False
    except Exception as e:
        print(f"[SKIP] parse error in {path}: {e}")
        return False
        
    mode = classify_mode(path)
    if mode == "legacy":
        # leave NON_COMPLIANT archives alone
        return False

    try:
        fixer = ViolationFixer(mode=mode)
        new_tree = fixer.visit(tree)
        ast.fix_missing_locations(new_tree)
        
        # Check if we need to add imports
        needs_imports = fixer.needs_imports
    except RecursionError:
        print(f"[SKIP] recursion error processing {path}")
        return False
    except Exception as e:
        print(f"[SKIP] transform error in {path}: {e}")
        return False

    try:
        new_src = ast.unparse(new_tree)  # Python 3.9+
    except Exception as e:
        print(f"[SKIP] unparse failed for {path}: {e}")
        return False

    # Add imports if needed
    if needs_imports:
        new_src = add_imports_if_needed(new_src, needs_imports)

    # sanity: must still compile
    try:
        compile(new_src, str(path), "exec")
    except Exception as e:
        print(f"[SKIP] compile failed after transform {path}: {e}")
        return False

    if dry_run:
        if new_src != src:
            print(f"[DRY] would modify {path}")
        return False

    if new_src != src:
        path.write_text(new_src, encoding="utf-8")
        print(f"[FIX] modified {path}")
        return True

    return False


def main():
    # Process all Python files in the project
    py_files = list(ROOT.rglob("*.py"))
    # Filter out auto-fix scripts themselves to prevent recursion
    py_files = [p for p in py_files if "auto_fix" not in p.name and "simple_auto_fix" not in p.name and "test_auto_fix" not in p.name]
    print(f"[INFO] Found {len(py_files)} Python files to process")
    
    # Process files in batches to avoid memory issues
    batch_size = 100
    total_modified = 0
    
    for i in range(0, len(py_files), batch_size):
        batch = py_files[i:i+batch_size]
        print(f"[INFO] Processing batch {i//batch_size + 1}/{(len(py_files)-1)//batch_size + 1} ({len(batch)} files)")
        
        modified_count = 0
        for p in sorted(batch):
            try:
                if transform_file(p, dry_run=False):
                    modified_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to process {p}: {e}")
                
        total_modified += modified_count
        print(f"[BATCH DONE] Modified {modified_count} files in this batch")
    
    print(f"[DONE] Total modified files: {total_modified}")


if __name__ == "__main__":
    main()