import ast

# Test the AST checker on PQC.py
with open("libs/PQC.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

# Check for global nodes
for node in ast.walk(tree):
    if isinstance(node, ast.Global):
        print(f"Found global at line {node.lineno}: {node.names}")