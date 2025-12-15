
import os
import json
import logging
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone

# Optional Redis import
try:
    import redis
except ImportError:
    redis = None

from v13.ledger.genesis_ledger import GenesisLedger

logger = logging.getLogger(__name__)

class EventBridge:
    """
    Bridge between ATLAS application events and the persistent Genesis Ledger.
    Supports local synchronous logging or asynchronous Redis Streams based logging.
    """
    def __init__(self, ledger: GenesisLedger, redis_url: Optional[str] = None, stream_key: str = "atlas_events"):
        self.ledger = ledger
        self.stream_key = stream_key
        self.redis_client = None
        
        # Initialize Redis if URL provided and generic Redis lib available
        if redis_url and redis:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info(f"EventBridge connected to Redis at {redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to synchronous mode.")

    def publish_event(self, 
                      event_type: str, 
                      wallet: str, 
                      metadata: Dict[str, Any], 
                      signature: str, 
                      value: int = 0) -> str:
        """
        Publish an event. 
        If Redis is active, pushes to Redis Stream (to be consumed by a worker).
        If Redis is inactive, writes directly to GenesisLedger (blocking/synchronous).
        
        Returns:
            Event ID (Redis Message ID or Ledger Event ID)
        """
        payload = {
            "event_type": event_type,
            "wallet": wallet,
            "metadata": metadata,
            "signature": signature,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": str(uuid.uuid4())
        }
        
        if self.redis_client:
            try:
                # Add to Redis Stream
                # Redis expects flat dict of strings/bytes usually, so we json dump complex fields if needed
                # For simplicity here we dump the whole thing as 'data'
                msg_id = self.redis_client.xadd(self.stream_key, {"json": json.dumps(payload)})
                return str(msg_id)
            except Exception as e:
                logger.error(f"Redis publish failed: {e}. Falling back to local ledger.")
        
        # Fallback / Local Mode: Write directly to ledger
        event = self.ledger.append_event(
            event_type=event_type,
            wallet=wallet,
            metadata=metadata,
            signature=signature,
            value=value
        )
        return event.id

    def consume_and_persist(self, count: int = 10, block_ms: int = 1000):
        """
        Worker method: Consumes events from Redis Stream and persists them to GenesisLedger.
        Should be run in a separate worker process if Redis is enabled.
        """
        if not self.redis_client:
            return 0
            
        # Read from stream
        # This is a simplified consumer group or direct read logic
        # For V1 simplicity, we'll assume a single consumer reading new entries ($) or keeping track of ID
        # Here we just demo the logic for "last_id" tracking would be needed in real prod
        
        # In a real worker, we'd use XREADGROUP
        pass # Placeholder for worker logic

    def replay_events(self, start_time: Optional[datetime] = None, filter_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Replay events from the ledger directly.
        """
        # Minimal implementation reading specific implementation from ledger file is inefficient
        # but satisfies V1 functional requirements
        events = []
        # Accessing private path of ledger is not ideal but pragmatic for this bridge
        if os.path.exists(self.ledger.storage_path):
             with open(self.ledger.storage_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        record = json.loads(line)
                        # TODO: proper timestamp parsing/filtering
                        if filter_func:
                            if filter_func(record):
                                events.append(record)
                        else:
                            events.append(record)
                    except:
                        pass
        return events

# Singleton factory
_bridge_instance = None

def get_event_bridge(ledger: Optional[GenesisLedger] = None) -> EventBridge:
    global _bridge_instance
    if _bridge_instance is None:
        if ledger is None:
             raise ValueError("Ledger must be provided for initial bridge setup")
        
        redis_url = os.getenv("REDIS_URL")
        _bridge_instance = EventBridge(ledger, redis_url)
    return _bridge_instance
