import ast
import pathlib
import sys
from typing import Tuple, Set, Dict

# Set recursion limit to prevent infinite recursion
sys.setrecursionlimit(1000)

ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to v13/
# Import our deterministic helper functions
sys.path.append(str(ROOT))
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
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
            return ast.Call(
                func=ast.Name(id=SAFE_FLOAT_FN, ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords,
            )

        return node

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
    mode = classify_mode(path)
    if mode == "legacy":
        # leave NON_COMPLIANT archives alone
        return False

    fixer = ViolationFixer(mode=mode)
    new_tree = fixer.visit(tree)
    ast.fix_missing_locations(new_tree)

    try:
        new_src = ast.unparse(new_tree)  # Python 3.9+
    except Exception as e:
        print(f"[SKIP] unparse failed for {path}: {e}")
        return False

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
    py_files = list(ROOT.rglob("*.py"))
    # Filter out the auto_fix_violations.py file itself to prevent recursion
    py_files = [p for p in py_files if p.name != "auto_fix_violations.py"]
    print(f"[INFO] Found {len(py_files)} Python files to process")
    for p in py_files:
        transform_file(p, dry_run=True)  # Dry run by default
if __name__ == "__main__":
    main()