"""
test_system_creator_wallet.py - Unit tests for System Creator Wallet
"""

import pytest
import os
import json
import asyncio
from unittest.mock import MagicMock, patch, mock_open

from v13.libs.crypto.derivation import derive_creator_keypair
from v13.libs.keystore.manager import KeystoreManager
from v13.ledger.writer import LedgerWriter
from v13.policy.authorization import AuthorizationEngine

# Expected values for "DEV" scope based on our HKDF-SHA256 logic
EXPECTED_ADDRESS_DEV = (
    "0x7f63e288dd4775ca540298e7e6de6169b2eec1f281c6949a1c2ee812b00e3d7f"
)

EXPECTED_ADDRESS_TESTNET = (
    "0xc5c70800f3bede34e79e3240932326b5048114ee1a9cb93c88e26284a9ea9617"
)
# Private key is sensitive, but in this specific fixed-salt/fixed-info implementation, it's deterministic.
# We test against the address mainly.


def test_derive_creator_keypair_dev():
    priv, addr = derive_creator_keypair("DEV")
    assert addr == EXPECTED_ADDRESS_DEV
    assert len(priv) == 64  # 32 bytes hex


def test_derive_creator_keypair_testnet():
    priv, addr = derive_creator_keypair("TESTNET")
    assert addr == EXPECTED_ADDRESS_TESTNET
    assert len(priv) == 64


def test_derive_creator_keypair_replay():
    """Verify that derivation is deterministic across calls."""
    # Call 1
    priv1, addr1 = derive_creator_keypair("DEV")
    # Call 2
    priv2, addr2 = derive_creator_keypair("DEV")

    assert priv1 == priv2
    assert addr1 == addr2


def test_derive_creator_keypair_invalid_scope():
    with pytest.raises(ValueError, match="Invalid scope"):
        derive_creator_keypair("MAINNET")


def test_keystore_manager_save_and_get(tmp_path):
    # Mock file path
    ks_file = tmp_path / ".qfs_keystore_test.json"

    ks = KeystoreManager(str(ks_file))
    assert not ks.exists("SYSTEM_CREATOR", "DEV")

    ks.save_key("SYSTEM_CREATOR", "DEV", "privkey123", "addr123")
    assert ks.exists("SYSTEM_CREATOR", "DEV")

    wallet = ks.get_wallet("SYSTEM_CREATOR", "DEV")
    assert wallet["public_address"] == "addr123"
    assert wallet["private_key"] == "privkey123"

    # Reload from file
    ks2 = KeystoreManager(str(ks_file))
    assert ks2.exists("SYSTEM_CREATOR", "DEV")
    assert ks2.get_wallet("SYSTEM_CREATOR", "DEV")["public_address"] == "addr123"


def test_keystore_conflict(tmp_path):
    ks_file = tmp_path / ".qfs_keystore_test.json"
    ks = KeystoreManager(str(ks_file))

    ks.save_key("R", "S", "k1", "a1")

    # Same data is fine
    ks.save_key("R", "S", "k1", "a1")

    # Different address raises
    with pytest.raises(ValueError, match="Key conflict"):
        ks.save_key("R", "S", "k2", "a2")


@pytest.mark.asyncio
async def test_ledger_writer_emit(tmp_path):
    ledger_file = tmp_path / "test_ledger.jsonl"
    writer = LedgerWriter(str(ledger_file))

    entry = await writer.emit_wallet_registered("addr1", "ROLE", "SCOPE", ["CAP1"])

    assert entry.wallet == "addr1"
    assert entry.timestamp == "2025-01-01T00:00:00Z"  # Deterministic
    assert entry.metadata["role"] == "ROLE"

    # Read back (simulated by just checking file presence/content for now, or using a reader if we had one in this test)
    # The LedgerWriter uses GenesisLedger internally which handles writes.
    assert os.path.exists(ledger_file)
    with open(ledger_file, "r") as f:
        line = f.readline()
        saved = json.loads(line)
        assert saved["wallet"] == "addr1"


def test_authorization_replay():
    # Mock entries
    class MockEntry:
        def __init__(self, et, meta):
            self.event_type = et
            self.metadata = meta

    entries = [
        MockEntry(
            "WALLET_REGISTERED",
            {
                "wallet_id": "w1",
                "role": "SYSTEM_CREATOR",
                "scope": "DEV",
                "capabilities": ["READ", "WRITE"],
            },
        )
    ]

    auth = AuthorizationEngine(entries)

    assert auth.resolve_role("w1") == "SYSTEM_CREATOR"
    assert auth.resolve_role("w2") == "NONE"

    assert auth.authorize("w1", "READ", "DEV") is True
    assert auth.authorize("w1", "WRITE", "DEV") is True
    assert auth.authorize("w1", "EXECUTE", "DEV") is False
    assert auth.authorize("w1", "READ", "PROD") is False  # Wrong scope

    # Test LEDGER_READ_ALL hierarchy
    entries2 = [
        MockEntry(
            "WALLET_REGISTERED",
            {
                "wallet_id": "wadmin",
                "role": "SYSTEM_CREATOR",
                "scope": "DEV",
                "capabilities": ["LEDGER_READ_ALL"],
            },
        )
    ]
    auth2 = AuthorizationEngine(entries2)
    assert auth2.authorize("wadmin", "READ", "DEV") is True
