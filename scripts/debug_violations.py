import sys
import os

# Add parent directory to path to import analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.zero_sim_analyzer import ViolationAnalyzer, VIOLATION_REGISTRY


def inspect_file(file_path):
    print(f"Inspecting {file_path}...")
    analyzer = ViolationAnalyzer(file_path)
    violations = analyzer.analyze()

    mutation_violations = [v for v in violations if v["type"] == "MUTATION_STATE"]

    print(f"Found {len(mutation_violations)} MUTATION_STATE violations:")
    for v in mutation_violations:
        print(f"  Line {v['line']}: {v['context']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_violations.py <file_path>")
        sys.exit(1)

    inspect_file(sys.argv[1])
