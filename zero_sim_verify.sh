#!/bin/bash
# zero_sim_verify.sh
# QFS V13 Zero-Simulation Compliance Verification Script
# Enforces CIR-302: No non-deterministic operations allowed.

set -e  # Exit immediately if a command exits with a non-zero status.

echo "========================================================"
echo "QFS V13 Zero-Simulation Compliance Verification"
echo "========================================================"

# 1. Run AST Zero-Sim Checker
echo "[STEP 1] Running AST Zero-Sim Checker..."
python3 src/libs/AST_ZeroSimChecker.py
if [ $? -eq 0 ]; then
    echo "✅ AST Check Passed: No forbidden functions or modules detected."
else
    echo "❌ AST Check Failed: Non-deterministic code detected."
    exit 1
fi

# 2. Scan for Forbidden Imports (Grep-based backup)
echo "[STEP 2] Scanning for forbidden imports (backup check)..."
FORBIDDEN_IMPORTS=("import time" "from time" "import random" "from random" "import datetime" "from datetime")
VIOLATIONS=0

for import_pattern in "${FORBIDDEN_IMPORTS[@]}"; do
    # Exclude the checker itself and tests
    grep -r "$import_pattern" src/libs/economics src/core --include="*.py" --exclude="AST_ZeroSimChecker.py" --exclude="*_test.py"
    if [ $? -eq 0 ]; then
        echo "❌ Forbidden import detected: '$import_pattern'"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [ $VIOLATIONS -gt 0 ]; then
    echo "❌ Import Scan Failed: $VIOLATIONS violations found."
    exit 1
else
    echo "✅ Import Scan Passed."
fi

# 3. Verify DeterministicTime Usage
echo "[STEP 3] Verifying DeterministicTime usage..."
# Check if economics modules import DeterministicTime
REQUIRED_IMPORT="from src.libs.DeterministicTime import DeterministicTime"
MODULES=("src/libs/economics/TreasuryDistributionEngine.py" "src/libs/economics/SystemRecoveryProtocol.py" "src/libs/economics/PsiSyncProtocol.py" "src/libs/economics/HoloRewardEngine.py")

for module in "${MODULES[@]}"; do
    if grep -q "DeterministicTime" "$module"; then
        echo "✅ $module uses DeterministicTime."
    else
        echo "❌ $module MISSING DeterministicTime usage."
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [ $VIOLATIONS -gt 0 ]; then
    echo "❌ DeterministicTime Verification Failed."
    exit 1
fi

echo "========================================================"
echo "✅ ALL ZERO-SIMULATION CHECKS PASSED"
echo "========================================================"
exit 0
