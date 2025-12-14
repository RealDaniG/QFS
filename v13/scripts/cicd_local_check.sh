#!/bin/bash
# QFS V13 Local CI/CD Check Script

echo "Running Local CI/CD Checks..."

# Run Zero-Simulation compliance check
echo "1. Running Zero-Simulation Compliance Check..."
python src/libs/AST_ZeroSimChecker.py
if [ $? -ne 0 ]; then
    echo "❌ Zero-Simulation Compliance Check FAILED"
    exit 1
fi
echo "✅ Zero-Simulation Compliance Check PASSED"

# Run deterministic hash check
echo "2. Running Deterministic Hash Check..."
python tools/deterministic_hash_check.py
if [ $? -ne 0 ]; then
    echo "❌ Deterministic Hash Check FAILED"
    exit 1
fi
echo "✅ Deterministic Hash Check PASSED"

# Run PQC integrity check
echo "3. Running PQC Integrity Check..."
python tools/validate_pqc_integrity.py
if [ $? -ne 0 ]; then
    echo "❌ PQC Integrity Check FAILED"
    exit 1
fi
echo "✅ PQC Integrity Check PASSED"

# Run unit tests
echo "4. Running Unit Tests..."
python -m pytest tests/unit/ -x
if [ $? -ne 0 ]; then
    echo "❌ Unit Tests FAILED"
    exit 1
fi
echo "✅ Unit Tests PASSED"

# Run fast integration tests
echo "5. Running Fast Integration Tests..."
python -m pytest tests/integration/ -x -k "not slow"
if [ $? -ne 0 ]; then
    echo "❌ Fast Integration Tests FAILED"
    exit 1
fi
echo "✅ Fast Integration Tests PASSED"

echo "🎉 All Local CI/CD Checks PASSED!"