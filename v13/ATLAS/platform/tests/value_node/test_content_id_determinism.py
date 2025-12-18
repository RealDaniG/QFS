"""Tests for deterministic content-ID (content as NFT-style object).

These tests are an initial verification slice for the V13.8
"content as NFT" model. They do NOT modify core economics or guards.
They only verify that canonical serialization and hashing behave
as expected for representative fixtures.
"""
from __future__ import annotations
import hashlib
import json
from typing import Dict, Any
import pytest

def compute_content_id(payload: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Reference content-id helper using canonical JSON serialization.

    This is a **test-side reference** implementation. Production code
    is expected to follow the same canonicalization rules (sorted keys,
    UTF-8 encoding, stable separators) but may live in a different
    module. This helper is intentionally pure and deterministic.
    """
    canonical = json.dumps({'payload': payload, 'metadata': metadata}, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()

@pytest.mark.parametrize('payload, metadata', [({'text': 'Hello, QFS!'}, {'creator_id': 'user_1', 'content_type': 'post'}), ({'text': 'Hello, QFS!', 'tags': ['qfs', 'atlas']}, {'creator_id': 'user_1', 'content_type': 'post'})])
def test_content_id_deterministic_for_same_input(payload: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    """Same payload + metadata should always yield the same content_id."""
    cid_1 = compute_content_id(payload, metadata)
    cid_2 = compute_content_id(payload, metadata)
    assert isinstance(cid_1, str)
    assert cid_1 == cid_2
    assert len(cid_1) == 64

def test_content_id_changes_when_payload_changes() -> None:
    """Different payloads must yield different content_ids."""
    base_metadata = {'creator_id': 'user_1', 'content_type': 'post'}
    cid_a = compute_content_id({'text': 'Hello, QFS!'}, base_metadata)
    cid_b = compute_content_id({'text': 'Hello, QFS!!'}, base_metadata)
    assert cid_a != cid_b

def test_content_id_changes_when_metadata_changes() -> None:
    """Metadata changes (e.g. creator_id) must affect content_id."""
    payload = {'text': 'Same text'}
    cid_user1 = compute_content_id(payload, {'creator_id': 'user_1', 'content_type': 'post'})
    cid_user2 = compute_content_id(payload, {'creator_id': 'user_2', 'content_type': 'post'})
    assert cid_user1 != cid_user2

def test_canonical_serialization_stable_field_order() -> None:
    """Field order in input dicts must not affect content_id.

    This ensures that callers can build metadata/payload dictionaries in
    any order and still obtain a stable identifier.
    """
    payload_a = {'text': 'Hello', 'lang': 'en'}
    payload_b = {'lang': 'en', 'text': 'Hello'}
    metadata_a = {'creator_id': 'user_1', 'content_type': 'post', 'extra': {'foo': 1, 'bar': 2}}
    metadata_b = {'content_type': 'post', 'creator_id': 'user_1', 'extra': {'bar': 2, 'foo': 1}}
    cid_a = compute_content_id(payload_a, metadata_a)
    cid_b = compute_content_id(payload_b, metadata_b)
    assert cid_a == cid_b