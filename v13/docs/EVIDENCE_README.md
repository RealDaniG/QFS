# Evidence Management System

This directory contains the evidence management tools for QFS V13.5.

## Evidence Indexer

The `tools/evidence_indexer.py` script creates a deterministic index of all evidence artifacts in the repository.

### Usage

```bash
# Index all evidence in the default directory
python tools/evidence_indexer.py

# Index evidence in specific directories
python tools/evidence_indexer.py --evidence-dirs docs/evidence docs/reports

# Save index to a specific location
python tools/evidence_indexer.py --output-file docs/evidence/EVIDENCE_INDEX.json
```

### Features

1. **Deterministic**: Same repository state always produces the same index
2. **Comprehensive**: Scans all subdirectories for evidence artifacts
3. **Organized**: Categorizes artifacts by component and phase
4. **Verifiable**: Includes SHA-256 hashes for integrity verification
5. **Summarized**: Provides statistics on artifact counts by type and phase

### Output Format

The indexer generates a JSON file with the following structure:

```json
{
  "metadata": {
    "component": "EvidenceIndexer",
    "version": "QFS-V13.5",
    "generated_at": "2025-12-14T10:30:45Z",
    "evidence_directories_scanned": ["docs/evidence"]
  },
  "artifacts": [
    {
      "name": "storage_determinism.json",
      "path": "storage/storage_determinism.json",
      "type": "json",
      "size_bytes": 1234,
      "modified_time": "2025-12-14T10:30:45Z",
      "created_time": "2025-12-14T10:30:45Z",
      "sha256_hash": "a1b2c3d4e5f6...",
      "component": "storage",
      "phase": "PHASE3",
      "tags": ["evidence", "test"]
    }
  ],
  "summary": {
    "total_artifacts": 42,
    "by_type": {
      "json": 25,
      "md": 12,
      "txt": 5
    },
    "by_phase": {
      "PHASE1": 10,
      "PHASE2": 8,
      "PHASE3": 15,
      "PHASE4": 6,
      "PHASE5": 3
    }
  }
}
```

## Integration with CI

To ensure the evidence index stays up-to-date, add this to your CI pipeline:

```bash
# Regenerate evidence index
python tools/evidence_indexer.py

# Check if index changed (indicating unindexed evidence)
git diff --exit-code docs/evidence/EVIDENCE_INDEX.json
```

## Related Runbooks

- [Storage Incident Response](runbooks/storage_12_month_assurance_plan.md)
- [Evidence Management](runbooks/evidence_management.md)