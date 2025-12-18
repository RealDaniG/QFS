"""
Phase V Prototype: Secure Chat Lifecycle
Validates end-to-end integration of v13.atlas.chat module.
Strict Zero-Sim Compliance: Single Thread, Single Log List, Real Math.
"""

import sys
import os

# Ensure proper path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.chat.chat_session import ChatSessionManager


def run_prototype():
    print(">>> Starting Phase V Secure Chat Prototype")

    # 1. Initialize Core
    log_list = []
    cm = CertifiedMath()
    chat_mgr = ChatSessionManager(cm)

    print(f"[*] Core Initialized. Math Mode: Real")

    # 2. Create Session (Alice)
    print("\n[Step 1] Alice creating chat session...")
    alice_wallet = "alice_wallet_123"
    timestamp_start = 1000000

    session = chat_mgr.create_session(
        owner_wallet=alice_wallet,
        timestamp=timestamp_start,
        log_list=log_list,
        metadata={"topic": "Project QFS"},
    )

    print(f"    > Session Created: {session.session_id}")
    print(f"    > Owner: {session.owner_wallet}")
    print(f"    > Status: {session.status}")

    # 3. Join Session (Bob)
    print("\n[Step 2] Bob joining session...")
    bob_wallet = "bob_wallet_456"
    chat_mgr.join_session(
        session.session_id, bob_wallet, timestamp_start + 10, log_list
    )
    print(f"    > Bob joined. Participants: {len(session.participants)}")

    # 4. Exchange Messages
    print("\n[Step 3] Exchanging messages...")

    # Alice sends
    msg1 = chat_mgr.send_message(
        session.session_id,
        alice_wallet,
        "encrypted_hello_bob",
        timestamp_start + 20,
        "sig_alice_1",
        log_list,
    )
    print(f"    > Alice sent msg: {msg1.message_id}")

    # Bob replies
    msg2 = chat_mgr.send_message(
        session.session_id,
        bob_wallet,
        "encrypted_hi_alice",
        timestamp_start + 30,
        "sig_bob_1",
        log_list,
    )
    print(f"    > Bob replied msg: {msg2.message_id}")

    if session.message_count != 2:
        print("!!! FAIL: Message count mismatch")
        sys.exit(1)

    # 5. End Session
    print("\n[Step 4] Ending session...")
    chat_mgr.end_session(
        session.session_id, alice_wallet, timestamp_start + 100, log_list
    )
    print(f"    > Session status: {session.status}")

    # 6. Verify Ended Constraint
    print("\n[Step 5] Verifying constraints (sending to ended session)...")
    try:
        chat_mgr.send_message(
            session.session_id,
            bob_wallet,
            "late_message",
            timestamp_start + 200,
            "sig_fail",
            log_list,
        )
        print("!!! FAIL: Allowed message to ended session")
        sys.exit(1)
    except ValueError as e:
        print(f"    > correctly blocked: {e}")

    # 7. Log Verification
    print("\n[Step 6] Verifying Log Integrity...")
    ops = [l["operation"] for l in log_list]
    print(f"    > Operations: {ops}")

    expected_ops = [
        "event_emitted",  # Chat created event
        "chat_session_created",  # Logic log
        "chat_participant_joined",
        "event_emitted",  # Msg 1 event
        "chat_message_dist",  # Msg 1 logic
        "event_emitted",  # Msg 2 event
        "chat_message_dist",  # Msg 2 logic
        "chat_session_ended",
    ]

    missing = [op for op in expected_ops if op not in ops]
    if missing:
        print(f"!!! FAIL: Missing operations in log: {missing}")
        sys.exit(1)

    print("\n>>> Phase V Prototype Verification COMPLETE: SUCCESS")


if __name__ == "__main__":
    run_prototype()
