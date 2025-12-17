"""
Data models for ATLAS API Gateway
"""
try:
    from ..libs.BigNum128 import BigNum128
except ImportError:
    try:
        from v13.libs.BigNum128 import BigNum128
    except ImportError:
        try:
            from v13.libs.BigNum128 import BigNum128
        except ImportError:
            from libs.BigNum128 import BigNum128
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class FeedRequest:
    """Request model for feed endpoint"""
    user_id: str
    cursor: Optional[str] = None
    limit: Optional[int] = 20
    mode: Optional[str] = 'coherence'

@dataclass
class FeedPost:
    """Post item in feed response"""
    post_id: str
    coherence_score: BigNum128
    policy_version: str
    why_this_ranking: str
    timestamp: int
    aegis_advisory: Optional[dict] = None
    policy_hints: Optional[dict] = None

@dataclass
class FeedResponse:
    """Response model for feed endpoint"""
    posts: List[FeedPost]
    next_cursor: Optional[str] = None
    policy_metadata: Optional[dict] = None

@dataclass
class InteractionRequest:
    """Request model for interaction endpoint"""
    user_id: str
    target_id: str
    content: Optional[str] = None
    reason: Optional[str] = None

@dataclass
class GuardResults:
    """Guard evaluation results"""
    safety_guard_passed: bool
    economics_guard_passed: bool
    explanation: str

@dataclass
class RewardEstimate:
    """Reward estimate for interaction"""
    amount: BigNum128
    token_type: str
    explanation: str

@dataclass
class InteractionResponse:
    """Response model for interaction endpoint"""
    success: bool
    event_id: Optional[str] = None
    guard_results: Optional[GuardResults] = None
    reward_estimate: Optional[RewardEstimate] = None
    aegis_advisory: Optional[dict] = None

@dataclass
class AGIObservation:
    """AGI observation/recommendation event for governance"""
    observation_id: str
    timestamp: int
    role: str
    action_type: str
    inputs: Dict[str, Any]
    suggested_changes: Dict[str, Any]
    explanation: str
    correlation_to_aegis: Optional[Dict[str, Any]] = None
    correlated_aegis_observations: List[str] = field(default_factory=list)
    pqc_cid: str = ''
    quantum_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorResponse:
    """Error response model for API errors"""
    error_code: str
    message: str
    details: Optional[str] = None