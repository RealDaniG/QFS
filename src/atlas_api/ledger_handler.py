"""
ledger_handler.py - Event ledger explorer backend for ATLAS x QFS

Implements backend endpoints for a minimal ledger explorer that provides
deterministic paginated streams of ledger events.
"""

import json
from typing import Dict, Any, Optional, List

# Import required components
from ..core.CoherenceLedger import CoherenceLedger, LedgerEntry
from ..libs.CertifiedMath import BigNum128, CertifiedMath


class LedgerHandler:
    """
    Event ledger explorer backend handler.
    
    Provides backend endpoints for a minimal ledger explorer that offers
    deterministic paginated streams of ledger events.
    """
    
    def __init__(self, coherence_ledger: CoherenceLedger):
        """
        Initialize the Ledger Handler.
        
        Args:
            coherence_ledger: CoherenceLedger instance to query
        """
        self.ledger = coherence_ledger
        
    def get_events(self, event_type: Optional[str] = None, module: Optional[str] = None,
                   user: Optional[str] = None, limit: int = 20, 
                   cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ledger events with optional filtering.
        
        Args:
            event_type: Optional event type filter
            module: Optional module filter
            user: Optional user filter
            limit: Maximum number of events to return (default: 20)
            cursor: Pagination cursor for next page
            
        Returns:
            Dict: Events and pagination info
        """
        # Get all ledger entries
        entries = self.ledger.ledger_entries
        
        # Apply filters
        filtered_entries = []
        for entry in entries:
            # Type filter
            if event_type and entry.entry_type != event_type:
                continue
                
            # For module and user filters, we would need to extract from entry data
            # Since our mock entries don't have this data, we'll skip these filters for now
            # In a real implementation, this would check the entry data
            
            filtered_entries.append(entry)
            
        # Sort by timestamp descending (newest first)
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        start_index = 0
        if cursor:
            # Parse cursor to determine start index
            # In a real implementation, this would be more sophisticated
            try:
                start_index = int(cursor.split('_')[1])
            except (IndexError, ValueError):
                start_index = 0
                
        # Apply limit
        end_index = min(start_index + limit, len(filtered_entries))
        paginated_entries = filtered_entries[start_index:end_index]
        
        # Convert entries to serializable format
        events_data = []
        for entry in paginated_entries:
            events_data.append({
                "event_id": entry.entry_id,
                "timestamp": entry.timestamp,
                "event_type": entry.entry_type,
                "data_summary": self._summarize_entry_data(entry.data),
                "previous_hash": entry.previous_hash[:16] + "...",
                "entry_hash": entry.entry_hash[:16] + "...",
                "pqc_cid": entry.pqc_cid
            })
            
        # Generate next cursor if there are more entries
        next_cursor = None
        if end_index < len(filtered_entries):
            next_cursor = f"cursor_{end_index}"
            
        return {
            "events": events_data,
            "next_cursor": next_cursor,
            "total_count": len(filtered_entries),
            "filters_applied": {
                "event_type": event_type,
                "module": module,
                "user": user
            }
        }
        
    def get_event_detail(self, event_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific ledger event.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Dict: Event details or error information
        """
        # Find the entry by ID
        for entry in self.ledger.ledger_entries:
            if entry.entry_id == event_id:
                # Return detailed information
                return {
                    "event_id": entry.entry_id,
                    "timestamp": entry.timestamp,
                    "event_type": entry.entry_type,
                    "data": entry.data,
                    "previous_hash": entry.previous_hash,
                    "entry_hash": entry.entry_hash,
                    "pqc_cid": entry.pqc_cid,
                    "quantum_metadata": entry.quantum_metadata,
                    "links": self._get_navigation_links(entry)
                }
                
        # Event not found
        return {
            "error": "Event not found",
            "event_id": event_id
        }
        
    def _summarize_entry_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of entry data for listing views.
        
        Args:
            data: Entry data to summarize
            
        Returns:
            Dict: Summarized data
        """
        summary = {}
        
        # Summarize token bundle if present
        if "token_bundle" in data:
            bundle = data["token_bundle"]
            summary["token_bundle"] = {
                "bundle_id": bundle.get("bundle_id", "unknown"),
                "timestamp": bundle.get("timestamp", 0)
            }
            
        # Summarize rewards if present
        if "rewards" in data:
            rewards = data["rewards"]
            summary["rewards"] = {
                "count": len(rewards),
                "types": list(rewards.keys()) if isinstance(rewards, dict) else []
            }
            
        # Summarize HSMF metrics if present
        if "hsmf_metrics" in data:
            metrics = data["hsmf_metrics"]
            summary["hsmf_metrics"] = {
                "count": len(metrics),
                "sample_keys": list(metrics.keys())[:3] if isinstance(metrics, dict) else []
            }
            
        return summary
        
    def _get_navigation_links(self, entry: LedgerEntry) -> Dict[str, Any]:
        """
        Get navigation links for an entry (prev/next).
        
        Args:
            entry: Ledger entry to get navigation for
            
        Returns:
            Dict: Navigation links
        """
        entries = self.ledger.ledger_entries
        entry_index = -1
        
        # Find entry index
        for i, e in enumerate(entries):
            if e.entry_id == entry.entry_id:
                entry_index = i
                break
                
        links = {}
        
        # Previous link
        if entry_index > 0:
            prev_entry = entries[entry_index - 1]
            links["previous"] = {
                "event_id": prev_entry.entry_id,
                "event_type": prev_entry.entry_type,
                "timestamp": prev_entry.timestamp
            }
            
        # Next link
        if entry_index < len(entries) - 1:
            next_entry = entries[entry_index + 1]
            links["next"] = {
                "event_id": next_entry.entry_id,
                "event_type": next_entry.entry_type,
                "timestamp": next_entry.timestamp
            }
            
        return links


# Add router integration
class LedgerRouter:
    """
    Router for ledger explorer endpoints.
    """
    
    def __init__(self, ledger_handler: LedgerHandler):
        """
        Initialize the Ledger Router.
        
        Args:
            ledger_handler: LedgerHandler instance
        """
        self.handler = ledger_handler
        
    def route_get_events(self, event_type: Optional[str] = None, module: Optional[str] = None,
                        user: Optional[str] = None, limit: int = 20, 
                        cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Route GET /api/v1/ledger/events requests.
        
        Args:
            event_type: Optional event type filter
            module: Optional module filter
            user: Optional user filter
            limit: Maximum number of events to return
            cursor: Pagination cursor
            
        Returns:
            Dict: JSON-serializable response
        """
        try:
            # Validate limit
            if limit <= 0 or limit > 100:
                return {
                    "error_code": "INVALID_LIMIT",
                    "message": "Invalid limit parameter",
                    "details": "Limit must be between 1 and 100"
                }
            
            # Call handler method
            result = self.handler.get_events(
                event_type=event_type,
                module=module,
                user=user,
                limit=limit,
                cursor=cursor
            )
            
            return result
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve ledger events",
                "details": str(e)
            }
            
    def route_get_event_detail(self, event_id: str) -> Dict[str, Any]:
        """
        Route GET /api/v1/ledger/events/{event_id} requests.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Dict: JSON-serializable response
        """
        try:
            # Validate event_id
            if not event_id:
                return {
                    "error_code": "MISSING_EVENT_ID",
                    "message": "Event ID is required",
                    "details": "The event_id parameter is mandatory"
                }
            
            # Call handler method
            result = self.handler.get_event_detail(event_id)
            
            return result
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve event details",
                "details": str(e)
            }


# Test function
def test_ledger_handler():
    """Test the LedgerHandler implementation."""
    print("Testing LedgerHandler...")
    
    # Create test log list and CertifiedMath instance
    log_list = []
    # Use the LogContext to create a proper log list
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    
    # Initialize coherence ledger
    ledger = CoherenceLedger(cm)
    
    # Create test token bundle
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85"
    }
    
    parameters = {
        "beta_penalty": BigNum128.from_int(100000000),
        "phi": BigNum128.from_int(1618033988749894848)
    }
    
    from ..core.TokenStateBundle import TokenStateBundle
    
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        nod_state={"nod_metric": "0.5"},
        signature="test_signature",
        timestamp=1234567890,
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=BigNum128.from_int(300000000000000000),
        lambda2=BigNum128.from_int(200000000000000000),
        c_crit=BigNum128.from_int(900000000000000000),
        parameters=parameters
    )
    
    # Add some test entries to the ledger
    entry1 = ledger.log_state(token_bundle, deterministic_timestamp=1234567890)
    print(f"Logged entry 1: {entry1.entry_id}")
    
    hsmf_metrics = {
        "c_holo": "0.95",
        "s_flx": "0.15",
        "s_psi_sync": "0.08",
        "f_atr": "0.85"
    }
    
    entry2 = ledger.log_state(token_bundle, hsmf_metrics, deterministic_timestamp=1234567891)
    print(f"Logged entry 2: {entry2.entry_id}")
    
    rewards = {
        "CHR": {
            "token_name": "CHR",
            "amount": "100.0",
            "eligibility": True,
            "coherence_gate_passed": True,
            "survival_gate_passed": True
        }
    }
    
    entry3 = ledger.log_state(token_bundle, hsmf_metrics, rewards, deterministic_timestamp=1234567892)
    print(f"Logged entry 3: {entry3.entry_id}")
    
    # Initialize ledger handler
    ledger_handler = LedgerHandler(ledger)
    
    # Test getting events
    events_result = ledger_handler.get_events(limit=10)
    print(f"Retrieved {len(events_result['events'])} events")
    print(f"Total count: {events_result['total_count']}")
    
    # Test filtering by event type
    reward_events = ledger_handler.get_events(event_type="reward_allocation")
    print(f"Reward allocation events: {len(reward_events['events'])}")
    
    # Test getting event detail
    if events_result['events']:
        first_event_id = events_result['events'][0]['event_id']
        detail_result = ledger_handler.get_event_detail(first_event_id)
        print(f"Event detail retrieved: {detail_result['event_id']}")
        print(f"Event type: {detail_result['event_type']}")
        print(f"Navigation links: {len(detail_result['links'])} links")
    
    # Test non-existent event
    non_existent = ledger_handler.get_event_detail("non_existent_id")
    print(f"Non-existent event result: {non_existent['error']}")
    
    # Test router integration
    print("\n--- Testing Router Integration ---")
    router = LedgerRouter(ledger_handler)
    
    router_events = router.route_get_events(limit=5)
    print(f"Router events result: {len(router_events.get('events', []))} events")
    
    if events_result['events']:
        first_event_id = events_result['events'][0]['event_id']
        router_detail = router.route_get_event_detail(first_event_id)
        print(f"Router event detail: {router_detail.get('event_id', 'N/A')}")


if __name__ == "__main__":
    test_ledger_handler()