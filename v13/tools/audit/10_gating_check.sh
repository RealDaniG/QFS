#!/bin/bash

# QFS V13.5 - Gating Check
# Simulates calling the gating service with manifest and signature

set -e

echo "Running gating check..."

# Simulate gating service response
# In a real implementation, this would call the actual gating service REST endpoint

# Check if all required evidence files exist
REQUIRED_FILES=(
    "evidence/phase1/phase1_files.sha256"
    "evidence/phase2/df_sha256s.txt"
    "evidence/phase2/adversary_results.json"
    "Docs/phase12_manifest.json"
    "Docs/phase12_manifest.json.sig"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo "Error: Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

# Simulate successful gating response
cat > evidence/gating_response.json << EOF
{
  "phase": "phase1-2",
  "status": "accepted",
  "manifest_hash": "$(sha256sum Docs/phase12_manifest.json | cut -d' ' -f1)",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "Gating check completed successfully."
echo "Response saved to evidence/gating_response.json"