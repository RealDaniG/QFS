import ast

# Test the AST checker on CertifiedMath.py
with open("libs/CertifiedMath.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

# Check for global nodes
for node in ast.walk(tree):
    if isinstance(node, ast.Global):
        print(f"Found global at line {node.lineno}: {node.names}")