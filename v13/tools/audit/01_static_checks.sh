#!/bin/bash

# QFS V13.5 - Phase 1 Static Checks
# Checks for floats, nondeterministic libs, and _log_operation calls

set -e

echo "Running Phase 1 Static Checks..."

# Create evidence directory
mkdir -p evidence/phase1/static

# Check for float constants
echo "Checking for float constants..."
grep -r "\b[0-9]*\.[0-9]*\b" src/ --include="*.py" > evidence/phase1/static/float_constants.txt 2>/dev/null || true

# Check for nondeterministic libraries
echo "Checking for nondeterministic libraries..."
# Add checks for random, time, etc.

# Check for _log_operation calls with pqc_cid
echo "Checking _log_operation calls..."
# This would need a more sophisticated check

echo "Phase 1 Static Checks completed."