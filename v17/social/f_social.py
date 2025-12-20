"""
Social F-Layer (v17)

Deterministic functions for threads and comments.
"""

import hashlib
from typing import Dict, List, Optional, Any
from v15.evidence.bus import EvidenceBus
from v17.social.schemas import Thread, Comment, ThreadState, Dispute
from pydantic import ValidationError


def create_thread(
    space_id: str,
    title: str,
    created_by: str,
    timestamp: int,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Thread:
    """Create a new deterministic thread."""
    thread_id = _generate_thread_id(space_id, created_by, title, timestamp)

    thread = Thread(
        thread_id=thread_id,
        space_id=space_id,
        title=title,
        created_by=created_by,
        created_at=timestamp,
        reference_id=reference_id,
        reference_type=reference_type,
        metadata=metadata or {},
    )

    EvidenceBus.emit(
        "SOCIAL_THREAD_CREATED", {"thread": thread.model_dump(), "timestamp": timestamp}
    )

    return thread


def post_comment(
    thread_id: str,
    author_wallet: str,
    content: str,
    timestamp: int,
    reply_to_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Comment:
    """Post a deterministic comment."""
    comment_id = _generate_comment_id(thread_id, author_wallet, timestamp, content)

    comment = Comment(
        comment_id=comment_id,
        thread_id=thread_id,
        author_wallet=author_wallet,
        content=content,
        timestamp=timestamp,
        reply_to_id=reply_to_id,
        metadata=metadata or {},
    )

    EvidenceBus.emit(
        "SOCIAL_COMMENT_POSTED",
        {"comment": comment.model_dump(), "timestamp": timestamp},
    )

    return comment


def create_dispute(
    target_id: str,
    target_type: str,
    raised_by: str,
    reason: str,
    timestamp: int,
) -> Dispute:
    """Raise a formal dispute."""
    dispute_id = _generate_dispute_id(target_id, raised_by, timestamp)

    dispute = Dispute(
        dispute_id=dispute_id,
        target_id=target_id,
        target_type=target_type,
        raised_by=raised_by,
        reason=reason,
        timestamp=timestamp,
        status="OPEN",
    )

    EvidenceBus.emit(
        "SOCIAL_DISPUTE_OPENED",
        {"dispute": dispute.model_dump(), "timestamp": timestamp},
    )

    return dispute


def get_thread_state(
    thread_id: str, events: Optional[List[Dict[str, Any]]] = None
) -> Optional[ThreadState]:
    """Reconstruct thread state from events."""
    if events is None:
        events = EvidenceBus.get_events(limit=1_000_000)

    thread_data = None
    comments = []

    for envelope in events:
        if not isinstance(envelope, dict):
            continue
        event = envelope.get("event", {})
        if not isinstance(event, dict):
            continue

        etype = event.get("type")
        payload = event.get("payload", {})

        if etype == "SOCIAL_THREAD_CREATED":
            t = payload.get("thread", {})
            if isinstance(t, dict) and t.get("thread_id") == thread_id:
                thread_data = t

        elif etype == "SOCIAL_COMMENT_POSTED":
            c = payload.get("comment", {})
            if isinstance(c, dict) and c.get("thread_id") == thread_id:
                comments.append(c)

    if not thread_data:
        return None

    try:
        thread = Thread(**thread_data)
    except ValidationError:
        return None

    comment_objs = []
    for c in comments:
        try:
            comment_objs.append(Comment(**c))
        except ValidationError:
            continue

    # Sort comments by timestamp
    comment_objs.sort(key=lambda x: x.timestamp)

    return ThreadState(thread=thread, comments=comment_objs)


def _generate_thread_id(space_id: str, creator: str, title: str, ts: int) -> str:
    canonical = f"{space_id}:{creator}:{title}:{ts}"
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"thread_{space_id}_{ts}_{h}"


def _generate_comment_id(thread_id: str, author: str, ts: int, content: str) -> str:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
    canonical = f"{thread_id}:{author}:{ts}:{content_hash}"
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"comment_{ts}_{h}"


def _generate_dispute_id(target_id: str, raiser: str, ts: int) -> str:
    canonical = f"{target_id}:{raiser}:{ts}"
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"dispute_{ts}_{h}"
