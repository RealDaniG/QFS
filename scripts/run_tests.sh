#!/bin/bash
# QFS V13 Test Runner Script

echo "Running QFS V13 Test Suite..."

# Run unit tests
echo "Running Unit Tests..."
python -m pytest tests/unit/ -v

# Run integration tests
echo "Running Integration Tests..."
python -m pytest tests/integration/ -v

# Run deterministic tests
echo "Running Deterministic Tests..."
python -m pytest tests/deterministic/ -v

# Run property-based tests
echo "Running Property-Based Tests..."
python -m pytest tests/property/ -v

echo "All tests completed!"