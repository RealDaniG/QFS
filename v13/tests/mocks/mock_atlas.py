from typing import Dict, Any
from v13.libs.deterministic_helpers import det_time_now
from v13.libs.canonical.models import ContentMetadata, ContentType


class MockAtlasFrontend:
    """
    Simulates the ATLAS user interface creating content.
    Uses deterministic timestamp for Zero-Sim compliance.
    """

    def create_post(
        self,
        content_id: str,
        author_id: str,
        data: Dict[str, Any],
        tts_timestamp: int = None,
    ) -> ContentMetadata:
        """
        Generate a ContentMetadata object as if originating from the UI.

        Args:
            tts_timestamp: Deterministic timestamp from DRV context. If None, uses det_time_now().
        """
        timestamp = tts_timestamp if tts_timestamp is not None else det_time_now()
        return ContentMetadata(
            content_id=content_id,
            author_id=author_id,
            timestamp=timestamp,
            type=ContentType.POST,
            attributes=data,
        )
