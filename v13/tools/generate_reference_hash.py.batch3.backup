"""
Generate the canonical reference hash for Determinism Fuzzer.
This script generates the reference hash that will be used to verify cross-runtime determinism.
"""

from pathlib import Path
from tools.determinism_fuzzer import DeterminismFuzzer


def generate_reference_hash():
    """Generate the canonical reference hash for 100k operations."""
    print("Generating reference hash for Determinism Fuzzer...")
    fuzzer = DeterminismFuzzer(seed=1234567890)
    reference_hash = fuzzer.run_fuzz_test(100000)

    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    with open("evidence/phase2_fuzzer_ref.sha256", "w") as f:
        f.write(reference_hash)
    print(f"Reference hash generated and saved: {reference_hash}")
    return reference_hash


if __name__ == "__main__":
    generate_reference_hash()
