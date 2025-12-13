"""
ATLAS API Router - Routes HTTP requests to appropriate handlers
"""
from .gateway import AtlasAPIGateway
from .models import FeedRequest, InteractionRequest


class AtlasAPIRouter:
    """
    API Router for ATLAS x QFS integration.
    
    Routes incoming HTTP requests to the appropriate handler methods
    in the AtlasAPIGateway.
    """

    def __init__(self):
        """Initialize the API router with a gateway instance"""
        self.gateway = AtlasAPIGateway()

    def route_get_feed(self, user_id: str, cursor: str = None, limit: int = 20, mode: str = "coherence") -> dict:
        """
        Route GET /api/v1/feed requests.
        
        Args:
            user_id: Authenticated user identifier
            cursor: Pagination cursor for next page
            limit: Number of items to return
            mode: Ranking mode (coherence or chronological)
            
        Returns:
            dict: JSON-serializable response
        """
        # Create request object
        request = FeedRequest(
            user_id=user_id,
            cursor=cursor,
            limit=limit,
            mode=mode
        )
        
        # Call gateway method
        response = self.gateway.get_feed(request)
        
        # Convert to dictionary for JSON serialization
        return {
            "posts": [],
            "next_cursor": response.next_cursor,
            "policy_metadata": response.policy_metadata
        }

    def route_post_interaction(self, interaction_type: str, user_id: str, target_id: str, 
                             content: str = None, reason: str = None) -> dict:
        """
        Route POST /api/v1/interactions/{type} requests.
        
        Args:
            interaction_type: Type of interaction (like, comment, follow, etc.)
            user_id: Authenticated user identifier
            target_id: Target entity identifier
            content: Comment content (for comment type)
            reason: Report reason (for report type)
            
        Returns:
            dict: JSON-serializable response
        """
        # Create request object
        request = InteractionRequest(
            user_id=user_id,
            target_id=target_id,
            content=content,
            reason=reason
        )
        
        # Call gateway method
        response = self.gateway.post_interaction(interaction_type, request)
        
        # Convert to dictionary for JSON serialization
        return {
            "success": response.success,
            "event_id": response.event_id,
            "guard_results": None,
            "reward_estimate": None
        }