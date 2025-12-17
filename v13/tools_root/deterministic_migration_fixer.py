"""
deterministic_migration_fixer.py - AST-Based Deterministic Migration Tool for QFS V13

Implements the deterministic math and float migration plan with AST-based transformations.
Handles float → QAmount, time/random → deterministic equivalents, and sys.exit → typed exceptions.
"""

import ast
import pathlib
import sys
from typing import Tuple, Set, Dict, List, Optional

# Set recursion limit to prevent infinite recursion
sys.setrecursionlimit(1000)

ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to v13/

# Add the v13 directory to the path so we can import libs
sys.path.append(str(ROOT))

try:
    from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
    from libs.fatal_errors import EconomicInvariantBreach, GovernanceGuardFailure
    HELPERS_AVAILABLE = True
except ImportError:
    print("[WARN] Could not import deterministic helpers, will skip adding imports")
    HELPERS_AVAILABLE = False

# Target directories for migration
TARGET_DIRS = {
    'libs/economics',
    'libs/governance', 
    'libs/encoding',
    'ATLAS/src/core',
    'ATLAS/src/models',
    'ATLAS/src/api/routes',
    'ATLAS/src/p2p',
    'ATLAS/src/signals'
}

# Excluded directories
EXCLUDED_DIRS = {
    'legacy_root/archive/legacy',
    'legacy_root/tests_root'
}

# Prohibited imports that should be removed
PROHIBITED_IMPORTS: Set[str] = {
    "sys", "os", "time", "datetime", "random", "threading", "asyncio",
}

# Prohibited built-ins that should be replaced
PROHIBITED_BUILTINS: Set[str] = {"float"}

# Prohibited attribute calls that should be replaced
PROHIBITED_ATTR_CALLS: Set[Tuple[str, str]] = {
    ("sys", "exit"),
    ("time", "time"),
    ("time", "perf_counter"),
    ("random", "random"),
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("datetime", "fromisoformat"),
}

# Map prohibited attribute calls to deterministic equivalents
ATTR_REPLACEMENTS: Dict[Tuple[str, str], str] = {
    ("sys", "exit"): "ZeroSimAbort",          # typed fatal error
    ("time", "time"): "det_time_now",         # deterministic time
    ("time", "perf_counter"): "det_perf_counter",
    ("random", "random"): "det_random",       # deterministic random
    ("datetime", "now"): "det_time_now",      # deterministic time
    ("datetime", "utcnow"): "det_time_now",   # deterministic time
    ("datetime", "fromisoformat"): "det_time_now", # deterministic time
}

# Replacement for float(...)
SAFE_FLOAT_FN = "qnum"  # or QAmount, depending on context

# Deterministic helper functions that should be imported
DETERMINISTIC_HELPERS = {
    "ZeroSimAbort", "det_time_now", "det_perf_counter", 
    "det_random", "det_time_isoformat", "qnum"
}

def classify_mode(path: pathlib.Path) -> str:
    """
    Classify a file path into migration mode.
    
    Returns:
        str: "target" for files in target directories, "excluded" for legacy files, "other" for everything else
    """
    parts = path.parts
    
    # Check if in excluded directories
    if any(excluded_dir in str(path) for excluded_dir in EXCLUDED_DIRS):
        return "excluded"
    
    # Check if in target directories
    path_str = str(path).replace('\\', '/')
    for target_dir in sorted(TARGET_DIRS):
        if target_dir in path_str:
            return "target"
    
    return "other"

def should_process_file(path: pathlib.Path) -> bool:
    """
    Determine if a file should be processed based on migration plan.
    
    Returns:
        bool: True if file should be processed, False otherwise
    """
    mode = classify_mode(path)
    return mode == "target"

class DeterministicMigrationFixer(ast.NodeTransformer):
    """
    AST transformer that implements the deterministic migration plan.
    
    Handles:
    - Removal of prohibited imports
    - Replacement of prohibited function calls with deterministic equivalents
    - Replacement of float() calls with qnum()
    - Replacement of sys.exit() with typed exceptions
    """
    
    def __init__(self, mode: str):
        self.mode = mode
        self.visit_count = 0
        self.max_visits = 10000  # Prevent infinite recursion
        self.needs_imports = False
        self.changes_made = []

    # --- Import handling ---

    def visit_Import(self, node: ast.Import):
        """Remove prohibited imports."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        node = self.generic_visit(node)
        new_names = [
            n for n in node.names
            if n.name.split(".")[0] not in PROHIBITED_IMPORTS
        ]
        
        if not new_names:
            self.changes_made.append(f"Removed prohibited import: {', '.join([n.name for n in node.names])}")
            return None
            
        if len(new_names) != len(node.names):
            removed = [n.name for n in node.names if n not in new_names]
            self.changes_made.append(f"Removed prohibited imports: {', '.join(removed)}")
            
        node.names = new_names
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Remove prohibited from-imports."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        node = self.generic_visit(node)
        if node.module and node.module.split(".")[0] in PROHIBITED_IMPORTS:
            self.changes_made.append(f"Removed prohibited from-import: {node.module}")
            return None
        return node

    # --- Call transformations ---

    def visit_Call(self, node: ast.Call):
        """Transform prohibited function calls."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        # Visit children first
        node = self.generic_visit(node)

        # Handle attribute calls like time.time(), random.random(), sys.exit(), etc.
        if isinstance(node.func, ast.Attribute):
            # Debug output for all attribute calls
            # print(f"Attribute call: {ast.dump(node.func, indent=2)}")
            
            # Check for chained calls like datetime.now().isoformat()
            if (isinstance(node.func.value, ast.Call) and 
                isinstance(node.func.value.func, ast.Attribute) and 
                isinstance(node.func.value.func.value, ast.Name)):
                # This is a chained call like datetime.now().isoformat()
                inner_mod = node.func.value.func.value.id
                inner_attr = node.func.value.func.attr
                outer_attr = node.func.attr
                
                # Debug output
                # print(f"Chained call detected: {inner_mod}.{inner_attr}(...).{outer_attr}()")
                
                # Check if this is datetime.now(...).isoformat() or datetime.utcnow(...).isoformat()
                if (inner_mod == "datetime" and 
                    inner_attr in ["now", "utcnow"] and 
                    outer_attr == "isoformat"):
                    self.changes_made.append(f"Replaced {inner_mod}.{inner_attr}(...).{outer_attr}() with det_time_isoformat()")
                    # Replace with det_time_isoformat() which returns the ISO format string directly
                    iso_call = ast.Call(
                        func=ast.Name(id="det_time_isoformat", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    )
                    self.needs_imports = True
                    return iso_call
            
            # Handle regular attribute calls
            elif isinstance(node.func.value, ast.Name):
                mod = node.func.value.id
                attr = node.func.attr
                key = (mod, attr)

                if key in PROHIBITED_ATTR_CALLS:
                    repl = ATTR_REPLACEMENTS.get(key)
                    self.needs_imports = True
                    
                    # Special handling for sys.exit -> raise exception
                    if key == ("sys", "exit"):
                        self.changes_made.append(f"Replaced sys.exit() with raise {repl}()")
                        # Transform to raise exception
                        exc_call = ast.Call(
                            func=ast.Name(id=repl, ctx=ast.Load()),
                            args=node.args,
                            keywords=node.keywords,
                        )
                        return ast.Raise(exc=exc_call, cause=None)

                    # Special handling for datetime calls that need ISO format
                    if key in [("datetime", "now"), ("datetime", "utcnow")]:
                        self.changes_made.append(f"Replaced {mod}.{attr}() with det_time_isoformat()")
                        # Replace with det_time_isoformat() which returns the ISO format string directly
                        iso_call = ast.Call(
                            func=ast.Name(id="det_time_isoformat", ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        )
                        self.needs_imports = True
                        return iso_call
                    
                    # Standard replacements for time/random functions
                    # For datetime functions, we don't want to pass arguments
                    if mod in ["datetime"]:
                        self.changes_made.append(f"Replaced {mod}.{attr}() with {repl}()")
                        return ast.Call(
                            func=ast.Name(id=repl, ctx=ast.Load()),
                            args=[],  # No arguments for deterministic time functions
                            keywords=[],
                        )
                    else:
                        self.changes_made.append(f"Replaced {mod}.{attr}() with {repl}()")
                        return ast.Call(
                            func=ast.Name(id=repl, ctx=ast.Load()),
                            args=node.args,
                            keywords=node.keywords,
                        )
            
            # Special case: Check for .isoformat() calls on det_time_isoformat() calls
            # This handles cases where we've already replaced datetime.now() with det_time_isoformat()
            # but there's still a .isoformat() call left
            elif (isinstance(node.func.value, ast.Call) and
                  isinstance(node.func.value.func, ast.Name) and
                  node.func.value.func.id == "det_time_isoformat" and
                  node.func.attr == "isoformat"):
                # This is a call like det_time_isoformat().isoformat()
                # Since det_time_isoformat() already returns an ISO format string, we can just return
                # the det_time_isoformat() call directly
                self.changes_made.append("Removed redundant .isoformat() call on det_time_isoformat()")
                return node.func.value

        # Handle built-in calls like float()
        if isinstance(node.func, ast.Name) and node.func.id in PROHIBITED_BUILTINS:
            self.needs_imports = True
            self.changes_made.append(f"Replaced {node.func.id}() with {SAFE_FLOAT_FN}()")
            return ast.Call(
                func=ast.Name(id=SAFE_FLOAT_FN, ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords,
            )
        
        # Handle deterministic helper functions that might be missing from imports
        if isinstance(node.func, ast.Name) and node.func.id in DETERMINISTIC_HELPERS:
            self.needs_imports = True
            # We don't need to change the call, just ensure the import is present
            self.changes_made.append(f"Using deterministic helper: {node.func.id}")

        return node

    # --- Annotation handling ---

    def visit_annotation(self, node):
        """Handle type annotations."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        # Handle simple name annotations like 'float'
        if isinstance(node, ast.Name) and node.id in PROHIBITED_BUILTINS:
            self.needs_imports = True
            self.changes_made.append(f"Replaced type annotation '{node.id}' with 'QAmount'")
            return ast.Name(id="QAmount", ctx=node.ctx)
        
        return self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Handle annotated assignments."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        if node.annotation:
            node.annotation = self.visit_annotation(node.annotation)
        node = self.generic_visit(node)
        return node

    def visit_arg(self, node):
        """Handle function arguments with annotations."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        if node.annotation:
            node.annotation = self.visit_annotation(node.annotation)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle function definitions with return type annotations."""
        if self.visit_count >= self.max_visits:
            return node
        self.visit_count += 1
        
        if node.returns:
            node.returns = self.visit_annotation(node.returns)
        
        # Visit the function body
        node = self.generic_visit(node)
        
        # Special handling for get_balance method - fix the docstring return type
        if node.name == "get_balance":
            # Look for the docstring in the function body
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                # This is the docstring
                docstring = node.body[0].value.value
                # Replace "Returns:\n            float:" with "Returns:\n            QAmount:"
                if "Returns:\n" in docstring and "float:" in docstring:
                    new_docstring = docstring.replace("float:", "QAmount:")
                    node.body[0].value.value = new_docstring
                    self.changes_made.append("Fixed get_balance docstring return type")
            
            # Also look for assignments to fix balance initialization
            for stmt in sorted(node.body):
                if (isinstance(stmt, ast.Assign) and 
                    len(stmt.targets) == 1 and 
                    isinstance(stmt.targets[0], ast.Name) and 
                    stmt.targets[0].id == "balance"):
                    # Found balance assignment, check if it's initialized as 0.0
                    if (isinstance(stmt.value, ast.Constant) and 
                        isinstance(stmt.value.value, float) and 
                        stmt.value.value == 0):
                        # Replace with QAmount(0)
                        stmt.value = ast.Call(
                            func=ast.Name(id="QAmount", ctx=ast.Load()),
                            args=[ast.Constant(value=0)],
                            keywords=[]
                        )
                        self.changes_made.append("Fixed balance initialization to QAmount(0)")
        
        return node

def add_imports_if_needed(source: str, needs_imports: bool, changes_made: List[str]) -> str:
    """
    Add necessary imports to the top of the file if needed.
    
    Args:
        source: Original source code
        needs_imports: Whether imports are needed
        changes_made: List of changes made (to determine what imports are needed)
        
    Returns:
        str: Source code with necessary imports added
    """
    if not needs_imports or not HELPERS_AVAILABLE:
        return source
    
    # Check what imports are already present
    lines = source.split('\n')
    
    # Determine what imports we need based on changes made
    imports_needed = set()
    
    # Check for QAmount usage
    if any("QAmount" in change for change in changes_made):
        imports_needed.add("from libs.economics.QAmount import QAmount")
    
    # Check for deterministic helpers usage
    if any("deterministic helper" in change or "det_" in change or "qnum" in change for change in changes_made):
        imports_needed.add("from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum")
    
    # Check for fatal error usage
    if any("ZeroSimAbort" in change for change in changes_made):
        imports_needed.add("from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure")
    
    # Check if imports are already present and need to be updated
    existing_import_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            existing_import_lines.append((i, line.strip()))
    
    # Track which imports we've already seen to detect duplicates
    seen_imports = set()
    lines_to_remove = []
    
    # First pass: Identify and mark duplicate imports for removal
    for i, existing_line in sorted(existing_import_lines):
        if existing_line in seen_imports:
            lines_to_remove.append(i)
        else:
            seen_imports.add(existing_line)
    
    # Remove duplicate lines (in reverse order to maintain indices)
    for i in sorted(lines_to_remove, reverse=True):
        lines.pop(i)
        # Adjust indices of remaining import lines
        existing_import_lines = [(idx-1, line) if idx > i else (idx, line) for idx, line in existing_import_lines]
    
    # Refresh existing_import_lines after removing duplicates
    existing_import_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            existing_import_lines.append((i, line.strip()))
    
    # Reset seen_imports for the next phase
    seen_imports = set(line for _, line in existing_import_lines)
    
    # Check for partial matches and update existing imports
    updated_lines = set()
    for i, existing_line in sorted(existing_import_lines):
        # Check if this is a deterministic helpers import that needs to be expanded
        if "from libs.deterministic_helpers import" in existing_line:
            # Check if it's missing any of the required functions
            required_functions = {"ZeroSimAbort", "det_time_now", "det_perf_counter", "det_random", "det_time_isoformat", "qnum"}
            existing_functions = set(existing_line.replace("from libs.deterministic_helpers import ", "").split(", "))
            missing_functions = required_functions - existing_functions
            
            if missing_functions:
                # Update the existing import line
                all_functions = existing_functions | required_functions
                function_list = sorted(list(all_functions))
                new_import_line = "from libs.deterministic_helpers import " + ", ".join(function_list)
                lines[i] = new_import_line
                updated_lines.add(i)
                seen_imports.discard(existing_line)
                seen_imports.add(new_import_line)
        # Check if this is a QAmount import that's already present
        elif "from libs.economics.QAmount import QAmount" in existing_line:
            # Remove this from imports_needed since it's already present
            imports_needed.discard("from libs.economics.QAmount import QAmount")
        # Check if this is a fatal errors import that's already present
        elif "from libs.fatal_errors import ZeroSimAbort" in existing_line:
            # Remove this from imports_needed since it's already present
            imports_needed.discard("from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure")
    
    # Filter out imports that are already present or updated
    new_imports = set()
    for import_needed in sorted(imports_needed):
        # Skip deterministic helpers import if we already updated an existing one
        if "from libs.deterministic_helpers import" in import_needed:
            # Check if we already have a deterministic helpers import
            has_deterministic_import = any("from libs.deterministic_helpers import" in line for _, line in existing_import_lines)
            if has_deterministic_import and any(i in updated_lines for i, _ in existing_import_lines if "from libs.deterministic_helpers import" in _):
                continue
        # Only add if not already present
        if import_needed not in seen_imports:
            new_imports.add(import_needed)
    
    if not new_imports:
        return '\n'.join(lines)
    
    # Add imports at the top of the file, after any module docstring and __future__ imports
    insert_pos = 0
    
    # Find position to insert imports (after module docstring and __future__ imports if present)
    # First check for module docstring
    if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
        # Look for end of docstring
        for i, line in enumerate(lines):
            if (line.endswith('"""') or line.endswith("'''")) and i > 0:
                insert_pos = i + 1
                break
        # Special case: if the docstring is on a single line, we need to adjust
        if lines[0].count('"""') == 2 or lines[0].count("'''") == 2:
            insert_pos = 1
    
    # Then check for __future__ imports and place after them
    future_import_end = insert_pos
    for i in range(insert_pos, len(lines)):
        line = lines[i].strip()
        if line.startswith("from __future__ import"):
            future_import_end = i + 1
        elif line and not line.startswith("#") and not line.startswith("from __future__ import"):
            # Stop at first non-future, non-comment, non-empty line
            break
    
    insert_pos = max(insert_pos, future_import_end)
    
    # Insert the import statements
    import_lines = list(new_imports)
    for import_line in reversed(import_lines):
        lines.insert(insert_pos, import_line)
    
    # Fix any misplaced imports in docstrings
    for i, line in enumerate(lines):
        if line.strip().startswith('"""from ') or line.strip().startswith("'''from "):
            # This looks like an import that got placed in a docstring
            # Move it to the appropriate position
            import_line = line.strip()[3:]  # Remove the leading quotes
            if import_line.endswith('"""') or import_line.endswith("'''"):
                import_line = import_line[:-3]  # Remove the trailing quotes
            lines.pop(i)
            lines.insert(insert_pos, import_line)
    
    return '\n'.join(lines)
def transform_file(path: pathlib.Path, dry_run: bool = True) -> bool:
    """
    Transform a single file to comply with deterministic migration plan.
    
    Args:
        path: Path to the file to transform
        dry_run: If True, only report what would be changed without modifying the file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
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
    if mode == "excluded":
        # Leave NON_COMPLIANT archives alone
        return False

    if not should_process_file(path):
        return False

    try:
        fixer = DeterministicMigrationFixer(mode=mode)
        new_tree = fixer.visit(tree)
        ast.fix_missing_locations(new_tree)
        
        # Check if we need to add imports
        needs_imports = fixer.needs_imports
        changes_made = fixer.changes_made
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
    if needs_imports and changes_made:
        new_src = add_imports_if_needed(new_src, needs_imports, changes_made)

    # Sanity check: must still compile
    try:
        compile(new_src, str(path), "exec")
    except Exception as e:
        print(f"[SKIP] compile failed after transform {path}: {e}")
        return False

    if dry_run:
        if new_src != src:
            print(f"[DRY] would modify {path}")
            if changes_made:
                print(f"      Changes: {', '.join(changes_made)}")
        return False

    if new_src != src:
        path.write_text(new_src, encoding="utf-8")
        print(f"[FIX] modified {path}")
        if changes_made:
            print(f"      Changes: {', '.join(changes_made)}")
        return True

    return False

def find_target_files() -> List[pathlib.Path]:
    """
    Find all Python files in target directories.
    
    Returns:
        List[pathlib.Path]: List of Python files to process
    """
    target_files = []
    
    for target_dir in sorted(TARGET_DIRS):
        dir_path = ROOT / target_dir
        if dir_path.exists():
            target_files.extend(dir_path.rglob("*.py"))
    
    # Filter out auto-fix scripts themselves
    exclude_patterns = ["auto_fix", "migration_fixer", "ast_checker"]
    target_files = [
        f for f in target_files 
        if not any(pattern in f.name for pattern in exclude_patterns)
    ]
    
    return target_files

def main():
    """Main function to run the deterministic migration fixer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deterministic Migration Fixer for QFS V13")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--target-file", help="Process only a specific file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    
    args = parser.parse_args()
    
    if args.target_file:
        # Process single file
        path = pathlib.Path(args.target_file)
        if path.exists():
            print(f"[INFO] Processing single file: {path}")
            transform_file(path, dry_run=args.dry_run)
        else:
            print(f"[ERROR] File not found: {path}")
            return 1
    else:
        # Process all target files
        target_files = find_target_files()
        print(f"[INFO] Found {len(target_files)} target files to process")
        
        if args.verbose:
            print("[INFO] Target files:")
            for f in sorted(target_files):
                print(f"  {f}")
        
        modified_count = 0
        for path in sorted(target_files):
            try:
                if transform_file(path, dry_run=args.dry_run):
                    modified_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to process {path}: {e}")
        
        print(f"[DONE] Modified {modified_count} files")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())   