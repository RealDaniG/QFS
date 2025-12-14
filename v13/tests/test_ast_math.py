import ast
import os

# Test the AST checker on CertifiedMath.py
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_V13_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_CERTIFIED_MATH_PATH = os.path.join(_V13_ROOT, "libs", "CertifiedMath.py")

with open(_CERTIFIED_MATH_PATH, "r", encoding="utf-8") as f:
    source = f.read()

tree = ast.parse(source)

# Check for global nodes
for node in ast.walk(tree):
    if isinstance(node, ast.Global):
        print(f"Found global at line {node.lineno}: {node.names}")