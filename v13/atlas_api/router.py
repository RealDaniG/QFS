"""
ATLAS API Router - Routes HTTP requests to appropriate handlers
"""
from .gateway import AtlasAPIGateway
from .models import FeedRequest, InteractionRequest, ErrorResponse
from ..auth.open_agi_role import OPENAGIRole, OPENAGIActionType

class AtlasAPIRouter:
    """
    API Router for ATLAS x QFS integration.
    
    Routes incoming HTTP requests to the appropriate handler methods
    in the AtlasAPIGateway.
    """

    def __init__(self):
        """Initialize the API router with a gateway instance"""
        self.gateway = AtlasAPIGateway()

    def route_get_feed(self, user_id: str, cursor: str=None, limit: int=20, mode: str='coherence') -> dict:
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
        try:
            if not user_id:
                return {'error_code': 'MISSING_USER_ID', 'message': 'User ID is required', 'details': 'The user_id parameter is mandatory for feed requests'}
            if limit <= 0 or limit > 100:
                return {'error_code': 'INVALID_LIMIT', 'message': 'Invalid limit parameter', 'details': 'Limit must be between 1 and 100'}
            if mode not in ['coherence', 'chronological']:
                return {'error_code': 'INVALID_MODE', 'message': 'Invalid mode parameter', 'details': "Mode must be either 'coherence' or 'chronological'"}
            request = FeedRequest(user_id=user_id, cursor=cursor, limit=limit, mode=mode)
            response = self.gateway.get_feed(request)
            if response.policy_metadata and response.policy_metadata.get('status') == 'REQUEST_VALIDATION_FAILED':
                return {'error_code': 'REQUEST_VALIDATION_FAILED', 'message': 'Request validation failed', 'details': response.policy_metadata.get('version', 'Invalid request')}
            posts_data = []
            for post in sorted(response.posts):
                posts_data.append({'post_id': post.post_id, 'coherence_score': post.coherence_score.to_decimal_string(), 'policy_version': post.policy_version, 'why_this_ranking': post.why_this_ranking, 'timestamp': post.timestamp})
            return {'posts': posts_data, 'next_cursor': response.next_cursor, 'policy_metadata': response.policy_metadata}
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_post_interaction(self, interaction_type: str, user_id: str, target_id: str, content: str=None, reason: str=None) -> dict:
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
        try:
            if not user_id:
                return {'error_code': 'MISSING_USER_ID', 'message': 'User ID is required', 'details': 'The user_id parameter is mandatory for interaction requests'}
            if not target_id:
                return {'error_code': 'MISSING_TARGET_ID', 'message': 'Target ID is required', 'details': 'The target_id parameter is mandatory for interaction requests'}
            valid_interaction_types = ['like', 'comment', 'repost', 'follow', 'report']
            if interaction_type not in valid_interaction_types:
                return {'error_code': 'INVALID_INTERACTION_TYPE', 'message': 'Invalid interaction type', 'details': f"Interaction type must be one of: {', '.join(valid_interaction_types)}"}
            if interaction_type == 'comment' and (not content):
                return {'error_code': 'MISSING_CONTENT', 'message': 'Content is required for comment interactions', 'details': 'The content parameter is mandatory for comment type interactions'}
            if interaction_type == 'report' and (not reason):
                return {'error_code': 'MISSING_REASON', 'message': 'Reason is required for report interactions', 'details': 'The reason parameter is mandatory for report type interactions'}
            request = InteractionRequest(user_id=user_id, target_id=target_id, content=content, reason=reason)
            response = self.gateway.post_interaction(interaction_type, request)
            guard_results_data = None
            if response.guard_results:
                guard_results_data = {'safety_guard_passed': response.guard_results.safety_guard_passed, 'economics_guard_passed': response.guard_results.economics_guard_passed, 'explanation': response.guard_results.explanation}
            reward_estimate_data = None
            if response.reward_estimate:
                reward_estimate_data = {'amount': response.reward_estimate.amount.to_decimal_string(), 'token_type': response.reward_estimate.token_type, 'explanation': response.reward_estimate.explanation}
            return {'success': response.success, 'event_id': response.event_id, 'guard_results': guard_results_data, 'reward_estimate': reward_estimate_data}
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_get_notifications(self, category: str=None, limit: int=20, cursor: str=None) -> dict:
        """
        Route GET /api/v1/notifications requests.
        
        Args:
            category: Optional category filter (social, economic, governance)
            limit: Maximum number of notifications to return
            cursor: Pagination cursor
            
        Returns:
            dict: JSON-serializable response
        """
        try:
            if limit <= 0 or limit > 100:
                return {'error_code': 'INVALID_LIMIT', 'message': 'Invalid limit parameter', 'details': 'Limit must be between 1 and 100'}
            result = self.gateway.get_notifications(category=category, limit=limit, cursor=cursor)
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_get_unread_notification_counts(self) -> dict:
        """
        Route GET /api/v1/notifications/unread requests.
        
        Returns:
            dict: JSON-serializable response with unread counts
        """
        try:
            result = self.gateway.get_unread_notification_counts()
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_authorize_open_agi_action(self, role: str, action_type: str, inputs: dict) -> dict:
        """
        Route POST /api/v1/openagi/authorize requests.
        
        Args:
            role: OPEN-AGI role
            action_type: Action type
            inputs: Action inputs
            
        Returns:
            dict: JSON-serializable response
        """
        try:
            if not role:
                return {'error_code': 'MISSING_ROLE', 'message': 'Role is required', 'details': 'The role parameter is mandatory'}
            if not action_type:
                return {'error_code': 'MISSING_ACTION_TYPE', 'message': 'Action type is required', 'details': 'The action_type parameter is mandatory'}
            result = self.gateway.authorize_open_agi_action(role=role, action_type=action_type, inputs=inputs)
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_get_governance_dashboard(self, start_timestamp: int=None, end_timestamp: int=None, role: str=None) -> dict:
        """
        Route GET /api/v1/governance/dashboard requests.
        
        Args:
            start_timestamp: Optional start timestamp for filtering
            end_timestamp: Optional end timestamp for filtering
            role: Operator role for authorization
            
        Returns:
            dict: JSON-serializable response with governance dashboard summary
        """
        try:
            if not role:
                return {'error_code': 'MISSING_ROLE', 'message': 'Role is required', 'details': 'The role parameter is mandatory for governance dashboard access'}
            try:
                open_agi_role = OPENAGIRole(role)
                if open_agi_role not in [OPENAGIRole.SYSTEM, OPENAGIRole.PROPOSER]:
                    return {'error_code': 'UNAUTHORIZED_ROLE', 'message': 'Unauthorized role for governance dashboard', 'details': 'Only SYSTEM and PROPOSER roles can access governance dashboard'}
            except ValueError:
                return {'error_code': 'INVALID_ROLE', 'message': 'Invalid role', 'details': f"Role '{role}' not recognized"}
            auth_result = self.gateway.open_agi_enforcer.authorize_action(role=open_agi_role, action_type=OPENAGIActionType.READ_STATE, inputs={'dashboard_access': True}, deterministic_timestamp=self.gateway._get_deterministic_timestamp())
            if not auth_result.get('authorized', False):
                return {'error_code': 'UNAUTHORIZED', 'message': 'Access denied', 'details': auth_result.get('reason', 'Not authorized to access governance dashboard')}
            start_ts = None
            end_ts = None
            if start_timestamp is not None:
                try:
                    start_ts = int(start_timestamp)
                except (ValueError, TypeError):
                    return {'error_code': 'INVALID_TIMESTAMP', 'message': 'Invalid start timestamp', 'details': 'Start timestamp must be a valid integer'}
            if end_timestamp is not None:
                try:
                    end_ts = int(end_timestamp)
                except (ValueError, TypeError):
                    return {'error_code': 'INVALID_TIMESTAMP', 'message': 'Invalid end timestamp', 'details': 'End timestamp must be a valid integer'}
            result = self.gateway.get_governance_dashboard(start_timestamp=start_ts, end_timestamp=end_ts)
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_get_correlated_observations(self, content_id: str=None, event_id: str=None) -> dict:
        """
        Route GET /api/v1/observations/correlated requests.
        
        Args:
            content_id: Optional content ID to filter by
            event_id: Optional event ID to filter by
            
        Returns:
            dict: JSON-serializable response with correlated observations
        """
        try:
            result = self.gateway.get_correlated_observations(content_id=content_id, event_id=event_id)
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}

    def route_submit_agi_observation(self, role: str, action_type: str, inputs: dict, suggested_changes: dict, explanation: str, correlation_to_aegis: dict=None) -> dict:
        """
        Route POST /api/v1/openagi/observation requests.
        
        Args:
            role: OPEN-AGI role
            action_type: Action type (e.g., policy_recommendation, threshold_adjustment)
            inputs: Observation inputs (referenced content/interaction IDs)
            suggested_changes: Suggested policy/threshold changes
            explanation: Explanation of the recommendation
            correlation_to_aegis: Optional correlation to AEGIS observations
            
        Returns:
            dict: JSON-serializable response
        """
        try:
            if not role:
                return {'error_code': 'MISSING_ROLE', 'message': 'Role is required', 'details': 'The role parameter is mandatory'}
            if not action_type:
                return {'error_code': 'MISSING_ACTION_TYPE', 'message': 'Action type is required', 'details': 'The action_type parameter is mandatory'}
            if not inputs or not isinstance(inputs, dict):
                return {'error_code': 'MISSING_INPUTS', 'message': 'Inputs are required', 'details': 'The inputs parameter is mandatory and must be a dictionary'}
            if not suggested_changes or not isinstance(suggested_changes, dict):
                return {'error_code': 'MISSING_SUGGESTED_CHANGES', 'message': 'Suggested changes are required', 'details': 'The suggested_changes parameter is mandatory and must be a dictionary'}
            if not explanation or not explanation.strip():
                return {'error_code': 'MISSING_EXPLANATION', 'message': 'Explanation is required', 'details': 'The explanation parameter is mandatory and cannot be empty'}
            result = self.gateway.submit_agi_observation(role=role, action_type=action_type, inputs=inputs, suggested_changes=suggested_changes, explanation=explanation, correlation_to_aegis=correlation_to_aegis)
            return result
        except Exception as e:
            return {'error_code': 'INTERNAL_ERROR', 'message': 'An internal error occurred', 'details': str(e)}