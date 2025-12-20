import sys

sys.path.insert(0, "src")

try:
    print("Attempting to import governance_v18...")
    from api.routes import governance_v18

    print("SUCCESS: governance_v18 imported")
    print(f"Router: {governance_v18.router}")
except Exception as e:
    import traceback

    print("FAILED TO IMPORT governance_v18")
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
