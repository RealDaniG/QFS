#!/bin/bash

# QFS V13.5 - Determinism Fuzzer Runner
# Runs the DeterminismFuzzer with specified parameters

set -e

# Default values
MODE="dev"
RUNTIME="python"
RUNS=5000
OUT="evidence/phase2/df_python.jsonl"
TEST_MODE="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --runtime)
            RUNTIME="$2"
            shift 2
            ;;
        --runs)
            RUNS="$2"
            shift 2
            ;;
        --out)
            OUT="$2"
            shift 2
            ;;
        --test_mode)
            TEST_MODE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set runs based on mode if not explicitly set
if [[ "$MODE" == "dev" ]]; then
    RUNS=${RUNS:-5000}
elif [[ "$MODE" == "pre-release" ]]; then
    RUNS=${RUNS:-25000}
elif [[ "$MODE" == "release" ]]; then
    RUNS=${RUNS:-100000}
fi

echo "Running Determinism Fuzzer - Mode: $MODE, Runtime: $RUNTIME, Runs: $RUNS"

# Create evidence directory
mkdir -p "$(dirname "$OUT")"

# Run the fuzzer based on runtime
if [[ "$RUNTIME" == "python" ]]; then
    # Run Python fuzzer
    cd src/tools
    if [[ "$TEST_MODE" == "true" ]]; then
        python -c "
import sys
sys.path.insert(0, '../..')
from determinism_fuzzer import DeterminismFuzzer
fuzzer = DeterminismFuzzer()
hash_result = fuzzer.run_fuzz_test($RUNS)
import json
result = {
    'runtime': 'python',
    'mode': '$MODE',
    'runs': $RUNS,
    'hash': hash_result
}
with open('../../$OUT', 'w') as f:
    json.dump(result, f)
print('Python fuzzer completed. Hash:', hash_result)
"
    else
        python -c "
import sys
sys.path.insert(0, '../..')
from determinism_fuzzer import DeterminismFuzzer
fuzzer = DeterminismFuzzer()
hash_result = fuzzer.run_fuzz_test($RUNS)
import json
result = {
    'runtime': 'python',
    'mode': '$MODE',
    'runs': $RUNS,
    'hash': hash_result
}
with open('../../$OUT', 'w') as f:
    json.dump(result, f)
print('Python fuzzer completed. Hash:', hash_result)
"
    fi
    cd ../..
elif [[ "$RUNTIME" == "node" ]]; then
    # Placeholder for Node.js fuzzer
    echo "Node.js fuzzer not implemented yet" > "$OUT"
elif [[ "$RUNTIME" == "rust" ]]; then
    # Placeholder for Rust fuzzer
    echo "Rust fuzzer not implemented yet" > "$OUT"
fi

# Also generate SHA256 checksums file
echo "Generating SHA256 checksums..."
cd evidence/phase2
sha256sum df_python.jsonl > df_sha256s.txt 2>/dev/null || true
cd ../..

echo "Determinism Fuzzer completed."