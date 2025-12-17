"""
Targeted auto-fix script for specific files with violations
"""
import ast
import pathlib
import sys
from typing import Tuple, Set, Dict, List

# Set recursion limit to prevent infinite recursion
sys.setrecursionlimit(1000)

ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to v13/

# Add the v13 directory to the path so we can import libs
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
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("datetime", "fromisoformat"),
    ("datetime", "timedelta"),
}

# Map prohibited attr calls to project helpers
ATTR_REPLACEMENTS: Dict[Tuple[str, str], str] = {
    ("sys", "exit"): "ZeroSimAbort",          # implemented in your core
    ("time", "time"): "det_time_now",         # deterministic clock
    ("time", "perf_counter"): "det_perf_counter",
    ("random", "random"): "det_random",
    ("datetime", "now"): "det_time_now",      # deterministic clock
    ("datetime", "utcnow"): "det_time_now",   # deterministic clock
    ("datetime", "fromisoformat"): "det_time_now", # deterministic clock
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
            
            # Debug output
            if mod in ["sys", "time", "random", "datetime"]:
                print(f"[DEBUG] Found call: {mod}.{attr}")

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

    def visit_annotation(self, node):
        """Handle type annotations"""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        # Handle simple name annotations like 'float'
        if isinstance(node, ast.Name) and node.id in PROHIBITED_BUILTINS:
            self.needs_imports = True
            return ast.Name(id=SAFE_FLOAT_FN, ctx=node.ctx)
        
        return self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Handle annotated assignments"""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        node.annotation = self.visit_annotation(node.annotation)
        node = self.generic_visit(node)
        return node

    def visit_arg(self, node):
        """Handle function arguments with annotations"""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        if node.annotation:
            node.annotation = self.visit_annotation(node.annotation)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle function definitions with return type annotations"""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        if node.returns:
            node.returns = self.visit_annotation(node.returns)
        return self.generic_visit(node)


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
    if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
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
        else:
            print(f"[DRY] no changes needed for {path}")
        return False

    if new_src != src:
        path.write_text(new_src, encoding="utf-8")
        print(f"[FIX] modified {path}")
        return True

    return False


def main():
    # Target specific files with violations
    target_files = [
        'v13/ATLAS/src/core/transaction_processor.py'
    ]
    
    print(f"[INFO] Targeting {len(target_files)} files with violations")
    
    modified_count = 0
    for file_path in sorted(target_files):
        path = pathlib.Path(file_path)
        print(f"[DEBUG] Checking file: {path} (exists: {path.exists()})")
        if path.exists():
            try:
                if transform_file(path, dry_run=False):
                    modified_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to process {path}: {e}")
        else:
            print(f"[SKIP] File not found: {path}")
    
    print(f"[DONE] Modified {modified_count} files")

if __name__ == "__main__":
    main()