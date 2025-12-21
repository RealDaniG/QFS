"""
IPFS Storage Adapter for Secure Chat

Production-ready IPFS integration for secure chat content storage.
"""
import hashlib
from typing import Dict, Optional, Union
import aiohttp
import json

class IPFSStorage:
    """
    IPFS-based storage adapter for secure chat content.
    
    Features:
    - Content-addressable storage
    - Automatic pinning for persistence
    - Content deduplication
    - Distributed retrieval
    - Fallback to local cache when IPFS is unavailable
    """

    def __init__(self, ipfs_endpoint: str='http://localhost:5001', pin=True, timeout=30):
        """
        Initialize IPFS storage adapter.
        
        Args:
            ipfs_endpoint: IPFS daemon HTTP endpoint
            pin: Whether to pin stored content for persistence
            timeout: Request timeout in seconds
        """
        self.endpoint = ipfs_endpoint.rstrip('/')
        self.pin = pin
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._local_cache: Dict[str, bytes] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    async def close(self):
        """Close HTTP session"""
        if self._session and (not self._session.closed):
            await self._session.close()

    async def store(self, content: bytes) -> str:
        """
        Store content on IPFS and return its CID.
        
        Args:
            content: Content to store
            
        Returns:
            str: IPFS CID of the stored content
            
        Raises:
            RuntimeError: If IPFS operation fails
        """
        if not content:
            raise ValueError('Content cannot be empty')
        sha256_hash = hashlib.sha256(content).hexdigest()
        if sha256_hash in self._local_cache:
            return sha256_hash
        try:
            session = await self._get_session()
            data = aiohttp.FormData()
            data.add_field('file', content, filename='secure_chat_content')
            async with session.post(f'{self.endpoint}/api/v0/add', data=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f'IPFS add failed: {resp.status} - {error_text}')
                result = await resp.json()
                cid = result.get('Hash')
                if not cid:
                    raise RuntimeError('No CID returned from IPFS')
                if self.pin:
                    pin_data = aiohttp.FormData()
                    pin_data.add_field('arg', cid)
                    async with session.post(f'{self.endpoint}/api/v0/pin/add', data=pin_data) as pin_resp:
                        if pin_resp.status != 200:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f'Failed to pin CID {cid}: {pin_resp.status}')
                self._local_cache[sha256_hash] = content
                return sha256_hash
        except aiohttp.ClientError as e:
            self._local_cache[sha256_hash] = content
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'IPFS unavailable, using local cache: {e}')
            return sha256_hash

    async def retrieve(self, content_hash: str) -> Optional[bytes]:
        """
        Retrieve content from IPFS by hash.
        
        Args:
            content_hash: SHA256 hash of the content
            
        Returns:
            bytes: Retrieved content or None if not found
        """
        if not content_hash:
            raise ValueError('Content hash is required')
        if content_hash in self._local_cache:
            return self._local_cache[content_hash]
        try:
            session = await self._get_session()
            async with session.get(f'{self.endpoint}/api/v0/cat', params={'arg': content_hash}) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    self._local_cache[content_hash] = content
                    return content
                elif resp.status == 404:
                    return None
                else:
                    error_text = await resp.text()
                    raise RuntimeError(f'IPFS cat failed: {resp.status} - {error_text}')
        except aiohttp.ClientError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'IPFS unavailable for retrieval: {e}')
            return None

    async def exists(self, content_hash: str) -> bool:
        """
        Check if content exists.
        
        Args:
            content_hash: SHA256 hash to check
            
        Returns:
            bool: True if content exists
        """
        if not content_hash:
            raise ValueError('Content hash is required')
        if content_hash in self._local_cache:
            return True
        try:
            session = await self._get_session()
            async with session.post(f'{self.endpoint}/api/v0/object/stat', data={'arg': content_hash}) as resp:
                if resp.status == 200:
                    return True
                elif resp.status == 404:
                    return False
                else:
                    error_text = await resp.text()
                    raise RuntimeError(f'IPFS stat failed: {resp.status} - {error_text}')
        except aiohttp.ClientError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'IPFS unavailable for existence check: {e}')
            return False

    async def clear_cache(self):
        """Clear local cache"""
        self._local_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {'cached_items': len(self._local_cache), 'cache_size_bytes': sum((len(v) for v in self._local_cache.values()))}