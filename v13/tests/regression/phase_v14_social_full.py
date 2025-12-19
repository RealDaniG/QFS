"""
phase_v14_social_full.py - v14 Regression Test Scenario

Canonical scenario for regression hash generation.
Covers all 11 event types across 3 modules.
"""

import sys
from pathlib import Path

# Add v13 to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.atlas.spaces import (
    SpacesManager,
    emit_space_created,
    emit_space_joined,
    emit_space_spoke,
    emit_space_ended,
)
from v13.atlas.wall import (
    WallService,
    emit_post_created,
    emit_post_quoted,
    emit_post_pinned,
    emit_post_reacted,
)
from v13.atlas.chat import (
    ChatService,
    ConversationType,
    emit_conversation_created,
    emit_message_sent,
    emit_message_read,
)


def run_scenario():
    """Run canonical v14 social scenario"""
    print("=" * 80)
    print("v14 Social Layer - Canonical Regression Scenario")
    print("=" * 80)

    # Initialize
    cm = CertifiedMath()
    spaces = SpacesManager(cm)
    wall = WallService(cm)
    chat = ChatService(cm)

    # Wallets
    alice = "wallet_alice"
    bob = "wallet_bob"
    charlie = "wallet_charlie"

    log_list = []

    print("\n[1/11] Creating space...")
    space = spaces.create_space(
        host_wallet=alice,
        title="Tech Talk",
        timestamp=1000000,
        log_list=log_list,
    )
    event1 = emit_space_created(space, cm, log_list, pqc_cid="test_001")
    print(f"  [OK] Space created: {space.space_id}")
    print(f"  [REWARD] {event1.amount} CHR to {alice}")

    print("\n[2/11] Joining space...")
    spaces.join_space(space.space_id, bob, 1000100, log_list)
    event2 = emit_space_joined(
        space.space_id, bob, 1000100, cm, log_list, pqc_cid="test_002"
    )
    print(f"  [OK] {bob} joined space")
    print(f"  💰 Reward: {event2.amount} CHR to {bob}")

    print("\n[3/11] Speaking in space...")
    spaces.record_speak_time(space.space_id, bob, 1000200, log_list)
    event3 = emit_space_spoke(
        space.space_id, bob, 100, 1000200, cm, log_list, pqc_cid="test_003"
    )
    print(f"  [OK] {bob} spoke in space")
    print(f"  💰 Reward: {event3.amount} CHR to {bob}")

    print("\n[4/11] Creating post...")
    post = wall.create_post(
        author_wallet=alice,
        content="Hello ATLAS!",
        timestamp=1000300,
        space_id=space.space_id,
        log_list=log_list,
    )
    event4 = emit_post_created(post, cm, log_list, pqc_cid="test_004")
    print(f"  [OK] Post created: {post.post_id}")
    print(f"  💰 Reward: {event4.amount} CHR to {alice}")

    print("\n[5/11] Quoting post...")
    quote = wall.quote_post(
        author_wallet=bob,
        parent_post_id=post.post_id,
        content="Great post!",
        timestamp=1000400,
        log_list=log_list,
    )
    event5 = emit_post_quoted(quote, post, cm, log_list, pqc_cid="test_005")
    print(f"  [OK] Post quoted: {quote.post_id}")
    print(f"  💰 Reward: {event5.amount} CHR to {bob}")

    print("\n[6/11] Pinning post...")
    wall.pin_post(post.post_id, alice, 1000500, log_list)
    event6 = emit_post_pinned(post, alice, cm, log_list, pqc_cid="test_006")
    print(f"  [OK] Post pinned by {alice}")
    print(f"  💰 Reward: {event6.amount} CHR to {alice}")

    print("\n[7/11] Reacting to post...")
    wall.add_reaction(post.post_id, charlie, "[LIKE]", log_list)
    event7 = emit_post_reacted(
        post.post_id, charlie, "[LIKE]", 1000600, cm, log_list, pqc_cid="test_007"
    )
    print(f"  [OK] {charlie} reacted with 👍")
    print(f"  💰 Reward: {event7.amount} FLX to {charlie}")

    print("\n[8/11] Creating conversation...")
    conversation = chat.create_conversation(
        creator_wallet=alice,
        participants=[alice, bob],
        conversation_type=ConversationType.ONE_ON_ONE,
        timestamp=1000700,
        log_list=log_list,
    )
    event8 = emit_conversation_created(conversation, cm, log_list, pqc_cid="test_008")
    print(f"  [OK] Conversation created: {conversation.conversation_id}")
    print(f"  💰 Reward: {event8.amount} CHR to {alice}")

    print("\n[9/11] Sending message...")
    message = chat.send_message(
        conversation_id=conversation.conversation_id,
        sender_wallet=alice,
        content_cid="Qm123abc",
        timestamp=1000800,
        log_list=log_list,
    )
    event9 = emit_message_sent(message, cm, log_list, pqc_cid="test_009")
    print(f"  [OK] Message sent: {message.message_id}")
    print(f"  💰 Reward: {event9.amount} CHR to {alice}")

    print("\n[10/11] Reading message...")
    chat.mark_as_read(
        message.message_id, conversation.conversation_id, bob, 1000900, log_list
    )
    event10 = emit_message_read(message, bob, 1000900, cm, log_list, pqc_cid="test_010")
    print(f"  [OK] Message read by {bob}")
    print(f"  💰 Reward: {event10.amount} FLX to {bob}")

    print("\n[11/11] Ending space...")
    spaces.end_space(space.space_id, alice, 1001000, log_list)
    event11 = emit_space_ended(space, 1001000, cm, log_list, pqc_cid="test_011")
    print(f"  [OK] Space ended by {alice}")
    print(f"  💰 Reward: {event11.amount} CHR to {alice}")

    # Calculate totals
    print("\n" + "=" * 80)
    print("Final State Summary")
    print("=" * 80)

    alice_chr = sum(
        [
            float(event1.amount),  # space_created
            float(event4.amount),  # post_created
            float(event6.amount),  # post_pinned
            float(event8.amount),  # conversation_created
            float(event9.amount),  # message_sent
            float(event11.amount),  # space_ended
        ]
    )

    bob_chr = sum(
        [
            float(event2.amount),  # space_joined
            float(event3.amount),  # space_spoke
            float(event5.amount),  # post_quoted
        ]
    )

    alice_flx = 0.0
    bob_flx = float(event10.amount)  # message_read
    charlie_flx = float(event7.amount)  # post_reacted

    print(f"\nAlice:")
    print(f"  CHR: {alice_chr}")
    print(f"  FLX: {alice_flx}")

    print(f"\nBob:")
    print(f"  CHR: {bob_chr}")
    print(f"  FLX: {bob_flx}")

    print(f"\nCharlie:")
    print(f"  CHR: 0.0")
    print(f"  FLX: {charlie_flx}")

    total_chr = alice_chr + bob_chr
    total_flx = alice_flx + bob_flx + charlie_flx

    print(f"\nTotal Emitted:")
    print(f"  CHR: {total_chr}")
    print(f"  FLX: {total_flx}")

    print("\n" + "=" * 80)
    print("Scenario Complete - Ready for Hash Generation")
    print("=" * 80)

    log_hash = cm.get_log_hash(log_list)
    print(f"Regression Hash: {log_hash}")
    return log_hash


if __name__ == "__main__":
    # Print hash for CI capture, exit 0 if successful
    h = run_scenario()
    if h:
        sys.exit(0)
    sys.exit(1)
