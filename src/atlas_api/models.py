"""
Data models for ATLAS API Gateway
"""
from dataclasses import dataclass
from typing import Optional, List
from ..libs.BigNum128 import BigNum128


@dataclass
class FeedRequest:
    """Request model for feed endpoint"""
    user_id: str
    cursor: Optional[str] = None
    limit: Optional[int] = 20
    mode: Optional[str] = "coherence"


@dataclass
class FeedPost:
    """Post item in feed response"""
    post_id: str
    coherence_score: BigNum128
    policy_version: str
    why_this_ranking: str
    timestamp: int


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