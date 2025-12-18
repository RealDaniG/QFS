"""Tests for Secure Chat Engine."""
from pathlib import Path
import pytest
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in sorted(_THIS_FILE.parents):
    if parent.name == 'ATLAS':
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    if str(_ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(_ATLAS_ROOT))
from src.secure_chat.core.engine import SecureChatEngine, ThreadStatus
from src.secure_chat.storage.memory_storage import MemoryStorage

class MockATREngine:

    def __init__(self):
        self.charges = []

    async def charge_fee(self, account_id: str, amount: int, description: str):
        self.charges.append({'account_id': account_id, 'amount': amount, 'description': description})

@pytest.fixture
def engine():
    storage = MemoryStorage()
    atr_engine = MockATREngine()
    fixed_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    engine = SecureChatEngine(storage, atr_engine, clock=lambda tz: fixed_time)
    engine.storage = storage
    return engine

@pytest.mark.asyncio
async def test_create_thread(engine):
    """Test thread creation with deterministic ID"""
    creator_id = 'user1'
    participants = ['user1', 'user2']
    thread, events = engine.create_thread(creator_id, participants)
    assert thread.creator_id == creator_id
    assert set(thread.participants) == set(participants)
    assert thread.status == ThreadStatus.ACTIVE
    assert len(events) == 1
    assert events[0]['event_type'] == 'THREAD_CREATED'
    thread2, _ = engine.create_thread(creator_id, participants)
    assert thread.thread_id == thread2.thread_id

@pytest.mark.asyncio
async def test_post_message(engine):
    """Test posting a message to a thread"""
    thread, _ = engine.create_thread('user1', ['user1', 'user2'])
    content = b'Hello, secure chat!'
    message, events = await engine.post_message(thread.thread_id, 'user1', content, 'text/plain')
    assert message.content_size == len(content)
    assert message.sender_id == 'user1'
    assert len(events) == 1
    assert events[0]['event_type'] == 'MESSAGE_POSTED'
    messages = engine.get_messages(thread.thread_id, 'user1')
    assert len(messages) == 1
    assert messages[0].message_id == message.message_id

def test_thread_participant_access(engine):
    """Test thread access control"""
    thread, _ = engine.create_thread('user1', ['user1', 'user2'])
    assert engine.get_thread(thread.thread_id, 'user3') is None
    assert not engine.get_messages(thread.thread_id, 'user3')

@pytest.mark.asyncio
async def test_thread_lifecycle(engine):
    """Test thread archiving and deletion"""
    thread, _ = engine.create_thread('user1', ['user1', 'user2'])
    await engine.post_message(thread.thread_id, 'user1', b'Hello', 'text/plain')
    updated_thread, events = await engine.update_thread_status(thread.thread_id, 'user1', ThreadStatus.ARCHIVED)
    assert updated_thread.status == ThreadStatus.ARCHIVED
    assert len(events) == 1
    assert events[0]['event_type'] == 'THREAD_UPDATED'
    with pytest.raises(ValueError, match='Cannot post to ARCHIVED thread'):
        await engine.post_message(thread.thread_id, 'user1', b'Should fail', 'text/plain')
    updated_thread, events = await engine.update_thread_status(thread.thread_id, 'user1', ThreadStatus.DELETED)
    assert updated_thread.status == ThreadStatus.DELETED
    assert not engine.get_messages(thread.thread_id, 'user1')

@pytest.mark.asyncio
async def test_message_size_limit(engine):
    """Test message size validation"""
    thread, _ = engine.create_thread('user1', ['user1'])
    large_content = b'x' * (engine.MAX_MESSAGE_SIZE + 1)
    with pytest.raises(ValueError, match='exceeds maximum size'):
        await engine.post_message(thread.thread_id, 'user1', large_content, 'text/plain')

def test_participant_validation(engine):
    """Test participant validation"""
    thread, _ = engine.create_thread('user1', [])
    assert thread.participants == ['user1']
    with pytest.raises(ValueError, match='Duplicate participants'):
        engine.create_thread('user1', ['user1', 'user1'])

@pytest.mark.asyncio
async def test_empty_message_validation(engine):
    """Test empty message validation"""
    thread, _ = engine.create_thread('user1', ['user1'])
    with pytest.raises(ValueError, match='Message content cannot be empty'):
        await engine.post_message(thread.thread_id, 'user1', b'', 'text/plain')

@pytest.mark.asyncio
async def test_thread_status_permissions(engine):
    """Test thread status update permissions"""
    thread, _ = engine.create_thread('user1', ['user1', 'user2'])
    with pytest.raises(PermissionError, match='Only thread creator can update'):
        await engine.update_thread_status(thread.thread_id, 'user2', ThreadStatus.ARCHIVED)

@pytest.mark.asyncio
async def test_deleted_thread_operations(engine):
    """Test operations on deleted threads"""
    thread, _ = engine.create_thread('user1', ['user1'])
    await engine.update_thread_status(thread.thread_id, 'user1', ThreadStatus.DELETED)
    with pytest.raises(ValueError, match='Cannot modify deleted thread'):
        await engine.update_thread_status(thread.thread_id, 'user1', ThreadStatus.ACTIVE)