"""
Tests for Audit Integrity - QFS V13.8

Verifies:
1. SHA-256 integrity hash verification.
2. Tamper detection logic.
3. Chain consistency checks.
"""
import pytest
from v13.core.audit_integrity import verify_explanation_integrity, detect_tampering

def test_integrity_verification_success():
    """Verify that correct hashes pass validation."""
    data = {'action': 'TEST', 'actor': 'Alice', 'ts': 123}
    import json, hashlib
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    valid_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    assert verify_explanation_integrity(data, valid_hash) is True

def test_integrity_verification_failure():
    """Verify that tampered data fails validation."""
    data = {'action': 'TEST', 'actor': 'Alice', 'ts': 123}
    import json, hashlib
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    valid_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    tampered_data = data.copy()
    tampered_data['actor'] = 'Bob'
    assert verify_explanation_integrity(tampered_data, valid_hash) is False

def test_tamper_detection_chain():
    """Verify chain integrity checks."""
    prev_hash = 'abc12345'
    record = {'prev_hash': prev_hash, 'action': 'Legit Action', 'hash': ''}
    import json, hashlib
    to_hash = {k: v for k, v in record.items() if k != 'hash'}
    json_str = json.dumps(to_hash, sort_keys=True, separators=(',', ':'))
    record['hash'] = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    result = detect_tampering(record, prev_hash)
    assert result['valid'] is True
    result_broken = detect_tampering(record, 'wrong_prev_hash')
    assert result_broken['valid'] is False
    assert result_broken['error'] == 'BROKEN_CHAIN_LINK'
    tampered_record = record.copy()
    tampered_record['action'] = 'Hacked Action'
    result_tampered = detect_tampering(tampered_record, prev_hash)
    assert result_tampered['valid'] is False
    assert result_tampered['error'] == 'INTEGRITY_HASH_MISMATCH'