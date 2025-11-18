#!/bin/bash

# QFS V13.5 - Optimized Full Audit Wrapper Script
# Runs all audit steps for Phase 1 + Phase 2 based on selected mode

set -e  # Exit on any error

# Default values
AUDIT_MODE="dev"
EVIDENCE_DIR="evidence"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            AUDIT_MODE="$2"
            shift 2
            ;;
        --evidence)
            EVIDENCE_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate audit mode
if [[ "$AUDIT_MODE" != "dev" && "$AUDIT_MODE" != "pre-release" && "$AUDIT_MODE" != "release" ]]; then
    echo "Error: Invalid audit mode. Must be one of: dev, pre-release, release"
    exit 1
fi

echo "QFS V13.5 Full Audit - Mode: $AUDIT_MODE"
echo "Evidence directory: $EVIDENCE_DIR"
echo "========================================"

# Create evidence directories
mkdir -p "$EVIDENCE_DIR"/phase1
mkdir -p "$EVIDENCE_DIR"/phase2

# Export environment variables for deterministic execution
export LC_ALL=C.UTF-8
export PYTHONHASHSEED=0
export TZ=UTC

# Run audit steps in order
echo "Running Phase 1 static checks..."
./tools/audit/01_static_checks.sh

echo "Running Phase 1 tests..."
./tools/audit/02_phase1_tests.sh

echo "Running concurrency tests..."
./tools/audit/03_concurrency.sh

echo "Running Phase 2 core tests..."
./tools/audit/04_phase2_core.sh

echo "Running oracle and QPU tests..."
./tools/audit/05_oracles_qpu.sh

echo "Running Holonet tests..."
./tools/audit/06_holonet.sh

echo "Running determinism fuzzer..."
./tools/audit/07_determinism_fuzzer.sh --mode "$AUDIT_MODE"

echo "Running adversarial simulator..."
./tools/audit/08_adversarial.sh --mode "$AUDIT_MODE"

echo "Creating and signing manifest..."
./tools/audit/09_manifest_sign.sh

echo "Running gating check..."
./tools/audit/10_gating_check.sh

# Package evidence
echo "Packaging evidence..."
cd "$EVIDENCE_DIR"
zip -r evidence_phase12.zip phase1 phase2
sha256sum evidence_phase12.zip > evidence_phase12.zip.sha256

echo "Audit completed successfully!"
echo "Evidence packaged in $EVIDENCE_DIR/evidence_phase12.zip"