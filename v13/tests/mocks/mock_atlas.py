import asyncio
from typing import Dict, Any, Optional
from v13.libs.canonical.models import ContentMetadata, ContentType


class MockAtlasFrontend:
    """
    Simulates the ATLAS user interface creating content.
    """

    def create_post(
        self, content_id: str, author_id: str, data: Dict[str, Any]
    ) -> ContentMetadata:
        """
        Generate a ContentMetadata object as if originating from the UI.
        """
        return ContentMetadata(
            content_id=content_id,
            author_id=author_id,
            timestamp=1234567890,  # Deterministic Mock Time
            type=ContentType.POST,
            attributes=data,
        )
