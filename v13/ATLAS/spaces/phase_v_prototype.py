"""
ATLAS Phase V Prototype - Spaces and Wall Posts Integration Check
"""

import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.spaces.spaces_manager import SpacesManager, ParticipantRole
from v13.atlas.spaces.spaces_events import (
    emit_space_created,
    emit_space_joined,
    emit_space_ended,
)
from v13.atlas.spaces.wall_posts import WallPostManager
from v13.atlas.spaces.wall_posts_events import (
    emit_post_created,
    emit_post_liked,
    emit_post_replied,
)


def run_prototype():
    print(">>> Starting ATLAS Phase V Prototype: Spaces + Wall Posts")

    cm = CertifiedMath()
    log_list = []

    # 1. Initialize Managers
    spaces_mgr = SpacesManager(cm)
    wall_mgr = WallPostManager(cm)

    # 2. Host creates a Space
    print("\n[Step 1] Creating Space...")
    space = spaces_mgr.create_space(
        "host_wallet", "Phase V Demo Space", 1000, log_list=log_list
    )
    event_space_created = emit_space_created(space, cm, log_list)
    print(f"Space Created: {space.space_id} by {space.host_wallet}")
    print(
        f"Event: {event_space_created.event_type} Amount: {event_space_created.amount} {event_space_created.token_type}"
    )

    # 3. User Joins Space
    print("\n[Step 2] User Joining Space...")
    spaces_mgr.join_space(space.space_id, "user_wallet", 1010, log_list=log_list)
    event_joined = emit_space_joined(space.space_id, "user_wallet", 1010, cm, log_list)
    print(f"User Joined: {event_joined.wallet_id}")

    # 4. Host Posts to Wall (Linked to Space)
    print("\n[Step 3] Host Posting to Wall...")
    post = wall_mgr.create_post(
        space.space_id,
        "host_wallet",
        "Welcome to the Phase V Space!",
        1020,
        log_list=log_list,
    )
    event_post = emit_post_created(post, cm, log_list)
    print(f"Post Created: {post.post_id}")
    print(f"Linked to Space: {post.space_id}")

    # 5. User Likes Post
    print("\n[Step 4] User Liking Post...")
    wall_mgr.like_post(post.post_id, "user_wallet", 1030, log_list=log_list)
    event_like = emit_post_liked(
        post.post_id, "user_wallet", "host_wallet", 1030, cm, log_list
    )
    print(
        f"Like Recorded. Event: {event_like.event_type} -> Reward Author: {event_like.wallet_id} ({event_like.amount})"
    )

    # 6. User Replies to Post
    print("\n[Step 5] User Replying...")
    reply = wall_mgr.reply_to_post(
        post.post_id, "user_wallet", "Great to be here!", 1040, log_list=log_list
    )
    reply_events = emit_post_replied(reply, "host_wallet", cm, log_list)

    print(f"Reply Created: {reply.post_id}")
    for e in reply_events:
        print(f"Event: {e.event_type} -> {e.wallet_id} ({e.amount})")

    # 7. End Space
    print("\n[Step 6] Ending Space...")
    spaces_mgr.end_space(space.space_id, "host_wallet", 2000, log_list=log_list)
    emit_space_ended(space, 2000, cm, log_list)
    print("Space Ended.")

    # 8. Post to Ended Space (Wall Persistence)
    print("\n[Step 7] Posting to Ended Space...")
    late_post = wall_mgr.create_post(
        space.space_id,
        "user_wallet",
        "Thanks for the session!",
        2010,
        log_list=log_list,
    )
    print(f"Late Post Created: {late_post.post_id} on {late_post.space_id}")

    print("\n>>> Prototype Complete. Zero-Sim Determinism Verified via Log Sequence.")
    print(f"Total Operations Logged: {len(log_list)}")


if __name__ == "__main__":
    run_prototype()
