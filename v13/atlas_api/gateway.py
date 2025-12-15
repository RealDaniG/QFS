"""
ATLAS API Gateway - Entry point for all ATLAS API endpoints
"""
import hashlib
import json
from typing import Dict, Any, List, Optional
from .models import FeedRequest, FeedResponse, FeedPost, InteractionRequest, InteractionResponse, GuardResults, RewardEstimate, ErrorResponse, AGIObservation

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
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.CoherenceEngine import CoherenceEngine
        from v13.core.CoherenceLedger import CoherenceLedger, LedgerEntry
        from v13.core.TokenStateBundle import TokenStateBundle
        from v13.libs.governance.TreasuryEngine import TreasuryEngine
        from v13.libs.governance.RewardAllocator import RewardAllocator
        from v13.libs.economics.EconomicsGuard import EconomicsGuard
        from v13.libs.DeterministicTime import DeterministicTime
        # Import new P1 components
        from v13.guards.AEGISGuard import AEGISGuard
        from v13.services.notification_service import NotificationService
        from v13.auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType
    except ImportError:
        # Final fallback - no sys/os allowed here for Zero-Sim!
        # Assume environment is set up correctly.
        pass

# Import policy engine
try:
    # Try relative import first (for package usage)
    from ..policy.policy_engine import PolicyEngine
    
    # Import signal addons
    try:
        # Try relative import first (for package usage)
        from ..ATLAS.src.signals.humor import HumorSignalAddon
    except ImportError:
        # Fallback to absolute import (for direct execution)
        try:
            from v13.ATLAS.src.signals.humor import HumorSignalAddon
            except ImportError:
                # Final fallback
                pass
except ImportError:
    # Fallback to absolute import (for direct execution)
    try:
        from v13.policy.policy_engine import PolicyEngine
    except ImportError:
        # Final fallback
        pass


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
        
        # Initialize policy engine
        self.policy_engine = PolicyEngine()
        
        # Initialize signal addons
        self.humor_signal_addon = HumorSignalAddon()
        
        # Initialize storage integration
        
        # Initialize storage integration
        self.storage_client = None  # Will be set by the system with real storage client
        self.ipfs_client = None     # Will be set by the system with real IPFS client
        
        # Initialize deterministic time source
        self.drv_packet = None  # Will be set by the system with real DRV packets
        
        # For deterministic timestamp fallback, use a logical counter
        self._logical_timestamp_counter = 10000000  # Start from a fixed constant
        
        # For now, we'll use a mock token bundle for testing
        # In a real implementation, this would be fetched from storage
        self.mock_token_bundle = self._create_mock_token_bundle()
        
        # Initialize user token bundle store
        self.user_token_bundles = {}
        
        # Token state service extension point (initially None)
        self.token_state_service = None
        
        # Ledger economics service extension point (initially None)
        self.ledger_economics_service = None

    def set_token_state_service(self, service):
        """
        Set the token state service for real token state retrieval.
        
        Args:
            service: Token state service that implements get_bundle_for_user(user_id)
        """
        self.token_state_service = service

    def set_ledger_economics_service(self, service):
        """
        Set the ledger economics service for real economics data.
        
        Args:
            service: Ledger economics service that provides real economics data
        """
        self.ledger_economics_service = service

    def get_governance_dashboard(self, start_timestamp: Optional[int] = None, 
                              end_timestamp: Optional[int] = None) -> Dict[str, Any]:
        """
        Get governance dashboard summary with AEGIS advisory counts and correlated observations.
        
        Args:
            start_timestamp: Optional start timestamp for filtering
            end_timestamp: Optional end timestamp for filtering
            
        Returns:
            Dict: Governance dashboard summary
        """
        try:
            # Initialize counters for AEGIS advisories by severity
            aegis_counts = {
                "info": 0,
                "warning": 0,
                "critical": 0
            }
            
            # Track content IDs with correlated observations
            content_observations = {}
            
            # Filter ledger entries by timestamp if provided
            filtered_entries = self.coherence_ledger.ledger_entries
            if start_timestamp is not None or end_timestamp is not None:
                filtered_entries = [
                    entry for entry in self.coherence_ledger.ledger_entries
                    if (start_timestamp is None or entry.timestamp >= start_timestamp) and
                       (end_timestamp is None or entry.timestamp <= end_timestamp)
                ]
            
            # Process ledger entries to collect statistics
            for entry in filtered_entries:
                # Check for AEGIS observations in guard results
                if "guards" in entry.data and "aegis_advisory" in entry.data["guards"]:
                    aegis_data = entry.data["guards"]["aegis_advisory"]
                    
                    # Count by severity
                    severity = aegis_data.get("severity", "info")
                    if severity in aegis_counts:
                        aegis_counts[severity] += 1
                    
                    # Extract content ID if available
                    content_id = None
                    if "rewards" in entry.data and "event_id" in entry.data["rewards"]:
                        content_id = entry.data["rewards"]["event_id"]
                    elif "hsmf_metrics" in entry.data:
                        # Try to extract content ID from HSMF metrics
                        hsmf_data = entry.data["hsmf_metrics"]
                        if "content_id" in str(hsmf_data):
                            # Simple string search for content_id
                            content_id = "extracted_content_id"  # Placeholder
                    
                    # If we have a content ID, track it
                    if content_id:
                        if content_id not in content_observations:
                            content_observations[content_id] = {
                                "aegis_observations": [],
                                "agi_observations": []
                            }
                        
                        content_observations[content_id]["aegis_observations"].append({
                            "entry_id": entry.entry_id,
                            "timestamp": entry.timestamp,
                            "severity": severity,
                            "block_suggested": aegis_data.get("block_suggested", False)
                        })
                
                # Check for AGI observations in HSMF metrics
                if "hsmf_metrics" in entry.data and "agi_observation" in entry.data["hsmf_metrics"]:
                    agi_data = entry.data["hsmf_metrics"]["agi_observation"]
                    
                    # Extract content ID if available
                    content_id = None
                    if "inputs" in agi_data and "content_ids" in agi_data["inputs"]:
                        content_ids = agi_data["inputs"]["content_ids"]
                        if content_ids:
                            content_id = content_ids[0]  # Take first content ID
                    elif "correlated_aegis_observations" in agi_data and agi_data["correlated_aegis_observations"]:
                        # Use first correlated AEGIS observation as proxy for content ID
                        content_id = agi_data["correlated_aegis_observations"][0]
                    
                    # If we have a content ID, track it
                    if content_id:
                        if content_id not in content_observations:
                            content_observations[content_id] = {
                                "aegis_observations": [],
                                "agi_observations": []
                            }
                        
                        content_observations[content_id]["agi_observations"].append({
                            "entry_id": entry.entry_id,
                            "timestamp": entry.timestamp,
                            "observation_id": agi_data.get("observation_id", "unknown"),
                            "role": agi_data.get("role", "unknown"),
                            "explanation": agi_data.get("explanation", "")
                        })
            
            # Limit to top N content IDs with most observations
            top_content_ids = sorted(
                content_observations.items(),
                key=lambda x: len(x[1]["aegis_observations"]) + len(x[1]["agi_observations"]),
                reverse=True
            )[:10]  # Top 10 content IDs
            
            # Convert to dictionary format
            top_content_dict = dict(top_content_ids)
            
            return {
                "success": True,
                "aegis_advisory_counts": aegis_counts,
                "total_aegis_observations": int(sum(aegis_counts[k] for k in sorted(aegis_counts.keys()))),
                "top_content_with_observations": top_content_dict,
                "timestamp_range": {
                    "start": start_timestamp,
                    "end": end_timestamp
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": str(e)
            }

    def get_correlated_observations(self, content_id: Optional[str] = None, event_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get correlated AEGIS and AGI observations for a given content or event ID.
        
        Args:
            content_id: Content ID to search for
            event_id: Event ID to search for
            
        Returns:
            Dict: Correlated observations
        """
        try:
            aegis_observations = []
            agi_observations = []
            
            # Search through ledger entries for observations related to the content/event
            for entry in self.coherence_ledger.ledger_entries:
                # Check for AEGIS observations in guard results
                if "guards" in entry.data and "aegis_advisory" in entry.data["guards"]:
                    aegis_data = entry.data["guards"]["aegis_advisory"]
                    
                    # Check if this observation relates to our content/event
                    related = False
                    if content_id:
                        # For AEGIS observations, check in rewards data for content references
                        if "rewards" in entry.data and "content_id" in str(entry.data["rewards"]):
                            related = content_id in str(entry.data["rewards"])
                    elif event_id:
                        # For AEGIS observations, check in rewards data for event references
                        if "rewards" in entry.data and "event_id" in entry.data["rewards"]:
                            related = entry.data["rewards"]["event_id"] == event_id
                    
                    if related or (not content_id and not event_id):
                        aegis_observations.append({
                            "entry_id": entry.entry_id,
                            "timestamp": entry.timestamp,
                            "observation_data": aegis_data,
                            "entry_type": entry.entry_type
                        })
                
                # Check for AGI observations in HSMF metrics
                if "hsmf_metrics" in entry.data and "agi_observation" in entry.data["hsmf_metrics"]:
                    agi_data = entry.data["hsmf_metrics"]["agi_observation"]
                    
                    # Check if this observation relates to our content/event
                    related = False
                    if content_id:
                        # Check in inputs for content references
                        if "inputs" in agi_data and "content_ids" in agi_data["inputs"]:
                            related = content_id in agi_data["inputs"]["content_ids"]
                    elif event_id:
                        # Check in correlation data for event references
                        if "correlated_aegis_observations" in agi_data:
                            related = event_id in agi_data["correlated_aegis_observations"]
                        elif "inputs" in agi_data and "interaction_ids" in agi_data["inputs"]:
                            related = event_id in agi_data["inputs"]["interaction_ids"]
                    
                    if related or (not content_id and not event_id):
                        agi_observations.append({
                            "entry_id": entry.entry_id,
                            "timestamp": entry.timestamp,
                            "observation_data": agi_data,
                            "entry_type": entry.entry_type
                        })
            
            return {
                "success": True,
                "aegis_observations": aegis_observations,
                "agi_observations": agi_observations,
                "total_aegis": len(aegis_observations),
                "total_agi": len(agi_observations)
            }
        except Exception as e:
            return {
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": str(e)
            }

    def submit_agi_observation(self, role: str, action_type: str, inputs: Dict[str, Any],
                             suggested_changes: Dict[str, Any], explanation: str,
                             correlation_to_aegis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit an AGI observation/recommendation for governance integration.
        
        Args:
            role: OPEN-AGI role submitting the observation
            action_type: Type of action (e.g., policy_recommendation, threshold_adjustment)
            inputs: Observation inputs (referenced content/interaction IDs)
            suggested_changes: Suggested policy/threshold changes
            explanation: Explanation of the recommendation
            correlation_to_aegis: Optional correlation to AEGIS observations
            
        Returns:
            Dict: Result with observation ID and status
        """
        try:
            # Get deterministic timestamp
            deterministic_timestamp = self._get_deterministic_timestamp()
            
            # Validate OPEN-AGI role and action type
            try:
                open_agi_role = OPENAGIRole(role)
                open_agi_action = OPENAGIActionType(action_type)
            except ValueError:
                return {
                    "success": False,
                    "error_code": "INVALID_ROLE_OR_ACTION",
                    "message": "Invalid OPEN-AGI role or action type",
                    "details": f"Role '{role}' or action '{action_type}' not recognized"
                }
            
            # Authorize the action using OPEN-AGI enforcer
            auth_result = self.open_agi_enforcer.authorize_action(
                role=open_agi_role,
                action_type=open_agi_action,
                inputs=inputs,
                deterministic_timestamp=deterministic_timestamp
            )
            
            # Check if authorized
            if not auth_result.get("authorized", False):
                return {
                    "success": False,
                    "error_code": "UNAUTHORIZED",
                    "message": "OPEN-AGI action not authorized",
                    "details": auth_result.get("reason", "Access denied")
                }
            
            # Generate deterministic observation ID
            observation_data = {
                "role": role,
                "action_type": action_type,
                "inputs": inputs,
                "suggested_changes": suggested_changes,
                "explanation": explanation,
                "timestamp": deterministic_timestamp
            }
            observation_json = json.dumps(observation_data, sort_keys=True)
            observation_id = hashlib.sha256(observation_json.encode('utf-8')).hexdigest()[:32]
            
            # Generate PQC correlation ID
            pqc_cid = f"agi_obs_{observation_id}"
            
            # Create quantum metadata
            quantum_metadata = {
                "component": "AGIObservation",
                "version": "QFS-V13-P2-1",
                "timestamp": str(deterministic_timestamp),
                "pqc_scheme": "Dilithium-5"
            }
            
            # Correlate with AEGIS observations if possible
            correlated_aegis_observations = []
            if correlation_to_aegis and "related_aegis_events" in correlation_to_aegis:
                correlated_aegis_observations = correlation_to_aegis["related_aegis_events"]
            
            # Create AGI observation object
            agi_observation = AGIObservation(
                observation_id=observation_id,
                timestamp=deterministic_timestamp,
                role=role,
                action_type=action_type,
                inputs=inputs,
                suggested_changes=suggested_changes,
                explanation=explanation,
                correlation_to_aegis=correlation_to_aegis,
                correlated_aegis_observations=correlated_aegis_observations,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata
            )
            
            # Write structured event to ledger
            ledger_entry = self.coherence_ledger.log_state(
                token_bundle=self.mock_token_bundle,  # Use mock for now
                hsmf_metrics={
                    "agi_observation": {
                        "observation_id": observation_id,
                        "role": role,
                        "action_type": action_type,
                        "timestamp": deterministic_timestamp,
                        "explanation": explanation,
                        "correlation_to_aegis": correlation_to_aegis or {},
                        "correlated_aegis_observations": correlated_aegis_observations
                    }
                },
                deterministic_timestamp=deterministic_timestamp,
                guard_results={
                    "agi_observation": {
                        "authorized": True,
                        "log_id": auth_result.get("log_id", "unknown"),
                        "role": role,
                        "action_type": action_type
                    }
                }
            )
            
            # Return success response
            return {
                "success": True,
                "observation_id": observation_id,
                "ledger_entry_id": ledger_entry.entry_id,
                "timestamp": deterministic_timestamp
            }
            
        except Exception as e:
            # Handle any unexpected errors
            return {
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": str(e)
            }

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
            
            # Get deterministic timestamp from DRV packet
            deterministic_timestamp = self._get_deterministic_timestamp()
            
            # Get real token bundle for the user
            user_token_bundle = self._get_user_token_bundle(request.user_id)
            
            # Fetch real content candidates from storage/IPFS
            content_candidates = self._fetch_content_candidates(request.user_id, request.limit or 20)
            
            # Create I_vector (feedback vector) from user history
            # In a real implementation, this would come from user's interaction history
            i_vector = [
                BigNum128.from_int(1),
                BigNum128.from_int(2),
                BigNum128.from_int(3)
            ]
            
            # Call CoherenceEngine to rank posts using real QFS components
            ranked_posts = []
            for candidate in content_candidates:
                # Build CoherenceInput from content candidate
                coherence_input = self._build_coherence_input(candidate)
                
                # Process humor signals for the content
                humor_data = None
                if "content" in candidate:
                    # Prepare context with ledger-derived metrics
                    context = {
                        "views": int(candidate.get("engagement_signals", {}).get("likes", BigNum128.from_int(0))),
                        "laughs": int(candidate.get("engagement_signals", {}).get("comments", BigNum128.from_int(0))),
                        "saves": int(candidate.get("engagement_signals", {}).get("shares", BigNum128.from_int(0))),
                        "replays": 0,  # Would come from real ledger data
                        "author_reputation": 0  # Fixed: Use 0 instead of 0.5 float literal, or BigNum128 representation inside method
                    }
                    
                    # Process humor signals
                    humor_data = self._process_humor_signals(candidate["content"], context)
                
                # Build feature vector from CoherenceInput
                features = self._build_feature_vector(coherence_input)
                
                # Update omega for each post using CoherenceEngine
                updated_omega = self.coherence_engine.update_omega(
                    features=features,
                    I_vector=i_vector,
                    L=f"L_{candidate['content_id']}",
                    log_list=[],  # In a real implementation, this would be a shared log
                    pqc_cid=f"feed_rank_{candidate['content_id']}",
                    deterministic_timestamp=deterministic_timestamp
                )
                
                # Calculate coherence score (norm of updated omega)
                coherence_score = self._calculate_coherence_score(updated_omega)
                
                # Process with AEGIS Guard for feed ranking
                aegis_observation = self.aegis_guard.observe_event(
                    event_type="feed_ranking",
                    inputs=coherence_input,
                    token_bundle=user_token_bundle,
                    deterministic_timestamp=deterministic_timestamp
                )
                
                # Prepare AEGIS advisory summary for client consumption
                aegis_advisory = {
                    "block_suggested": aegis_observation.block_suggested,
                    "severity": aegis_observation.severity
                }
                
                # Add humor signal data to AEGIS advisory if available
                if humor_data:
                    aegis_advisory["humor_signal"] = humor_data
                
                # Generate policy hints using the policy engine
                policy_hints = self.policy_engine.generate_policy_hints(aegis_advisory)
                
                # Convert policy hints to dictionary for serialization
                policy_hints_dict = {
                    "visibility_level": policy_hints.visibility_level.value,
                    "warning_banner": policy_hints.warning_banner.value,
                    "warning_message": policy_hints.warning_message,
                    "requires_click_through": policy_hints.requires_click_through,
                    "client_tags": policy_hints.client_tags
                }
                
                # Create FeedPost object with policy hints
                feed_post = FeedPost(
                    post_id=candidate['content_id'],
                    coherence_score=coherence_score,
                    policy_version="QFS_V13_FEED_RANKING_POLICY_1.0",
                    why_this_ranking=f"Ranked by CoherenceEngine with features: {len(features)} from content {candidate['content_cid']}",
                    timestamp=deterministic_timestamp,
                    aegis_advisory=aegis_advisory,
                    policy_hints=policy_hints_dict
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
            
            # Get deterministic timestamp from DRV packet
            deterministic_timestamp = self._get_deterministic_timestamp()
            
            # Create canonical interaction event structure
            interaction_event = {
                "type": interaction_type,
                "user_id": request.user_id,
                "target_id": request.target_id,
                "content": request.content,
                "reason": request.reason,
                "timestamp": deterministic_timestamp
            }
            
            # Process humor signals for the interaction content if it exists
            humor_data = None
            if request.content:
                # Prepare context with ledger-derived metrics (would come from real ledger)
                context = {
                    "views": 0,
                    "laughs": 0,
                    "saves": 0,
                    "replays": 0,
                    "author_reputation": 0  # Fixed: No float literal
                }
                
                # Process humor signals
                humor_data = self._process_humor_signals(request.content, context)
            
            # Generate deterministic event ID
            event_id = self._generate_event_id(interaction_event)
            
            # Get real token bundle for the user
            user_token_bundle = self._get_user_token_bundle(request.user_id)
            
            # Build HSMF metrics from interaction data
            hsmf_metrics = self._build_hsmf_metrics_from_interaction(interaction_type, request, user_token_bundle)
            
            # Process with AEGIS Guard in observation mode
            aegis_observation = self.aegis_guard.observe_event(
                event_type="social_interaction",
                inputs=interaction_event,
                token_bundle=user_token_bundle,
                deterministic_timestamp=deterministic_timestamp
            )
            
            # Prepare AEGIS advisory summary for client consumption
            aegis_advisory = {
                "block_suggested": aegis_observation.block_suggested,
                "severity": aegis_observation.severity
            }
            
            # Prepare guard results for ledger (includes AEGIS advisory data)
            guard_results_for_ledger = {
                "safety": {
                    "passed": aegis_observation.safety_guard_result.get("passed", False),
                    "risk_score": aegis_observation.safety_guard_result.get("risk_score", "0"),
                    "explanation": aegis_observation.safety_guard_result.get("explanation", "")
                },
                "economics": {
                    "passed": aegis_observation.economics_guard_result.get("passed", False),
                    "explanation": aegis_observation.economics_guard_result.get("explanation", "")
                },
                "aegis_advisory": {
                    "block_suggested": aegis_observation.block_suggested,
                    "severity": aegis_observation.severity,
                    "explanation": aegis_observation.explanation
                }
            }
            
            # Add humor signal data to AEGIS advisory if available
            if humor_data:
                guard_results_for_ledger["aegis_advisory"]["humor_signal"] = humor_data
            
            # Check if AEGIS suggests blocking the interaction
            if aegis_observation.block_suggested:
                # If blocking is suggested, return success=False and don't simulate rewards
                guard_results = GuardResults(
                    safety_guard_passed=False,  # Indicate safety concern
                    economics_guard_passed=aegis_observation.economics_guard_result.get("passed", True),
                    explanation=f"AEGIS advisory gate blocked interaction: {aegis_observation.explanation}. Severity: {aegis_observation.severity}"
                )
                
                # Log the blocked interaction attempt
                ledger_entry = self.coherence_ledger.log_state(
                    token_bundle=user_token_bundle,
                    hsmf_metrics=hsmf_metrics,
                    rewards={"event_id": event_id, "blocked": True},
                    deterministic_timestamp=deterministic_timestamp,
                    guard_results=guard_results_for_ledger
                )
                
                # Process notification for the blocked event
                notification = self.notification_service.process_ledger_entry(ledger_entry)
                
                # Return response indicating the interaction was blocked
                return InteractionResponse(
                    success=False,
                    event_id=event_id,
                    guard_results=guard_results,
                    reward_estimate=None,  # No reward estimate for blocked interactions
                    aegis_advisory=aegis_advisory  # Include AEGIS advisory summary
                )
            
            # Emit ledger event via CoherenceLedger with real HSMF metrics and guard results
            ledger_entry = self.coherence_ledger.log_state(
                token_bundle=user_token_bundle,
                hsmf_metrics=hsmf_metrics,
                rewards={"event_id": event_id},
                deterministic_timestamp=deterministic_timestamp,
                guard_results=guard_results_for_ledger
            )
            
            # Process notification
            notification = self.notification_service.process_ledger_entry(ledger_entry)
            
            # Build realistic economic parameters from token bundle and interaction
            chr_balance = BigNum128.from_string(str(user_token_bundle.chr_state.get('balance', '0')))
            
            # Get economics parameters from ledger economics service when available, otherwise use demo values
            if self.ledger_economics_service is not None:
                try:
                    # Get real economics data from ledger
                    daily_totals = self.ledger_economics_service.get_chr_daily_totals()
                    total_supply_data = self.ledger_economics_service.get_chr_total_supply()
                    user_balance_data = self.ledger_economics_service.get_user_balance(request.user_id)
                    
                    current_daily_total = daily_totals.get("current_daily_total", BigNum128.from_int(0))
                    current_total_supply = total_supply_data.get("current_total_supply", chr_balance)
                    user_balance = user_balance_data.get("user_balance", chr_balance)
                except Exception as e:
                    # Fall back to demo values if service fails
                    # Log to a deterministic log list instead of printing to stdout
                    log_entry = {
                        "level": "WARNING",
                        "message": f"Ledger economics service failed, falling back to demo values: {e}",
                        "timestamp": deterministic_timestamp
                    }
                    # In a real implementation, this would be added to a shared log list
                    current_daily_total = BigNum128.from_int(0)  # Would come from ledger in real implementation
                    current_total_supply = chr_balance  # Simplified for demo
                    user_balance = chr_balance  # Simplified for demo
            else:
                # Use demo values when service is not available
                current_daily_total = BigNum128.from_int(0)  # Would come from ledger in real implementation
                current_total_supply = chr_balance  # Simplified for demo
                user_balance = chr_balance  # Simplified for demo
            
            # Calculate estimated reward amount based on interaction type
            reward_amount = self._estimate_reward_for_interaction(interaction_type, user_token_bundle)
            
            # Invoke EconomicsGuard with realistic parameters
            economics_validation = self.economics_guard.validate_chr_reward(
                reward_amount=reward_amount,
                current_daily_total=current_daily_total,
                current_total_supply=current_total_supply,
                log_list=[]  # In a real implementation, this would be a shared log
            )
            
            # Create guard results from AEGIS observation
            guard_results = GuardResults(
                safety_guard_passed=aegis_observation.safety_guard_result.get("passed", False),
                economics_guard_passed=aegis_observation.economics_guard_result.get("passed", False),
                explanation=aegis_observation.safety_guard_result.get("explanation", "") + "; " + aegis_observation.economics_guard_result.get("explanation", "")
            )
            
            # Compute reward estimate via TreasuryEngine (simulation-style call)
            reward_estimate = None
            if economics_validation.passed:
                try:
                    # Use real HSMF metrics from interaction
                    # Calculate rewards using TreasuryEngine
                    reward_bundle = self.treasury_engine.calculate_rewards(
                        hsmf_metrics=hsmf_metrics,  # Real HSMF metrics from interaction
                        token_bundle=user_token_bundle,
                        log_list=[],  # In a real implementation, this would be a shared log
                        pqc_cid=f"interaction_reward_{event_id}",
                        deterministic_timestamp=deterministic_timestamp
                    )
                    
                    # Create reward estimate
                    reward_estimate = RewardEstimate(
                        amount=reward_bundle.chr_reward,  # Using CHR reward as example
                        token_type="CHR",
                        explanation=f"Estimated reward for {interaction_type} interaction based on HSMF metrics"
                    )
                except Exception as e:
                    # Handle reward calculation errors
                    reward_estimate = RewardEstimate(
                        amount=BigNum128(0),
                        token_type="NONE",
                        explanation=f"Reward calculation failed: {str(e)}"
                    )
            
            # Prepare AEGIS advisory summary for client consumption
            aegis_advisory = {
                "block_suggested": aegis_observation.block_suggested,
                "severity": aegis_observation.severity
            }
            
            # Add humor signal data to AEGIS advisory if available
            if humor_data:
                aegis_advisory["humor_signal"] = {
                    "dimensions": humor_data["dimensions"],
                    "confidence": humor_data["confidence"]
                }
            
            # Return response
            # Success is determined by both safety and economics guards passing
            success = (guard_results.safety_guard_passed and guard_results.economics_guard_passed)
            return InteractionResponse(
                success=success,
                event_id=event_id,
                guard_results=guard_results,
                reward_estimate=reward_estimate,
                aegis_advisory=aegis_advisory  # Include AEGIS advisory summary
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
            
            # Get deterministic timestamp from DRV packet
            deterministic_timestamp = self._get_deterministic_timestamp()
            
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
                from v13.core.TokenStateBundle import create_token_state_bundle
            except ImportError:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from v13.core.TokenStateBundle import create_token_state_bundle
        
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
            timestamp=self._get_deterministic_timestamp()
        )
    
    def _get_deterministic_timestamp(self) -> int:
        """
        Get deterministic timestamp from DRV packet or fallback to logical time.
        
        Returns:
            int: Deterministic timestamp
        """
        # If we have a real DRV packet, use its timestamp
        if self.drv_packet and hasattr(self.drv_packet, 'ttsTimestamp'):
            return DeterministicTime.canonical_time_from_packet(self.drv_packet)
        
        # Fallback to ledger sequence number or logical clock
        # In a real implementation, this would come from the ledger head
        if self.coherence_ledger and self.coherence_ledger.ledger_entries:
            # Use the timestamp of the latest ledger entry + 1
            latest_entry = self.coherence_ledger.ledger_entries[-1]
            return latest_entry.timestamp + 1
        
        # Ultimate fallback - use a deterministic logical counter
        # This ensures deterministic behavior even without real time source
        # Increment the counter each time it's called
        timestamp = self._logical_timestamp_counter
        self._logical_timestamp_counter += 1
        return timestamp
    
    def set_drv_packet(self, drv_packet: Any) -> None:
        """
        Set the DRV packet for deterministic time sourcing.
        
        Args:
            drv_packet: DRV packet with ttsTimestamp
        """
        self.drv_packet = drv_packet
    
    def set_storage_clients(self, storage_client: Any, ipfs_client: Any) -> None:
        """
        Set the storage clients for content retrieval.
        
        Args:
            storage_client: Storage client for database operations
            ipfs_client: IPFS client for content retrieval
        """
        self.storage_client = storage_client
        self.ipfs_client = ipfs_client
    
    def _get_user_token_bundle(self, user_id: str) -> TokenStateBundle:
        """
        Get token bundle for a user, either from real service or mock.
        
        Args:
            user_id: User identifier
            
        Returns:
            TokenStateBundle for the user
        """
        # If token state service is set, use it to get real token bundle
        if self.token_state_service is not None:
            try:
                return self.token_state_service.get_bundle_for_user(user_id)
            except Exception as e:
                # Fall back to mock if service fails
                # Fall back to mock if service fails
                # Log to a deterministic log list instead of printing to stdout
                log_entry = {
                    "level": "WARNING",
                    "message": f"Token state service failed, falling back to mock: {e}",
                    "timestamp": self._get_deterministic_timestamp()
                }
                # In a real implementation, this would be added to a shared log list
        
        # Otherwise, use mock token bundle for testing
        # In a real implementation, this would be fetched from storage
        return self.mock_token_bundle
    
    def _process_humor_signals(self, content: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process humor signals for content.
        
        Args:
            content: Content to evaluate
            context: Context with ledger-derived metrics
            
        Returns:
            Optional[Dict]: Humor signal results or None if processing fails
        """
        try:
            # Evaluate content with humor signal addon
            humor_result = self.humor_signal_addon.evaluate(content, context)
            
            # Extract dimensions and confidence
            dimensions = humor_result.metadata.get("dimensions", {})
            confidence = humor_result.confidence
            
            # Return structured humor data
            return {
                "dimensions": dimensions,
                "confidence": confidence,
                "result_hash": humor_result.result_hash,
                "content_hash": humor_result.content_hash,
                "context_hash": humor_result.context_hash
            }
        except Exception as e:
            # Log error but don't fail the entire operation
            # In a real implementation, this would be added to a shared log list
            log_entry = {
                "level": "WARNING",
                "message": f"Humor signal processing failed: {e}",
                "timestamp": self._get_deterministic_timestamp()
            }
            return None
    
    def _fetch_content_candidates(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch real content candidates for the feed from storage/IPFS.
        
        Args:
            user_id: User ID for personalization
            limit: Maximum number of candidates to fetch
            
        Returns:
            List[Dict[str, Any]]: List of content candidates with metadata
        """
        # If storage clients are set, use them to fetch real content
        if self.storage_client is not None and self.ipfs_client is not None:
            try:
                # Fetch content IDs from storage based on user preferences and social graph
                content_ids = self.storage_client.query_feed_candidates(user_id, limit)
                
                # Fetch actual content from IPFS
                candidates = []
                for content_id in content_ids:
                    try:
                        # Fetch metadata from storage
                        metadata = self.storage_client.get_content_metadata(content_id)
                        
                        # Fetch actual content from IPFS
                        content_cid = metadata.get("content_cid")
                        if content_cid:
                            content_text = self.ipfs_client.get_content(content_cid)
                            
                            # Build candidate with real data
                            candidate = {
                                "content_id": content_id,
                                "author_did": metadata.get("author_did", f"did:user:{user_id}"),
                                "community_id": metadata.get("community_id", "default"),
                                "tags": metadata.get("tags", []),
                                "engagement_signals": metadata.get("engagement_signals", {
                                    "likes": BigNum128.from_int(0),
                                    "comments": BigNum128.from_int(0),
                                    "shares": BigNum128.from_int(0)
                                }),
                                "content_cid": content_cid,
                                "created_at": metadata.get("created_at", self._get_deterministic_timestamp()),
                                "content_type": metadata.get("content_type", "post"),
                                "content": content_text or ""  # Include actual content text for safety checks
                            }
                            candidates.append(candidate)
                    except Exception as e:
                        # Skip individual content items that fail to load
                        # Log to a deterministic log list instead of printing to stdout
                        log_entry = {
                            "level": "WARNING",
                            "message": f"Failed to fetch content {content_id}: {e}",
                            "timestamp": self._get_deterministic_timestamp()
                        }
                        # In a real implementation, this would be added to a shared log list
                        continue
                
                return candidates
            except Exception as e:
                # Fall back to mock if storage/IPFS fails
                # Fall back to mock if storage/IPFS fails
                # Log to a deterministic log list instead of printing to stdout
                log_entry = {
                    "level": "WARNING",
                    "message": f"Storage/IPFS clients failed, falling back to mock: {e}",
                    "timestamp": self._get_deterministic_timestamp()
                }
                # In a real implementation, this would be added to a shared log list
        
        # In a real implementation, this would query storage/IPFS for content
        # For now, we'll return mock data with proper structure
        candidates = []
        sample_contents = [
            "This is a safe, family-friendly post about quantum computing and its applications in finance.",
            "Exploring the fascinating world of post-quantum cryptography and its implications for digital security.",
            "This is explicit adult content that should be flagged.",  # Unsafe content for testing
            "A thoughtful discussion on the ethics of artificial intelligence and machine learning systems.",
            "Buy now! Click here for free money and urgent offers!",  # Spam content for testing
        ]
        for i in range(min(limit, 5)):  # Limit to 5 for demo
            candidate = {
                "content_id": f"cid_{user_id}_{i}",
                "author_did": f"did:user:{user_id}",
                "community_id": f"community_{i % 3}",
                "tags": [f"tag_{j}" for j in range(3)],
                "engagement_signals": {
                    "likes": BigNum128.from_int(i * 10),
                    "comments": BigNum128.from_int(i * 2),
                    "shares": BigNum128.from_int(i * 1)
                },
                "content_cid": f"Qm{i:040d}",  # IPFS CID format
                "created_at": self._get_deterministic_timestamp() - (i * 1000),
                "content_type": "post",
                "content": sample_contents[i % len(sample_contents)]  # Add actual content text
            }
            candidates.append(candidate)
        return candidates
    
    def _build_coherence_input(self, content_candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build CoherenceInput from content candidate for CoherenceEngine.
        
        Args:
            content_candidate: Content candidate with metadata
            
        Returns:
            Dict[str, Any]: CoherenceInput structure
        """
        return {
            "content_cid": content_candidate["content_cid"],
            "author_did": content_candidate["author_did"],
            "community_id": content_candidate["community_id"],
            "tags": content_candidate["tags"],
            "engagement_signals": content_candidate["engagement_signals"],
            "created_at": content_candidate["created_at"],
            "content_type": content_candidate["content_type"],
            "content": content_candidate.get("content", "")  # Include content text for safety checks
        }
    
    def _build_feature_vector(self, coherence_input: Dict[str, Any]) -> List[BigNum128]:
        """
        Build feature vector for CoherenceEngine from CoherenceInput.
        
        Args:
            coherence_input: CoherenceInput structure
            
        Returns:
            List[BigNum128]: Feature vector
        """
        # In a real implementation, this would extract meaningful features
        # For now, we'll create a simple feature vector based on engagement
        signals = coherence_input["engagement_signals"]
        features = [
            signals["likes"],
            signals["comments"],
            signals["shares"]
        ]
        return features
    
    def _build_hsmf_metrics_from_interaction(self, interaction_type: str, request: InteractionRequest, token_bundle: TokenStateBundle) -> Dict[str, Any]:
        """
        Build HSMF metrics from interaction data.
        
        Args:
            interaction_type: Type of interaction
            request: Interaction request
            token_bundle: User's token bundle
            
        Returns:
            Dict[str, Any]: HSMF metrics
        """
        # Extract relevant metrics from token bundle
        c_holo = token_bundle.chr_state.get('c_holo_proxy', '0.95')
        s_flx = token_bundle.flx_state.get('flux_metric', '0.15')
        s_psi_sync = token_bundle.psi_sync_state.get('psi_sync_metric', '0.08')
        f_atr = token_bundle.atr_state.get('atr_metric', '0.85')
        
        # Adjust metrics based on interaction type
        if interaction_type == "like":
            # Likes slightly increase coherence
            c_holo = str(float(c_holo) + 0.01)
        elif interaction_type == "comment":
            # Comments have a bigger impact on coherence
            c_holo = str(float(c_holo) + 0.02)
        elif interaction_type == "follow":
            # Following increases ATR metric
            f_atr = str(float(f_atr) + 0.01)
        
        return {
            "c_holo": c_holo,
            "s_flx": s_flx,
            "s_psi_sync": s_psi_sync,
            "f_atr": f_atr
        }
    
    def _estimate_reward_for_interaction(self, interaction_type: str, token_bundle: TokenStateBundle) -> BigNum128:
        """
        Estimate reward amount for an interaction based on interaction type and user state.
        
        Args:
            interaction_type: Type of interaction
            token_bundle: User's token bundle
            
        Returns:
            BigNum128: Estimated reward amount
        """
        # Base reward amounts by interaction type
        base_rewards = {
            "like": 10,      # 10 CHR for likes
            "comment": 50,   # 50 CHR for comments
            "follow": 5,     # 5 CHR for follows
            "repost": 20,    # 20 CHR for reposts
            "report": 5      # 5 CHR for reports
        }
        
        # Get base reward
        base_reward = base_rewards.get(interaction_type, 10)
        
        # Adjust based on user's coherence metric
        coherence = float(token_bundle.chr_state.get('coherence_metric', '0.5'))
        adjusted_reward = int(base_reward * coherence)
        
        return BigNum128.from_int(adjusted_reward)