import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

print("DEBUG: Starting Import Test")
try:
    from v15.atlas.governance.ProposalEngine import ProposalEngine

    print("✅ ProposalEngine Imported Successfully")

    eng = ProposalEngine()
    print(f"✅ ProposalEngine Instantiated: {eng}")

except Exception as e:
    print(f"❌ Import Failed: {e}")
    import traceback

    traceback.print_exc()
