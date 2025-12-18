"""
Memory-based storage implementation for Secure Chat

For testing and development purposes only.
"""
import hashlib
from typing import Dict, Optional

class MemoryStorage:
    """In-memory storage for testing purposes only"""

    def __init__(self):
        self._store: Dict[str, bytes] = {}

    async def store(self, content: bytes) -> str:
        """Store content and return its hash"""
        if not content:
            raise ValueError('Content cannot be empty')
        content_hash = hashlib.sha256(content).hexdigest()
        self._store[content_hash] = content
        return content_hash

    async def retrieve(self, content_hash: str) -> Optional[bytes]:
        """Retrieve content by hash"""
        if not content_hash:
            raise ValueError('Content hash is required')
        return self._store.get(content_hash)

    async def exists(self, content_hash: str) -> bool:
        """Check if content exists"""
        if not content_hash:
            raise ValueError('Content hash is required')
        return content_hash in self._store
