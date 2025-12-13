"""
ATLAS API Gateway - Entry point for all ATLAS API endpoints
"""
import hashlib
import json
from typing import Dict, Any, List, Optional
from .models import FeedRequest, FeedResponse, FeedPost, InteractionRequest, InteractionResponse, GuardResults, RewardEstimate, ErrorResponse

# Import QFS components with proper error handling
try:
    # Try relative imports first (for package usage)
    from ..libs.CertifiedMath import CertifiedMath, BigNum128
    from ..core.CoherenceEngine import CoherenceEngine
    from ..core.CoherenceLedger import CoherenceLedger, LedgerEntry
    from ..core.TokenStateBundle import TokenStateBundle
    from ..libs.governance.TreasuryEngine import TreasuryEngine
    from ..libs.governance.RewardAllocator import RewardAllocator
    from ..libs.economics.EconomicsGuard import EconomicsGuard
    from ..libs.DeterministicTime import DeterministicTime
    # Import new P1 components
    from ..guards.AEGISGuard import AEGISGuard
    from ..services.notification_service import NotificationService
    from ..auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        from src.core.CoherenceEngine import CoherenceEngine
        from src.core.CoherenceLedger import CoherenceLedger, LedgerEntry
        from src.core.TokenStateBundle import TokenStateBundle
        from src.libs.governance.TreasuryEngine import TreasuryEngine
        from src.libs.governance.RewardAllocator import RewardAllocator
        from src.libs.economics.EconomicsGuard import EconomicsGuard
        from src.libs.DeterministicTime import DeterministicTime
        # Import new P1 components
        from src.guards.AEGISGuard import AEGISGuard
        from src.services.notification_service import NotificationService
        from src.auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.CoherenceEngine import CoherenceEngine
        from core.CoherenceLedger import CoherenceLedger, LedgerEntry
        from core.TokenStateBundle import TokenStateBundle
        from libs.governance.TreasuryEngine import TreasuryEngine
        from libs.governance.RewardAllocator import RewardAllocator
        from libs.economics.EconomicsGuard import EconomicsGuard
        from libs.DeterministicTime import DeterministicTime
        # Import new P1 components
        from guards.AEGISGuard import AEGISGuard
        from services.notification_service import NotificationService
        from auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType


class AtlasAPIGateway:
    """
    Main API gateway for ATLAS x QFS integration.
    
    This gateway connects ATLAS API endpoints to the actual QFS modules,
    providing real integration with CoherenceEngine, CoherenceLedger,
    TreasuryEngine, and EconomicsGuard while preserving determinism.
    """

    def __init__(self):
        """Initialize the API gateway with QFS components"""
        # Initialize core QFS components
        self.cm = CertifiedMath()
        self.coherence_engine = CoherenceEngine(self.cm)
        self.treasury_engine = TreasuryEngine(self.cm)
        self.reward_allocator = RewardAllocator(self.cm)
        self.economics_guard = EconomicsGuard(self.cm)
        self.coherence_ledger = CoherenceLedger(self.cm)
        
        # Initialize P1 components
        self.aegis_guard = AEGISGuard(self.cm)
        self.notification_service = NotificationService(self.cm)
        self.open_agi_enforcer = OPENAGIRoleEnforcer(self.cm)
        
        # For now, we'll use a mock token bundle for testing
        # In a real implementation, this would be fetched from storage
        self.mock_token_bundle = self._create_mock_token_bundle()

    def get_feed(self, request: FeedRequest) -> FeedResponse:
        """
        Get coherence-ranked content feed by calling the CoherenceEngine.
        
        Args:
            request: FeedRequest object with user context and parameters
            
        Returns:
            FeedResponse with ranked posts and policy metadata
        """
        try:
            # Validate request shape
            if not self._validate_request_shape(request):
                return FeedResponse(
                    posts=[],
                    next_cursor=None,
                    policy_metadata={
                        "version": "INVALID_REQUEST",
                        "status": "REQUEST_VALIDATION_FAILED"
                    }
                )
            
            # For demonstration purposes, we'll create mock post IDs and features
            # In a real implementation, these would come from a database or other storage
            mock_post_ids = ["post_1", "post_2", "post_3", "post_4", "post_5"]
            mock_features = [
                [BigNum128.from_int(1), BigNum128.from_int(2), BigNum128.from_int(3)],
                [BigNum128.from_int(2), BigNum128.from_int(3), BigNum128.from_int(4)],
                [BigNum128.from_int(3), BigNum128.from_int(4), BigNum128.from_int(5)],
                [BigNum128.from_int(4), BigNum128.from_int(5), BigNum128.from_int(6)],
                [BigNum128.from_int(5), BigNum128.from_int(6), BigNum128.from_int(7)]
            ]
            
            # Create mock I_vector (feedback vector) for demonstration
            mock_i_vector = [
                BigNum128.from_int(1),
                BigNum128.from_int(2),
                BigNum128.from_int(3)
            ]
            
            # Get deterministic timestamp (in a real implementation, this would come from a DRV packet)
            deterministic_timestamp = 1234567890
            
            # Call CoherenceEngine to rank posts
            ranked_posts = []
            for i, post_id in enumerate(mock_post_ids):
                # Update omega for each post using CoherenceEngine
                updated_omega = self.coherence_engine.update_omega(
                    features=mock_features[i] if i < len(mock_features) else [],
                    I_vector=mock_i_vector,
                    L=f"L_{post_id}",
                    log_list=[],  # In a real implementation, this would be a shared log
                    pqc_cid=f"feed_rank_{post_id}",
                    deterministic_timestamp=deterministic_timestamp
                )
                
                # Calculate coherence score (norm of updated omega)
                coherence_score = self._calculate_coherence_score(updated_omega)
                
                # Create FeedPost object
                feed_post = FeedPost(
                    post_id=post_id,
                    coherence_score=coherence_score,
                    policy_version="QFS_V13_FEED_RANKING_POLICY_1.0",
                    why_this_ranking=f"Ranked by CoherenceEngine with features: {len(mock_features[i])}",
                    timestamp=deterministic_timestamp
                )
                ranked_posts.append(feed_post)
            
            # Sort posts by coherence score (descending)
            ranked_posts.sort(key=lambda x: x.coherence_score, reverse=True)
            
            # Apply limit
            if request.limit and request.limit > 0:
                ranked_posts = ranked_posts[:request.limit]
            
            # Return response with real policy metadata
            return FeedResponse(
                posts=ranked_posts,
                next_cursor=None,
                policy_metadata={
                    "version": "QFS_V13_FEED_RANKING_POLICY_1.0",
                    "mode": request.mode,
                    "applied_at": deterministic_timestamp,
                    "engine": "CoherenceEngine",
                    "status": "SUCCESS"
                }
            )
        except Exception as e:
            # Handle any unexpected errors
            return FeedResponse(
                posts=[],
                next_cursor=None,
                policy_metadata={
                    "version": "ERROR",
                    "status": "INTERNAL_ERROR",
                    "error_details": str(e)
                }
            )

    def post_interaction(self, interaction_type: str, request: InteractionRequest) -> InteractionResponse:
        """
        Submit social interaction and process through QFS components.
        
        Args:
            interaction_type: Type of interaction (like, comment, follow, etc.)
            request: InteractionRequest object with interaction details
            
        Returns:
            InteractionResponse with results, guard evaluations, and reward estimates
        """
        try:
            # Validate request shape
            if not self._validate_request_shape(request):
                return InteractionResponse(
                    success=False,
                    event_id=None,
                    guard_results=None,
                    reward_estimate=None
                )
            
            # Get deterministic timestamp (in a real implementation, this would come from a DRV packet)
            deterministic_timestamp = 1234567890
            
            # Create canonical interaction event structure
            interaction_event = {
                "type": interaction_type,
                "user_id": request.user_id,
                "target_id": request.target_id,
                "content": request.content,
                "reason": request.reason,
                "timestamp": deterministic_timestamp
            }
            
            # Generate deterministic event ID
            event_id = self._generate_event_id(interaction_event)
            
            # Emit ledger event via CoherenceLedger
            ledger_entry = self.coherence_ledger.log_state(
                token_bundle=self.mock_token_bundle,
                hsmf_metrics={"interaction_type": interaction_type},
                rewards={"event_id": event_id},
                deterministic_timestamp=deterministic_timestamp
            )
            
            # Process with AEGIS Guard in observation mode
            aegis_observation = self.aegis_guard.observe_event(
                event_type="social_interaction",
                inputs=interaction_event,
                token_bundle=self.mock_token_bundle,
                deterministic_timestamp=deterministic_timestamp
            )
            
            # Process notification
            notification = self.notification_service.process_ledger_entry(ledger_entry)
            
            # Invoke EconomicsGuard (using CHR reward validation as a placeholder for interaction validation)
            economics_validation = self.economics_guard.validate_chr_reward(
                reward_amount=BigNum128.from_int(100),  # Placeholder reward amount
                current_daily_total=BigNum128.from_int(10000),  # Placeholder daily total
                current_total_supply=BigNum128.from_int(1000000),  # Placeholder total supply
                log_list=[]  # In a real implementation, this would be a shared log
            )
            
            # Create guard results
            guard_results = GuardResults(
                safety_guard_passed=True,  # In a real implementation, this would come from SafetyGuard
                economics_guard_passed=economics_validation.passed,
                explanation=economics_validation.error_message if not economics_validation.passed else "Interaction approved by EconomicsGuard"
            )
            
            # Compute reward estimate via TreasuryEngine (simulation-style call)
            reward_estimate = None
            if economics_validation.passed:
                try:
                    # Create mock HSMF metrics for reward calculation
                    hsmf_metrics = {
                        "S_CHR": BigNum128.from_int(1),
                        "C_holo": BigNum128.from_int(1),
                        "Action_Cost_QFS": BigNum128.from_int(1)
                    }
                    
                    # Calculate rewards using TreasuryEngine
                    reward_bundle = self.treasury_engine.calculate_rewards(
                        hsmf_metrics=hsmf_metrics,
                        token_bundle=self.mock_token_bundle,
                        log_list=[],  # In a real implementation, this would be a shared log
                        pqc_cid=f"interaction_reward_{event_id}",
                        deterministic_timestamp=deterministic_timestamp
                    )
                    
                    # Create reward estimate
                    reward_estimate = RewardEstimate(
                        amount=reward_bundle.chr_reward,  # Using CHR reward as example
                        token_type="CHR",
                        explanation=f"Estimated reward for {interaction_type} interaction"
                    )
                except Exception as e:
                    # Handle reward calculation errors
                    reward_estimate = RewardEstimate(
                        amount=BigNum128(0),
                        token_type="NONE",
                        explanation=f"Reward calculation failed: {str(e)}"
                    )
            
            # Return response
            return InteractionResponse(
                success=economics_validation.passed,
                event_id=event_id,
                guard_results=guard_results,
                reward_estimate=reward_estimate
            )
        except Exception as e:
            # Handle any unexpected errors
            return InteractionResponse(
                success=False,
                event_id=None,
                guard_results=GuardResults(
                    safety_guard_passed=False,
                    economics_guard_passed=False,
                    explanation=f"Internal error occurred: {str(e)}"
                ),
                reward_estimate=None
            )

    def get_notifications(self, category: Optional[str] = None, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get notifications by category.
        
        Args:
            category: Optional category filter (social, economic, governance)
            limit: Maximum number of notifications to return
            cursor: Pagination cursor
            
        Returns:
            Dict: Notifications response
        """
        try:
            from ..services.notification_service import NotificationCategory
            
            # Convert category string to enum
            category_enum = None
            if category:
                try:
                    category_enum = NotificationCategory(category.lower())
                except ValueError:
                    return {
                        "error_code": "INVALID_CATEGORY",
                        "message": "Invalid notification category",
                        "details": f"Category must be one of: social, economic, governance"
                    }
            
            # Get notifications from service
            result = self.notification_service.get_notifications(
                category=category_enum,
                limit=limit,
                cursor=cursor
            )
            
            return result
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve notifications",
                "details": str(e)
            }

    def get_unread_notification_counts(self) -> Dict[str, Any]:
        """
        Get unread notification counts per category.
        
        Returns:
            Dict: Unread counts
        """
        try:
            counts = self.notification_service.get_unread_counts()
            return {
                "unread_counts": counts
            }
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve unread counts",
                "details": str(e)
            }

    def authorize_open_agi_action(self, role: str, action_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authorize an OPEN-AGI action.
        
        Args:
            role: OPEN-AGI role
            action_type: Action type
            inputs: Action inputs
            
        Returns:
            Dict: Authorization result
        """
        try:
            # Convert string parameters to enums
            try:
                role_enum = OPENAGIRole(role)
                action_enum = OPENAGIActionType(action_type)
            except ValueError as e:
                return {
                    "error_code": "INVALID_PARAMETERS",
                    "message": "Invalid role or action type",
                    "details": str(e)
                }
            
            # Get deterministic timestamp
            deterministic_timestamp = 1234567890
            
            # Authorize action
            result = self.open_agi_enforcer.authorize_action(
                role=role_enum,
                action_type=action_enum,
                inputs=inputs,
                deterministic_timestamp=deterministic_timestamp
            )
            
            return result
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to authorize OPEN-AGI action",
                "details": str(e)
            }

    def _validate_request_shape(self, request: Any) -> bool:
        """
        Validate basic input shape for requests.
        
        Args:
            request: Request object to validate
            
        Returns:
            bool: True if request shape is valid
        """
        # Basic validation - check that required fields are present
        if hasattr(request, 'user_id') and request.user_id:
            return True
        return False

    def _calculate_coherence_score(self, omega_vector: List[BigNum128]) -> BigNum128:
        """
        Calculate coherence score as the norm of the omega vector.
        
        Args:
            omega_vector: Updated omega vector from CoherenceEngine
            
        Returns:
            BigNum128: Coherence score
        """
        if not omega_vector:
            return BigNum128(0)
        
        # Calculate sum of squares
        sum_squares = BigNum128(0)
        for val in omega_vector:
            val_squared = self.cm.mul(val, val, [])
            sum_squares = self.cm.add(sum_squares, val_squared, [])
        
        # Calculate square root using sqrt(x)
        coherence_score = self.cm.sqrt(sum_squares, 50, [])
        
        return coherence_score

    def _generate_event_id(self, event_data: Dict[str, Any]) -> str:
        """
        Generate deterministic event ID from event data.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            str: Deterministic event ID
        """
        # Serialize event data deterministically
        serialized = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        # Generate SHA-256 hash
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def _create_mock_token_bundle(self) -> TokenStateBundle:
        """
        Create a mock token bundle for testing purposes.
        
        Returns:
            TokenStateBundle: Mock token bundle
        """
        # Import the create_token_state_bundle function
        try:
            from ..core.TokenStateBundle import create_token_state_bundle
        except ImportError:
            try:
                from src.core.TokenStateBundle import create_token_state_bundle
            except ImportError:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from core.TokenStateBundle import create_token_state_bundle
        
        # Create mock token states
        chr_state = {
            "coherence_metric": "0.98",
            "c_holo_proxy": "0.99",
            "resonance_metric": "0.05",
            "flux_metric": "0.15",
            "psi_sync_metric": "0.08",
            "atr_metric": "0.85",
            "balance": "1000.0"
        }
        
        flx_state = {
            "flux_metric": "0.15",
            "balance": "500.0"
        }
        
        psi_sync_state = {
            "psi_sync_metric": "0.08",
            "balance": "250.0"
        }
        
        atr_state = {
            "atr_metric": "0.85",
            "balance": "200.0"
        }
        
        res_state = {
            "resonance_metric": "0.05",
            "balance": "150.0"
        }
        
        nod_state = {
            "nod_metric": "0.5",
            "balance": "100.0"
        }
        
        # Create and return token bundle using the helper function
        return create_token_state_bundle(
            chr_state=chr_state,
            flx_state=flx_state,
            psi_sync_state=psi_sync_state,
            atr_state=atr_state,
            res_state=res_state,
            nod_state=nod_state,
            lambda1=BigNum128(1618033988749894848),  # 1.618033988749894848 * 1e18
            lambda2=BigNum128(618033988749894848),   # 0.618033988749894848 * 1e18
            c_crit=BigNum128.from_int(1),
            pqc_cid="mock_pqc_cid",
            timestamp=1234567890
        )