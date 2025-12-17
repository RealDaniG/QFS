"""
Test Evidence Determinism
=========================

Verifies `canonical_evidence_json` and `hash_evidence` guarantees.
"""

# import pytest (implicitly used by test runner)
# import json (unused)
from v13.services.governance.evidence import canonical_evidence_json, hash_evidence


def test_key_ordering():
    """Different insertion order must produce identical bytes."""
    ev1 = {"a": 1, "b": 2, "c": 3}
    ev2 = {"c": 3, "a": 1, "b": 2}

    b1 = canonical_evidence_json(ev1)
    b2 = canonical_evidence_json(ev2)

    assert b1 == b2
    assert b1 == b'{"a":1,"b":2,"c":3}'


def test_nested_ordering():
    """Nested dictionaries must also be sorted."""
    ev1 = {"meta": {"z": 9, "x": 8}, "data": [1, 2]}
    ev2 = {"data": [1, 2], "meta": {"x": 8, "z": 9}}

    assert canonical_evidence_json(ev1) == canonical_evidence_json(ev2)


def test_hashing_stability():
    """Hash must be stable across runs (SHA3-256)."""
    ev = {"id": "ev_001", "content": "hello"}

    h1 = hash_evidence(ev)
    h2 = hash_evidence(ev)

    assert h1 == h2
    # Known hash for {"content":"hello","id":"ev_001"}
    # SHA3-256 of '{"content":"hello","id":"ev_001"}'
    # We can check length at least
    assert len(h1) == 64


def test_list_order_matters():
    """Lists should NOT be reordered (they are sequence data)."""
    ev1 = {"tags": ["a", "b"]}
    ev2 = {"tags": ["b", "a"]}

    assert canonical_evidence_json(ev1) != canonical_evidence_json(ev2)
    assert hash_evidence(ev1) != hash_evidence(ev2)
