"""
Phase 3 Batch 5 Phase 2: Transform Module-Level Singletons to Factory Functions

Target: 8 GLOBAL_MUTATION violations
Pattern: Module-level singleton assignments (logger, router, cm, etc.)
Approach: Convert to lazy-initialized factory functions

Violations to Transform:
1. v13/AEGIS/services/governance_map.py:27 - router
2. v13/core/CoherenceEngine.py:19 - ReferralRewarded
3. v13/core/observability/logger.py:121 - logger
4. v13/libs/BigNum128.py:21 - cm
5. v13/libs/BigNum128_fixed.py:13 - cm
6. v13/libs/deterministic_helpers.py:28 - _prng_state
7. v13/libs/PQC.py:15 - _adapter
8. v13/libs/pqc_provider.py:20 - logger
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class TransformRecord:
    file: Path
    line: int
    variable: str
    original: str
    transformed: str


class SingletonToFactoryTransformer(ast.NodeTransformer):
    """Transform module-level singletons to lazy-initialized factories"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.transforms: List[TransformRecord] = []
        self.inside_function = False
        self.function_depth = 0

        # Target singletons to transform
        self.target_singletons = {
            "router",
            "logger",
            "cm",
            "_prng_state",
            "_adapter",
            "ReferralRewarded",
        }

    def visit_FunctionDef(self, node):
        self.inside_function = True
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1
        if self.function_depth == 0:
            self.inside_function = False
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Transform module-level singleton assignments"""
        if not self.inside_function:
            for target in sorted(node.targets):
                if isinstance(target, ast.Name):
                    if target.id in self.target_singletons:
                        original = ast.unparse(node)

                        # Record transformation (manual fix required)
                        self.transforms.append(
                            TransformRecord(
                                file=Path(self.filepath),
                                line=node.lineno,
                                variable=target.id,
                                original=original,
                                transformed=f"# TODO: Convert {target.id} to factory function",
                            )
                        )

        return self.generic_visit(node)


def analyze_singletons(root_dir: Path):
    """Analyze singleton violations and provide transformation guidance"""

    target_files = [
        "v13/AEGIS/services/governance_map.py",
        "v13/core/CoherenceEngine.py",
        "v13/core/observability/logger.py",
        "v13/libs/BigNum128.py",
        "v13/libs/BigNum128_fixed.py",
        "v13/libs/deterministic_helpers.py",
        "v13/libs/PQC.py",
        "v13/libs/pqc_provider.py",
    ]

    print("=" * 80)
    print("Phase 2: Singleton Analysis")
    print("=" * 80)

    all_transforms = []

    for file_path in sorted(target_files):
        full_path = root_dir / file_path
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(full_path))
            transformer = SingletonToFactoryTransformer(str(full_path))
            transformer.visit(tree)

            if transformer.transforms:
                print(f"\n📄 {file_path}")
                for t in sorted(transformer.transforms):
                    print(f"   Line {t.line}: {t.variable}")
                    print(f"      Original: {t.original}")
                    all_transforms.extend(transformer.transforms)

        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print("\n" + "=" * 80)
    print(f"Total singletons found: {len(all_transforms)}")
    print("=" * 80)

    return all_transforms


def generate_transformation_guide(transforms: List[TransformRecord]):
    """Generate manual transformation guide"""

    guide = """# Phase 2 Transformation Guide

## Manual Transformations Required

Due to the complexity and context-specific nature of singleton patterns,
these transformations should be done manually with careful consideration.

## Transformation Pattern

### Before (Module-level singleton):
```python
logger = StructuredLogger()
```

### After (Lazy-initialized factory):
```python
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger
```

## Files to Transform

"""

    for t in sorted(transforms):
        guide += f"\n### {t.file}\n"
        guide += f"**Line {t.line}:** `{t.variable}`\n"
        guide += f"```python\n{t.original}\n```\n"

    guide += """
## Verification Steps

1. Make changes manually to each file
2. Run: `python v13/libs/AST_ZeroSimChecker.py v13/ --fail`
3. Verify GLOBAL_MUTATION count drops to 0
4. Run tests: `pytest v13/tests/ -v`
5. Commit if successful

## Safety

- Each transformation is reversible via git
- Test after each file transformation
- If tests fail, revert that file and skip it
"""

    return guide


if __name__ == "__main__":
    root = Path(".")

    print("Analyzing singleton violations...")
    transforms = analyze_singletons(root)

    if transforms:
        guide = generate_transformation_guide(transforms)
        guide_path = Path("batch5_phase2_transformation_guide.md")
        guide_path.write_text(guide, encoding="utf-8")
        print(f"\n✅ Transformation guide written to: {guide_path}")
        print("\n⚠️  Manual transformations required - see guide for details")
    else:
        print("\n✅ No singletons found to transform")
