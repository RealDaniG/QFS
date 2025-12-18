"""
test_chat.py - ATLAS Chat Module Tests

Comprehensive test suite for Chat module covering:
- Conversation lifecycle
- Message operations
- Deterministic ordering
- Status management
- Event emission
- Integration with Spaces

Zero-Sim compliant with deterministic assertions.
"""

import pytest
from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.chat import (
    ChatService,
    Conversation,
    Message,
    ConversationType,
    MessageStatus,
    emit_conversation_created,
    emit_message_sent,
    emit_message_read,
)


@pytest.fixture
def cm():
    """CertifiedMath instance for tests"""
    return CertifiedMath()


@pytest.fixture
def chat_service(cm):
    """ChatService instance for tests"""
    return ChatService(cm, max_participants=100)


# ============================================================================
# Conversation Lifecycle Tests
# ============================================================================


def test_create_conversation_deterministic_id(chat_service):
    """Test that conversation IDs are deterministic"""
    participants = ["wallet_alice", "wallet_bob"]

    conv1 = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    # Reset service and create again with same params
    chat_service2 = ChatService(CertifiedMath(), max_participants=100)
    conv2 = chat_service2.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    assert conv1.conversation_id == conv2.conversation_id


def test_create_one_on_one_conversation(chat_service):
    """Test creating a one-on-one conversation"""
    participants = ["wallet_alice", "wallet_bob"]

    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    assert conversation.conversation_type == ConversationType.ONE_ON_ONE
    assert len(conversation.participants) == 2
    assert conversation.created_by == "wallet_alice"
    assert conversation.message_count == 0
    assert conversation.participants == sorted(participants)


def test_create_group_conversation(chat_service):
    """Test creating a group conversation"""
    participants = ["wallet_alice", "wallet_bob", "wallet_charlie"]

    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.GROUP,
        timestamp=1000000,
        log_list=[],
    )

    assert conversation.conversation_type == ConversationType.GROUP
    assert len(conversation.participants) == 3
    assert conversation.participants == sorted(participants)


def test_max_participants_limit(chat_service):
    """Test that max participants limit is enforced"""
    participants = [f"wallet_{i}" for i in range(101)]

    with pytest.raises(ValueError, match="exceeds max participants"):
        chat_service.create_conversation(
            creator_wallet="wallet_0",
            participants=participants,
            conversation_type=ConversationType.GROUP,
            timestamp=1000000,
            log_list=[],
        )


def test_creator_must_be_participant(chat_service):
    """Test that creator must be in participants list"""
    participants = ["wallet_bob", "wallet_charlie"]

    with pytest.raises(ValueError, match="Creator .* must be in participants"):
        chat_service.create_conversation(
            creator_wallet="wallet_alice",
            participants=participants,
            conversation_type=ConversationType.ONE_ON_ONE,
            timestamp=1000000,
            log_list=[],
        )


# ============================================================================
# Message Operations Tests
# ============================================================================


def test_send_message_deterministic_id(chat_service):
    """Test that message IDs are deterministic"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    msg1 = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    # Reset and send again
    chat_service2 = ChatService(CertifiedMath(), max_participants=100)
    conversation2 = chat_service2.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    msg2 = chat_service2.send_message(
        conversation_id=conversation2.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    assert msg1.message_id == msg2.message_id


def test_send_message_updates_conversation(chat_service):
    """Test that sending a message updates conversation metadata"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    initial_count = conversation.message_count
    initial_last_message = conversation.last_message_at

    chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    assert conversation.message_count == initial_count + 1
    assert conversation.last_message_at == 1000100


def test_reply_to_message(chat_service):
    """Test replying to a message"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    original_msg = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    reply_msg = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_bob",
        content_cid="Qm456def",
        timestamp=1000200,
        reply_to=original_msg.message_id,
        log_list=[],
    )

    assert reply_msg.reply_to_message_id == original_msg.message_id


def test_sender_must_be_participant(chat_service):
    """Test that only participants can send messages"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    with pytest.raises(ValueError, match="is not a participant"):
        chat_service.send_message(
            conversation_id=conversation.conversation_id,
            sender_wallet="wallet_charlie",
            content_cid="Qm123abc",
            timestamp=1000100,
            log_list=[],
        )


# ============================================================================
# Message Ordering Tests
# ============================================================================


def test_get_messages_deterministic_order(chat_service):
    """Test that messages are returned in deterministic order"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    # Send messages in random order
    msg3 = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm3",
        timestamp=1000300,
        log_list=[],
    )

    msg1 = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_bob",
        content_cid="Qm1",
        timestamp=1000100,
        log_list=[],
    )

    msg2 = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm2",
        timestamp=1000200,
        log_list=[],
    )

    messages = chat_service.get_conversation_messages(conversation.conversation_id)

    # Should be ordered by timestamp ASC
    assert messages[0].message_id == msg1.message_id
    assert messages[1].message_id == msg2.message_id
    assert messages[2].message_id == msg3.message_id


def test_get_messages_pagination(chat_service):
    """Test message pagination"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    # Send 10 messages
    for i in range(10):
        chat_service.send_message(
            conversation_id=conversation.conversation_id,
            sender_wallet="wallet_alice",
            content_cid=f"Qm{i}",
            timestamp=1000000 + (i * 100),
            log_list=[],
        )

    # Get last 5 messages
    messages = chat_service.get_conversation_messages(
        conversation.conversation_id, limit=5
    )

    assert len(messages) == 5
    # Should be the 5 most recent
    assert messages[0].content_cid == "Qm5"
    assert messages[4].content_cid == "Qm9"


# ============================================================================
# Status Management Tests
# ============================================================================


def test_mark_message_as_read(chat_service):
    """Test marking a message as read"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    message = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    assert message.status == MessageStatus.SENT

    updated_message = chat_service.mark_as_read(
        message_id=message.message_id,
        conversation_id=conversation.conversation_id,
        reader_wallet="wallet_bob",
        timestamp=1000200,
        log_list=[],
    )

    assert updated_message.status == MessageStatus.READ


def test_reader_must_be_participant(chat_service):
    """Test that only participants can mark messages as read"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=participants,
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    message = chat_service.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        log_list=[],
    )

    with pytest.raises(ValueError, match="is not a participant"):
        chat_service.mark_as_read(
            message_id=message.message_id,
            conversation_id=conversation.conversation_id,
            reader_wallet="wallet_charlie",
            timestamp=1000200,
            log_list=[],
        )


# ============================================================================
# Event Emission Tests
# ============================================================================


def test_conversation_created_event(cm):
    """Test conversation_created event emission"""
    participants = ["wallet_alice", "wallet_bob"]
    conversation = Conversation(
        conversation_id="conv_123",
        conversation_type=ConversationType.ONE_ON_ONE,
        participants=participants,
        created_at=1000000,
        created_by="wallet_alice",
        last_message_at=1000000,
        message_count=0,
    )

    log_list = []
    event = emit_conversation_created(conversation, cm, log_list, pqc_cid="test_cid")

    assert event.event_type == "conversation_created"
    assert event.wallet_id == "wallet_alice"
    assert event.token_type == "CHR"
    assert event.amount == "0.300000000000000000"
    assert event.metadata["conversation_id"] == "conv_123"


def test_message_sent_event(cm):
    """Test message_sent event emission"""
    message = Message(
        message_id="msg_123",
        conversation_id="conv_123",
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        status=MessageStatus.SENT,
    )

    log_list = []
    event = emit_message_sent(message, cm, log_list, pqc_cid="test_cid")

    assert event.event_type == "message_sent"
    assert event.wallet_id == "wallet_alice"
    assert event.token_type == "CHR"
    assert event.amount == "0.100000000000000000"
    assert event.metadata["message_id"] == "msg_123"


def test_message_read_event(cm):
    """Test message_read event emission"""
    message = Message(
        message_id="msg_123",
        conversation_id="conv_123",
        sender_wallet="wallet_alice",
        content_cid="Qm123abc",
        timestamp=1000100,
        status=MessageStatus.READ,
    )

    log_list = []
    event = emit_message_read(
        message, "wallet_bob", 1000200, cm, log_list, pqc_cid="test_cid"
    )

    assert event.event_type == "message_read"
    assert event.wallet_id == "wallet_bob"
    assert event.token_type == "FLX"
    assert event.amount == "0.010000000000000000"
    assert event.metadata["message_id"] == "msg_123"


# ============================================================================
# Integration Tests
# ============================================================================


def test_multiple_conversations_per_user(chat_service):
    """Test that a user can have multiple conversations"""
    # Create conversation 1
    conv1 = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=["wallet_alice", "wallet_bob"],
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    # Create conversation 2
    conv2 = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=["wallet_alice", "wallet_charlie"],
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000100,
        log_list=[],
    )

    assert conv1.conversation_id != conv2.conversation_id
    assert len(chat_service.conversations) == 2


def test_conversation_isolation(chat_service):
    """Test that conversations are isolated"""
    conv1 = chat_service.create_conversation(
        creator_wallet="wallet_alice",
        participants=["wallet_alice", "wallet_bob"],
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000000,
        log_list=[],
    )

    conv2 = chat_service.create_conversation(
        creator_wallet="wallet_charlie",
        participants=["wallet_charlie", "wallet_dave"],
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000100,
        log_list=[],
    )

    # Send message in conv1
    chat_service.send_message(
        conversation_id=conv1.conversation_id,
        sender_wallet="wallet_alice",
        content_cid="Qm123",
        timestamp=1000200,
        log_list=[],
    )

    # Conv2 should have no messages
    messages_conv2 = chat_service.get_conversation_messages(conv2.conversation_id)
    assert len(messages_conv2) == 0

    # Conv1 should have 1 message
    messages_conv1 = chat_service.get_conversation_messages(conv1.conversation_id)
    assert len(messages_conv1) == 1
