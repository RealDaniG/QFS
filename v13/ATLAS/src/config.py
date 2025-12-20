"""
ATLAS API Configuration
Centralizes environment variable access to isolate non-deterministic inputs.
"""

import os

# Configuration variables
# These are read once at module load time
EXPLAIN_THIS_SOURCE = os.getenv("EXPLAIN_THIS_SOURCE", "memory")
QFS_LEDGER_PATH = os.getenv("QFS_LEDGER_PATH", "v13/ledger/qfs_ledger.jsonl")

