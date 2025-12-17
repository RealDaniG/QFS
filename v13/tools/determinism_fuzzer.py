import json
import logging
from typing import List, Dict, Any
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeterminismFuzzer:
    def __init__(self, seed: int = 1234567890):
        self.seed = seed
        self.cm = CertifiedMath()

    def _generate_test_inputs(self, num_tests: int) -> List[Dict[str, Any]]:
        """Generate deterministic test inputs using counter-based PRNG."""
        inputs = []
        counter = self.seed
        for _ in range(num_tests):
            # Using bitwise shift for power of 2 for AST compliance
            val1 = (counter * 1664525 + 1013904223) % (1 << 32)
            counter += 1
            val2 = (counter * 1664525 + 1013904223) % (1 << 32)
            counter += 1
            inputs.append(
                {
                    "a": BigNum128(val1),
                    "b": BigNum128(val2),
                    "iterations": 5 + counter % 6,
                }
            )
        return inputs

    def run_fuzz_test(self, num_tests: int = 100000) -> str:
        """Run fuzz test and return deterministic SHA-256 hash of all outputs."""
        log_list = []
        inputs = self._generate_test_inputs(num_tests)
        for test in sorted(inputs):
            # unused variables are expected here as we are testing the math engine stability
            _exp = self.cm.exp(test["a"], test["iterations"], log_list)
            _ln = self.cm.ln(
                test["a"] if test["a"].value > 0 else BigNum128(1),
                test["iterations"],
                log_list,
            )
            _sin = self.cm.sin(test["a"], test["iterations"], log_list)
            _add = self.cm.add(test["a"], test["b"], log_list)
        return self.cm.get_log_hash(log_list)

    def compare_with_reference(
        self, reference_hash: str, num_tests: int = 100000
    ) -> bool:
        """Compare against known-good hash from reference runtime."""
        actual_hash = self.run_fuzz_test(num_tests)
        return actual_hash == reference_hash


def test_determinism_fuzzer():
    """Test the DeterminismFuzzer implementation."""
    logger.info("Testing DeterminismFuzzer...")
    fuzzer = DeterminismFuzzer()
    test_hash = fuzzer.run_fuzz_test(1000)
    logger.info(f"Test hash (1000 ops): {test_hash}")
    is_same = fuzzer.compare_with_reference(test_hash, 1000)
    logger.info(f"Self-comparison: {is_same}")
    logger.info("✓ DeterminismFuzzer test completed!")


def main():
    """Main function to run the DeterminismFuzzer with command-line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="QFS V13.5 Determinism Fuzzer")
    parser.add_argument(
        "--mode",
        choices=["dev", "pre-release", "release"],
        default="dev",
        help="Audit mode (default: dev)",
    )
    parser.add_argument(
        "--runtime", default="python", help="Target runtime (default: python)"
    )
    parser.add_argument("--runs", type=int, help="Number of operations to run")
    parser.add_argument("--out", help="Output file path")
    parser.add_argument(
        "--test_mode",
        choices=["true", "false"],
        default="false",
        help="Test mode (default: false)",
    )
    args = parser.parse_args()
    if args.runs is None:
        if args.mode == "dev":
            runs = 5000
        elif args.mode == "pre-release":
            runs = 25000
        elif args.mode == "release":
            runs = 100000
        else:
            runs = 1000
    else:
        runs = args.runs

    logger.info(
        f"Running Determinism Fuzzer - Mode: {args.mode}, Runtime: {args.runtime}, Runs: {runs}"
    )
    fuzzer = DeterminismFuzzer()
    hash_result = fuzzer.run_fuzz_test(runs)
    result = {
        "runtime": args.runtime,
        "mode": args.mode,
        "runs": runs,
        "hash": hash_result,
    }

    if args.out:
        # Use simple open, tools are allowed to write results
        with open(args.out, "w") as f:
            json.dump(result, f)
        logger.info(f"Results saved to {args.out}")
    else:
        logger.info(f"Hash: {hash_result}")
    return hash_result


if __name__ == "__main__":
    main()
