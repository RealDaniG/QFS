"""Tests for QFSClient and RealLedger integration."""

import sys
from pathlib import Path

import pytest
import asyncio
from datetime import datetime, timezone

# Ensure the repository's ATLAS root directory (parent of 'src') is on sys.path
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in _THIS_FILE.parents:
    if parent.name == "ATLAS":
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    if str(_ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(_ATLAS_ROOT))

from src.qfs_client import QFSClient
from src.qfs_types import OperationBundle
from src.types import Transaction, DeterminismReport
from src.real_ledger import RealLedger, MockLedger

@pytest.fixture
def mock_ledger():
    """Create mock ledger for testing"""
    return MockLedger()

@pytest.fixture
def real_ledger(mock_ledger):
    """Create real ledger with mock adapter"""
    return RealLedger(mock_ledger)

@pytest.fixture
def qfs_client(real_ledger):
    """Create QFS client with real ledger"""
    return QFSClient(real_ledger, private_key="test_key")

@pytest.mark.asyncio
async def test_submit_transaction(qfs_client):
    """Test transaction submission"""
    tx = Transaction(
        transaction_id=None,
        operation_type="secure_chat_thread_created",
        creator_id="user_123",
        data={
            "participants": ["user_123", "user_456"],
            "title": "Test Thread",
            "metadata": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    receipt = await qfs_client.submit_transaction(tx)
    
    assert receipt.status in ["submitted", "confirmed"]
    assert receipt.transaction_id is not None
    assert receipt.bundle_hash is not None
    assert receipt.timestamp is not None

@pytest.mark.asyncio
async def test_get_state(qfs_client):
    """Test state retrieval"""
    # First submit a transaction to create state
    tx = Transaction(
        transaction_id=None,
        operation_type="secure_chat_thread_created",
        creator_id="user_123",
        data={
            "participants": ["user_123"],
            "title": "Test Thread",
            "metadata": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    await qfs_client.submit_transaction(tx)
    
    # Get state
    state = await qfs_client.get_state("user_123")
    
    assert state is not None
    assert state["address"] == "user_123"
    assert state["balance"] == 1000
    assert state["nonce"] == 1

@pytest.mark.asyncio
async def test_replay_transaction(qfs_client):
    """Test transaction replay for determinism"""
    # Submit a transaction
    tx = Transaction(
        transaction_id="test_tx_123",
        operation_type="secure_chat_thread_created",
        creator_id="user_123",
        data={
            "participants": ["user_123"],
            "title": "Test Thread",
            "metadata": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    receipt = await qfs_client.submit_transaction(tx)
    
    # Replay the transaction
    report = await qfs_client.replay_transaction(receipt.transaction_id)
    
    assert isinstance(report, DeterminismReport)
    assert report.transaction_hash == receipt.transaction_id
    assert report.replay_success is True
    assert report.matches_original is True

def test_operation_bundle_serialization():
    """Test deterministic serialization of operation bundles"""
    bundle = OperationBundle(
        operations=[
            {
                "type": "secure_chat_thread_created",
                "creator_id": "user_123",
                "data": {"title": "Test"},
                "nonce": 0
            }
        ],
        bundle_hash="test_hash",
        timestamp="2023-01-01T00:00:00Z",
        creator_id="user_123"
    )
    
    # Convert to dict and back
    bundle_dict = bundle.to_dict()
    
    assert bundle_dict["bundle_hash"] == "test_hash"
    assert bundle_dict["creator_id"] == "user_123"
    assert len(bundle_dict["operations"]) == 1

@pytest.mark.asyncio
async def test_bundle_tracking(qfs_client):
    """Test pending bundle tracking"""
    # Submit a transaction
    tx = Transaction(
        transaction_id=None,
        operation_type="secure_chat_thread_created",
        creator_id="user_123",
        data={
            "participants": ["user_123"],
            "title": "Test Thread",
            "metadata": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    receipt = await qfs_client.submit_transaction(tx)
    
    # Check pending bundles
    pending = await qfs_client.list_pending_bundles()
    assert receipt.bundle_hash in pending
    
    # Get bundle status
    status = await qfs_client.get_bundle_status(receipt.bundle_hash)
    assert status["status"] == "confirmed"

@pytest.mark.asyncio
async def test_transaction_validation(qfs_client):
    """Test transaction validation"""
    # Test missing operation type
    with pytest.raises(ValueError, match="operation_type"):
        tx = Transaction(
            transaction_id=None,
            operation_type="",
            creator_id="user_123",
            data={}
        )
        await qfs_client.submit_transaction(tx)
    
    # Test missing creator ID
    with pytest.raises(ValueError, match="creator_id"):
        tx = Transaction(
            transaction_id=None,
            operation_type="test",
            creator_id="",
            data={}
        )
        await qfs_client.submit_transaction(tx)

@pytest.mark.asyncio
async def test_real_ledger_adapter(real_ledger):
    """Test RealLedger adapter functionality"""
    # Create operation bundle
    bundle = OperationBundle(
        operations=[
            {
                "type": "secure_chat_thread_created",
                "creator_id": "user_123",
                "data": {"title": "Test"},
                "nonce": 0
            }
        ],
        bundle_hash="test_hash",
        timestamp="2023-01-01T00:00:00Z",
        creator_id="user_123"
    )
    
    # Submit bundle
    receipt = await real_ledger.submit_bundle(bundle)
    
    assert receipt.status == "confirmed"
    assert receipt.bundle_hash == "test_hash"
    
    # Get snapshot
    snapshot = await real_ledger.get_snapshot()
    
    assert snapshot is not None
    assert "user_123" in snapshot
    
    # Get bundle status
    status = await real_ledger.get_bundle_status("test_hash")
    assert status["status"] == "confirmed"
