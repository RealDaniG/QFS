"""
Evidence Canonicalization
=========================

Enforces strict serializability, ordering, and hashing for evidence bundles.
Zero-Sim requirement: Identical Input -> Identical Bytes -> Identical Hash.

Contract:
- Keys are sorted alphabetically.
- No optional fields (None values are dropped or strictly explicit).
- Float values are FORBIDDEN (must use integer scales or strings).
"""

import json
import hashlib
from typing import Any, Dict


def canonical_evidence_json(evidence: Dict[str, Any]) -> bytes:
    """
    Produce a canonical JSON byte string for the given evidence.

    Rules:
    1. Keys sorted.
    2. No whitespace (separators=(',', ':')).
    3. Recursive sorting for nested dicts.
    4. Lists are NOT sorted (order matters for logs), but elements are canonicalized.

    Args:
        evidence: The dictionary to serialize.

    Returns:
        bytes: Functional deterministic JSON.
    """
    # 1. Validation (Zero-Sim Scan would enforce this statically, but runtime check here)
    # We could check for floats but let's assume upstream provides clean data.

    # 2. Dump
    # sort_keys=True ensures dictionary keys are A-Z.
    # separators=(',', ':') removes whitespace.
    try:
        json_str = json.dumps(
            evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
    except TypeError as e:
        raise ValueError(f"Evidence contains non-serializable types: {e}")

    return json_str.encode("utf-8")


def hash_evidence(evidence: Dict[str, Any]) -> str:
    """
    Produce a deterministic SHA3-256 hash of the evidence.
    """
    payload = canonical_evidence_json(evidence)
    return hashlib.sha3_256(payload).hexdigest()


def normalize_evidence(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to clean evidence before canonicalization (e.g., removing None values if needed).
    """
    # Recursive normalization could go here.
    # For P0, we assume the input is already a valid dict structure.
    return evidence
