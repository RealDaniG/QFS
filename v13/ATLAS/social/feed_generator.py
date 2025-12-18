"""
ATLAS Social Feed Generator
Parses raw EconomicEvents and logic logs to build user feeds.
"""

from typing import List, Dict, Any, Optional
from .feed_models import FeedItem, UserFeed, SpaceDashboard


class FeedGenerator:
    """
    Read-only aggregator for generating social views.
    """

    @staticmethod
    def generate_user_feed(
        user_wallet: str,
        events: List[Any],  # EconomicEvent or dict
        current_time: int,
    ) -> UserFeed:
        """
        Scan events for items relevant to the user.
        Relevant = Posted by user, Replied to user, or Space event user is in.
        For Phase VI MVP: Just trace 'creation' events for now.
        """
        feed_items = []

        # We assume 'events' is a mixed list of objects or dicts.
        # In a real system, we'd query a DB. Here we scan the memory log.

        for evt in events:
            # Handle EconomicEvent objects
            if hasattr(evt, "event_type"):
                e_type = evt.event_type
                e_id = evt.event_id
                e_wallet = evt.wallet_id
                e_meta = evt.metadata or {}
                e_time = evt.timestamp
            # Handle dict logs (from logic layers)
            elif isinstance(evt, dict):
                e_type = evt.get("event_type", evt.get("operation", "unknown"))
                e_id = evt.get(
                    "event_id", evt.get("session_id", evt.get("post_id", "unknown"))
                )
                e_wallet = evt.get(
                    "wallet_id", evt.get("owner", evt.get("author", "unknown"))
                )
                e_meta = evt
                e_time = evt.get("timestamp", 0)
            else:
                continue

            # Filtering Logic
            if e_type == "wall_post_created":
                # Add to feed if user is author or (future) follower
                if e_wallet == user_wallet:
                    feed_items.append(
                        FeedItem(
                            item_id=e_id,
                            item_type="wall_post",
                            timestamp=e_time,
                            source_id=e_meta.get("space_id", ""),
                            author_wallet=e_wallet,
                            summary_text="Created a wall post",
                            metadata=e_meta,
                        )
                    )

            elif e_type in ["chat_created", "chat_session_created"]:
                if e_wallet == user_wallet:  # Owner
                    feed_items.append(
                        FeedItem(
                            item_id=e_id,
                            item_type="chat_session",
                            timestamp=e_time,
                            source_id=e_meta.get("session_id", e_id),
                            author_wallet=e_wallet,
                            summary_text="Started a secure chat",
                            metadata=e_meta,
                        )
                    )

        # Sort by time desc
        feed_items.sort(key=lambda x: x.timestamp, reverse=True)

        return UserFeed(
            user_wallet=user_wallet, generated_at=current_time, items=feed_items
        )

    @staticmethod
    def generate_space_dashboard(
        space_id: str, events: List[Any], current_time: int
    ) -> SpaceDashboard:
        """
        Generate dashboard for a space.
        """
        recent_posts = []
        active_chats = set()
        member_count = 0

        for evt in events:
            # Normalize (similar to above)
            if hasattr(evt, "event_type"):
                e_type = evt.event_type
                e_meta = evt.metadata or {}
                e_time = evt.timestamp
                e_id = evt.event_id
                e_wallet = evt.wallet_id
            elif isinstance(evt, dict):
                e_type = evt.get("event_type", evt.get("operation", "unknown"))
                e_meta = evt
                e_time = evt.get("timestamp", 0)
                e_id = evt.get("event_id", "")
                e_wallet = evt.get("wallet_id", "")
            else:
                continue

            # Logic
            if e_type == "space_joined":
                if e_meta.get("space_id") == space_id:
                    member_count += 1

            elif e_type == "wall_post_created":
                if e_meta.get("space_id") == space_id:
                    recent_posts.append(
                        FeedItem(
                            item_id=e_id,
                            item_type="wall_post",
                            timestamp=e_time,
                            source_id=space_id,
                            author_wallet=e_wallet,
                            summary_text="New post in space",
                            metadata=e_meta,
                        )
                    )

        recent_posts.sort(key=lambda x: x.timestamp, reverse=True)

        return SpaceDashboard(
            space_id=space_id,
            generated_at=current_time,
            active_member_count=member_count,
            recent_posts=recent_posts,
            active_chats=list(active_chats),
        )
