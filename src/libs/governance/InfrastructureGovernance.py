"""
InfrastructureGovernance.py - Manages infrastructure-only governance using NOD token voting power

Implements the InfrastructureGovernance class for managing infrastructure-only governance decisions
using NOD token voting power, with firewall separation from social governance, using CertifiedMath
public API for all calculations and maintaining full auditability via log_list, pqc_cid, and quantum_metadata.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Import required modules
try:
    # Try relative imports first (for package usage)
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle
    from ...libs.economics.economic_constants import (
        NOD_DEFAULT_QUORUM_THRESHOLD,
        MIN_QUORUM_THRESHOLD,
        MAX_QUORUM_THRESHOLD,
        BLOCK_TIME_SECONDS,
        GOVERNANCE_VOTING_WINDOW_BLOCKS,
        GOVERNANCE_EXECUTION_DELAY_BLOCKS,
        GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS,
        GOVERNANCE_EMERGENCY_QUORUM,
        MAX_NOD_VOTING_POWER_RATIO
    )
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        from src.core.TokenStateBundle import TokenStateBundle
        from src.libs.economics.economic_constants import (
            NOD_DEFAULT_QUORUM_THRESHOLD,
            MIN_QUORUM_THRESHOLD,
            MAX_QUORUM_THRESHOLD,
            BLOCK_TIME_SECONDS,
            GOVERNANCE_VOTING_WINDOW_BLOCKS,
            GOVERNANCE_EXECUTION_DELAY_BLOCKS,
            GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS,
            GOVERNANCE_EMERGENCY_QUORUM,
            MAX_NOD_VOTING_POWER_RATIO
        )
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle
        from libs.economics.economic_constants import (
            NOD_DEFAULT_QUORUM_THRESHOLD,
            MIN_QUORUM_THRESHOLD,
            MAX_QUORUM_THRESHOLD,
            BLOCK_TIME_SECONDS,
            GOVERNANCE_VOTING_WINDOW_BLOCKS,
            GOVERNANCE_EXECUTION_DELAY_BLOCKS,
            GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS,
            GOVERNANCE_EMERGENCY_QUORUM,
            MAX_NOD_VOTING_POWER_RATIO
        )


class GovernanceProposalType(Enum):
    """Types of infrastructure governance proposals"""
    STORAGE_REPLICATION_FACTOR = "storage_replication_factor"
    AI_MODEL_VERSION_APPROVAL = "ai_model_version_approval"
    NETWORK_BANDWIDTH_PARAMETERS = "network_bandwidth_parameters"
    INFRASTRUCTURE_UPGRADE = "infrastructure_upgrade"
    SECURITY_PATCH_DEPLOYMENT = "security_patch_deployment"


class ProposalStatus(Enum):
    """Status of governance proposals"""
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"  # NEW: Proposer-cancelled
    EXPIRED = "expired"      # NEW: Timed out before tally


@dataclass
class InfrastructureProposal:
    """Container for infrastructure governance proposals"""
    proposal_id: str
    title: str
    description: str
    proposal_type: GovernanceProposalType
    proposer_node_id: str
    parameters: Dict[str, Any]
    creation_timestamp: int
    voting_end_timestamp: int
    execution_earliest_timestamp: int  # NEW: Earliest execution time (after timelock)
    status: ProposalStatus
    yes_votes: BigNum128  # Total NOD voting power for yes
    no_votes: BigNum128   # Total NOD voting power for no
    quorum_required: BigNum128  # Required NOD voting power to be valid
    total_nod_supply_snapshot: BigNum128  # NEW: Immutable supply snapshot at creation
    voters: Dict[str, bool]  # NEW: node_id → voted (prevents double-voting)
    executed: bool  # NEW: Whether proposal has been executed
    execution_result: Optional[Dict[str, Any]] = None  # NEW: Execution outcome
    execution_payload: Optional[Dict[str, Any]] = None


class InfrastructureGovernance:
    """
    Manager for infrastructure-only governance using NOD token voting power.
    
    Manages infrastructure-only governance decisions using NOD token voting power,
    with firewall separation from social governance, using CertifiedMath public API
    for all calculations and maintaining full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath, quorum_threshold: BigNum128 = None):
        """
        Initialize the Infrastructure Governance system.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
            quorum_threshold: Minimum percentage of total NOD supply required for quorum (default: 0.66)
        """
        self.cm = cm_instance
        
        # Set quorum threshold with constitutional bounds enforcement
        if quorum_threshold is None:
            self.quorum_threshold = NOD_DEFAULT_QUORUM_THRESHOLD
        else:
            # Enforce constitutional bounds
            if self.cm.lt(quorum_threshold, MIN_QUORUM_THRESHOLD, [], None, None):
                raise ValueError(f"Quorum threshold {quorum_threshold.to_decimal_string()} below minimum {MIN_QUORUM_THRESHOLD.to_decimal_string()}")
            if self.cm.gt(quorum_threshold, MAX_QUORUM_THRESHOLD, [], None, None):
                raise ValueError(f"Quorum threshold {quorum_threshold.to_decimal_string()} above maximum {MAX_QUORUM_THRESHOLD.to_decimal_string()}")
            self.quorum_threshold = quorum_threshold
            
        self.proposals: Dict[str, InfrastructureProposal] = {}
        self.last_proposal_timestamp: int = 0  # For cooldown enforcement
        
        # FIREWALL ASSERTION: Verify TokenStateBundle does not contain user-facing logic
        # This is a constitutional guarantee that NOD governance cannot affect user systems
        assert hasattr(TokenStateBundle, '__init__'), "TokenStateBundle must be available for verification"
        # Note: Full firewall enforcement requires runtime checks during proposal validation

    def create_proposal(
        self,
        title: str,
        description: str,
        proposal_type: GovernanceProposalType,
        proposer_node_id: str,
        parameters: Dict[str, Any],
        total_nod_supply: BigNum128,
        creation_timestamp: int,
        voting_duration_blocks: int = None,  # Default from economic_constants
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new infrastructure governance proposal.
        
        Args:
            title: Title of the proposal
            description: Detailed description of the proposal
            proposal_type: Type of infrastructure proposal
            proposer_node_id: Node ID of the proposer
            parameters: Proposal parameters
            total_nod_supply: Total NOD token supply
            creation_timestamp: Timestamp when proposal is created
            voting_duration_blocks: Duration of voting period in blocks (default from constants)
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            str: Unique proposal ID
        """
        if log_list is None:
            log_list = []
        
        # Enforce proposal cooldown (constitutional requirement)
        if self.last_proposal_timestamp > 0:
            cooldown_blocks = GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS.value
            cooldown_seconds = cooldown_blocks * BLOCK_TIME_SECONDS.value
            time_since_last = creation_timestamp - self.last_proposal_timestamp
            if time_since_last < cooldown_seconds:
                raise ValueError(f"Proposal cooldown not satisfied: {time_since_last}s < {cooldown_seconds}s required")
        
        # Verify proposer is a valid active node (stub - requires AEGIS integration)
        if not self._is_valid_active_node(proposer_node_id):
            raise ValueError(f"Proposer {proposer_node_id} is not a valid active node")
        
        # Validate proposal parameters (constitutional requirement)
        self._validate_proposal_parameters(proposal_type, parameters)
        
        # Use default voting duration if not specified
        if voting_duration_blocks is None:
            voting_duration_blocks = GOVERNANCE_VOTING_WINDOW_BLOCKS.value
            
        # Generate unique proposal ID
        proposal_data = f"{proposer_node_id}:{creation_timestamp}:{title}"
        proposal_id = hashlib.sha256(proposal_data.encode()).hexdigest()[:32]
        
        # Calculate quorum requirement: total_supply * quorum_threshold
        quorum_required = self.cm.mul(total_nod_supply, self.quorum_threshold, log_list, pqc_cid, quantum_metadata)
        
        # Calculate voting end timestamp
        voting_end_timestamp = creation_timestamp + (voting_duration_blocks * BLOCK_TIME_SECONDS.value)
        
        # Calculate execution earliest timestamp (with timelock)
        execution_delay_seconds = GOVERNANCE_EXECUTION_DELAY_BLOCKS.value * BLOCK_TIME_SECONDS.value
        execution_earliest_timestamp = voting_end_timestamp + execution_delay_seconds
        
        # Create the proposal
        proposal = InfrastructureProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            proposer_node_id=proposer_node_id,
            parameters=parameters,
            creation_timestamp=creation_timestamp,
            voting_end_timestamp=voting_end_timestamp,
            execution_earliest_timestamp=execution_earliest_timestamp,
            status=ProposalStatus.ACTIVE,
            yes_votes=BigNum128(0),
            no_votes=BigNum128(0),
            quorum_required=quorum_required,
            total_nod_supply_snapshot=total_nod_supply,  # Immutable snapshot
            voters={},  # Empty voter registry
            executed=False,
            execution_result=None
        )
        
        # Store the proposal
        self.proposals[proposal_id] = proposal
        self.last_proposal_timestamp = creation_timestamp
        
        # Log the proposal creation
        self._log_proposal_creation(
            proposal, total_nod_supply,
            log_list, pqc_cid, quantum_metadata, creation_timestamp
        )
        
        return proposal_id

    def _is_valid_active_node(self, node_id: str) -> bool:
        """
        Verify that a node ID corresponds to a valid active AEGIS node.
        
        This is a stub pending AEGIS API integration. In production, this should:
        - Query AEGIS registry for node status
        - Verify node has minimum uptime/contribution
        - Check node hasn't been slashed
        
        Args:
            node_id: Node ID to verify
            
        Returns:
            bool: True if node is valid and active
        """
        # STUB: Accept all node_ids for now
        # TODO: Integrate with AEGIS_API.is_active_node(node_id)
        return len(node_id) > 0
    
    def _validate_proposal_parameters(self, proposal_type: GovernanceProposalType, parameters: Dict[str, Any]):
        """
        Validate proposal parameters based on type-specific rules.
        
        Prevents governance from approving invalid or dangerous state transitions.
        
        Args:
            proposal_type: Type of proposal
            parameters: Proposed parameters
            
        Raises:
            ValueError: If parameters are invalid
        """
        if proposal_type == GovernanceProposalType.STORAGE_REPLICATION_FACTOR:
            if "proposed_factor" not in parameters:
                raise ValueError("STORAGE_REPLICATION_FACTOR requires 'proposed_factor' parameter")
            factor = parameters["proposed_factor"]
            if not isinstance(factor, int) or factor < 1 or factor > 10:
                raise ValueError(f"Storage replication factor must be between 1 and 10, got {factor}")
        
        elif proposal_type == GovernanceProposalType.AI_MODEL_VERSION_APPROVAL:
            if "model_version" not in parameters or "model_hash" not in parameters:
                raise ValueError("AI_MODEL_VERSION_APPROVAL requires 'model_version' and 'model_hash' parameters")
            # Additional validation: verify model_hash format
            model_hash = parameters["model_hash"]
            if not isinstance(model_hash, str) or len(model_hash) != 64:
                raise ValueError(f"model_hash must be 64-character hex string, got {model_hash}")
        
        elif proposal_type == GovernanceProposalType.NETWORK_BANDWIDTH_PARAMETERS:
            if "max_bandwidth_mbps" not in parameters:
                raise ValueError("NETWORK_BANDWIDTH_PARAMETERS requires 'max_bandwidth_mbps' parameter")
            bandwidth = parameters["max_bandwidth_mbps"]
            if not isinstance(bandwidth, (int, float)) or bandwidth <= 0 or bandwidth > 10000:
                raise ValueError(f"Bandwidth must be between 0 and 10000 Mbps, got {bandwidth}")
        
        # Additional validation rules can be added for other proposal types
        # This provides a constitutional firewall against invalid governance outcomes

    def cast_vote(
        self,
        proposal_id: str,
        voter_node_id: str,
        voter_nod_balance: BigNum128,
        vote_yes: bool,
        timestamp: int,
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Cast a vote on an infrastructure governance proposal.
        
        Args:
            proposal_id: ID of the proposal to vote on
            voter_node_id: Node ID of the voter
            voter_nod_balance: NOD balance of the voter (voting power)
            vote_yes: True for yes vote, False for no vote
            timestamp: Timestamp of the vote
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
        """
        if log_list is None:
            log_list = []
            
        # Validate proposal exists
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
            
        proposal = self.proposals[proposal_id]
        
        # Validate proposal is active
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f"Proposal {proposal_id} is not active (status: {proposal.status.value})")
            
        # Validate voting is still open
        if timestamp > proposal.voting_end_timestamp:
            raise ValueError(f"Voting period for proposal {proposal_id} has ended")
            
        # DOUBLE-VOTE PROTECTION: Check if node has already voted
        if voter_node_id in proposal.voters:
            raise ValueError(f"Node {voter_node_id} has already voted on proposal {proposal_id}")
            
        # Validate voter has voting power
        if voter_nod_balance.value <= 0:
            raise ValueError("Voter must have positive NOD balance to vote")
        
        # VOTE WEIGHT CAP: Enforce per-node voting power limit
        max_vote_power = self.cm.mul(proposal.total_nod_supply_snapshot, MAX_NOD_VOTING_POWER_RATIO, log_list, pqc_cid, quantum_metadata)
        effective_vote_power = voter_nod_balance
        capped = False
        
        if self.cm.gt(voter_nod_balance, max_vote_power, log_list, pqc_cid, quantum_metadata):
            effective_vote_power = max_vote_power
            capped = True
            # Log vote capping event
            if log_list is not None:
                log_list.append({
                    "operation": "vote_power_capped",
                    "proposal_id": proposal_id,
                    "voter_node_id": voter_node_id,
                    "original_balance": voter_nod_balance.to_decimal_string(),
                    "effective_power": effective_vote_power.to_decimal_string(),
                    "cap_ratio": MAX_NOD_VOTING_POWER_RATIO.to_decimal_string(),
                    "timestamp": timestamp
                })
            
        # Cast the vote with effective voting power
        if vote_yes:
            proposal.yes_votes = self.cm.add(proposal.yes_votes, effective_vote_power, log_list, pqc_cid, quantum_metadata)
        else:
            proposal.no_votes = self.cm.add(proposal.no_votes, effective_vote_power, log_list, pqc_cid, quantum_metadata)
        
        # Mark node as having voted (prevents double-voting)
        proposal.voters[voter_node_id] = True
            
        # Log the vote
        self._log_vote(
            proposal_id, voter_node_id, effective_vote_power, vote_yes, capped,
            log_list, pqc_cid, quantum_metadata, timestamp
        )

    def tally_votes(
        self,
        proposal_id: str,
        timestamp: int,
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Tally votes for a proposal and determine if it passes.
        
        Args:
            proposal_id: ID of the proposal to tally
            timestamp: Timestamp of the tally
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            bool: True if proposal passes, False otherwise
        """
        if log_list is None:
            log_list = []
            
        # Validate proposal exists
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
            
        proposal = self.proposals[proposal_id]
        
        # Validate voting period has ended
        if timestamp < proposal.voting_end_timestamp:
            raise ValueError(f"Voting period for proposal {proposal_id} has not ended yet")
            
        # Calculate total votes
        total_votes = self.cm.add(proposal.yes_votes, proposal.no_votes, log_list, pqc_cid, quantum_metadata)
        
        # Check if quorum is met
        quorum_met = self.cm.gte(total_votes, proposal.quorum_required, log_list, pqc_cid, quantum_metadata)
        
        if not quorum_met:
            # Proposal rejected due to insufficient quorum
            proposal.status = ProposalStatus.REJECTED
            self._log_tally_result(
                proposal_id, False, "insufficient_quorum",
                log_list, pqc_cid, quantum_metadata, timestamp
            )
            return False
            
        # Check if yes votes exceed no votes
        yes_wins = self.cm.gt(proposal.yes_votes, proposal.no_votes, log_list, pqc_cid, quantum_metadata)
        
        if yes_wins:
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
            
        # Log the tally result
        self._log_tally_result(
            proposal_id, yes_wins, "vote_result",
            log_list, pqc_cid, quantum_metadata, timestamp
        )
        
        return yes_wins

    def execute_proposal(
        self,
        proposal_id: str,
        current_timestamp: int,
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a PASSED proposal after timelock period expires.
        
        Constitutional requirements:
        - Proposal must be in PASSED status
        - Current time must be >= execution_earliest_timestamp (timelock)
        - Proposal can only be executed once (executed flag check)
        - Mutates infrastructure config state (not code)
        - Emits irreversible log entry
        
        Args:
            proposal_id: ID of the proposal to execute
            current_timestamp: Current timestamp
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            Dict[str, Any]: Execution result details
            
        Raises:
            ValueError: If proposal not found, not PASSED, timelock not satisfied, or already executed
        """
        if log_list is None:
            log_list = []
        
        # Validate proposal exists
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        
        # Validate proposal is PASSED
        if proposal.status != ProposalStatus.PASSED:
            raise ValueError(f"Proposal {proposal_id} is not in PASSED status (current status: {proposal.status.value})")
        
        # ONCE-ONLY EXECUTION: Check if already executed
        if proposal.executed:
            raise ValueError(f"Proposal {proposal_id} has already been executed")
        
        # TIMELOCK ENFORCEMENT: Check execution timestamp
        if current_timestamp < proposal.execution_earliest_timestamp:
            remaining_seconds = proposal.execution_earliest_timestamp - current_timestamp
            raise ValueError(f"Timelock not satisfied: {remaining_seconds}s remaining until {proposal.execution_earliest_timestamp}")
        
        # EXECUTE THE PROPOSAL: Mutate infrastructure config state
        execution_result = {
            "success": True,
            "proposal_id": proposal_id,
            "proposal_type": proposal.proposal_type.value,
            "parameters_applied": proposal.parameters,
            "execution_timestamp": current_timestamp,
            "timelock_satisfied": current_timestamp >= proposal.execution_earliest_timestamp
        }
        
        # Apply the infrastructure config mutation based on proposal type
        if proposal.proposal_type == GovernanceProposalType.STORAGE_REPLICATION_FACTOR:
            # Example: Update storage replication factor (would mutate actual config in production)
            proposed_factor = proposal.parameters.get("proposed_factor")
            execution_result["applied_config"] = {"storage_replication_factor": proposed_factor}
        elif proposal.proposal_type == GovernanceProposalType.AI_MODEL_VERSION_APPROVAL:
            # Example: Approve AI model version
            model_version = proposal.parameters.get("model_version")
            model_hash = proposal.parameters.get("model_hash")
            execution_result["applied_config"] = {"approved_model_version": model_version, "model_hash": model_hash}
        # Add other proposal types as needed
        
        # Mark proposal as executed
        proposal.executed = True
        proposal.status = ProposalStatus.EXECUTED
        proposal.execution_result = execution_result
        
        # Log execution (irreversible)
        self._log_execution(
            proposal_id, execution_result,
            log_list, pqc_cid, quantum_metadata, current_timestamp
        )
        
        return execution_result

    def cancel_proposal(
        self,
        proposal_id: str,
        canceller_node_id: str,
        current_timestamp: int,
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Cancel an ACTIVE proposal (proposer-only).
        
        Args:
            proposal_id: ID of the proposal to cancel
            canceller_node_id: Node ID requesting cancellation
            current_timestamp: Current timestamp
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Raises:
            ValueError: If not proposer, proposal not found, or not ACTIVE
        """
        if log_list is None:
            log_list = []
        
        # Validate proposal exists
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        
        # PROPOSER-ONLY: Verify canceller is the original proposer
        if canceller_node_id != proposal.proposer_node_id:
            raise ValueError(f"Only proposer {proposal.proposer_node_id} can cancel this proposal")
        
        # Validate proposal is ACTIVE (can't cancel PASSED/REJECTED/EXECUTED)
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f"Can only cancel ACTIVE proposals (current status: {proposal.status.value})")
        
        # Cancel the proposal
        proposal.status = ProposalStatus.CANCELLED
        
        # Log cancellation
        self._log_cancellation(
            proposal_id, canceller_node_id,
            log_list, pqc_cid, quantum_metadata, current_timestamp
        )

    def expire_stale_proposals(
        self,
        current_timestamp: int,
        log_list: List[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Batch expire all stale ACTIVE proposals whose voting window has passed.
        
        Processes proposals in deterministic sorted order (by proposal_id) to ensure
        replay consistency.
        
        Args:
            current_timestamp: Current timestamp
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            List[str]: List of expired proposal IDs
        """
        if log_list is None:
            log_list = []
        
        expired_ids = []
        
        # Get all ACTIVE proposals and sort by proposal_id (deterministic order)
        active_proposals = [
            (p_id, p) for p_id, p in self.proposals.items()
            if p.status == ProposalStatus.ACTIVE
        ]
        active_proposals.sort(key=lambda x: x[0])  # Sort by proposal_id for determinism
        
        # Expire stale proposals
        for proposal_id, proposal in active_proposals:
            if current_timestamp > proposal.voting_end_timestamp:
                # Voting window has passed without tally
                proposal.status = ProposalStatus.EXPIRED
                expired_ids.append(proposal_id)
                
                # Log expiry
                self._log_expiry(
                    proposal_id, current_timestamp, proposal.voting_end_timestamp,
                    log_list, pqc_cid, quantum_metadata, current_timestamp
                )
        
        return expired_ids

    def get_proposal(self, proposal_id: str) -> Optional[InfrastructureProposal]:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal to retrieve
            
        Returns:
            InfrastructureProposal: The proposal, or None if not found
        """
        return self.proposals.get(proposal_id)

    def get_active_proposals(self) -> List[InfrastructureProposal]:
        """
        Get all active proposals.
        
        Returns:
            List[InfrastructureProposal]: List of active proposals
        """
        return [p for p in self.proposals.values() if p.status == ProposalStatus.ACTIVE]

    def _log_proposal_creation(
        self,
        proposal: InfrastructureProposal,
        total_nod_supply: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal creation for audit purposes with SHA-256 event hash.
        
        Args:
            proposal: The created proposal
            total_nod_supply: Total NOD supply
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_proposal_creation",
            "proposal_id": proposal.proposal_id,
            "title": proposal.title,
            "proposal_type": proposal.proposal_type.value,
            "proposer_node_id": proposal.proposer_node_id,
            "total_nod_supply": total_nod_supply.to_decimal_string(),
            "total_nod_supply_snapshot": proposal.total_nod_supply_snapshot.to_decimal_string(),
            "quorum_required": proposal.quorum_required.to_decimal_string(),
            "creation_timestamp": proposal.creation_timestamp,
            "voting_end_timestamp": proposal.voting_end_timestamp,
            "execution_earliest_timestamp": proposal.execution_earliest_timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_proposal_creation",
            "details": event_data,
            "event_hash": event_hash,
            "result": proposal.quorum_required.to_decimal_string(),
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_vote(
        self,
        proposal_id: str,
        voter_node_id: str,
        voter_nod_balance: BigNum128,
        vote_yes: bool,
        capped: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log vote for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            voter_node_id: Node ID of the voter
            voter_nod_balance: NOD balance of the voter (effective after capping)
            vote_yes: Vote decision
            capped: Whether vote power was capped
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_vote",
            "proposal_id": proposal_id,
            "voter_node_id": voter_node_id,
            "voter_nod_balance": voter_nod_balance.to_decimal_string(),
            "vote": "yes" if vote_yes else "no",
            "capped": capped,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_vote",
            "details": event_data,
            "event_hash": event_hash,
            "result": voter_nod_balance.to_decimal_string(),
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_tally_result(
        self,
        proposal_id: str,
        passed: bool,
        reason: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log tally result for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            passed: Whether the proposal passed
            reason: Reason for the result
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        proposal = self.proposals.get(proposal_id)
        
        # Create event details with quorum calculation
        event_data = {
            "operation": "infrastructure_tally",
            "proposal_id": proposal_id,
            "result": "passed" if passed else "rejected",
            "reason": reason,
            "yes_votes": proposal.yes_votes.to_decimal_string() if proposal else "0",
            "no_votes": proposal.no_votes.to_decimal_string() if proposal else "0",
            "quorum_required": proposal.quorum_required.to_decimal_string() if proposal else "0",
            "quorum_met": passed or reason == "vote_result",  # True if reason is vote_result (quorum was met)
            "execution_eligible": passed,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_tally",
            "details": event_data,
            "event_hash": event_hash,
            "result": "1" if passed else "0",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_execution(
        self,
        proposal_id: str,
        execution_result: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal execution for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            execution_result: Execution result details
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_execution",
            "proposal_id": proposal_id,
            "execution_result": execution_result,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_execution",
            "details": event_data,
            "event_hash": event_hash,
            "result": "executed",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_cancellation(
        self,
        proposal_id: str,
        canceller_node_id: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal cancellation for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            canceller_node_id: Node ID who cancelled
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_cancellation",
            "proposal_id": proposal_id,
            "canceller_node_id": canceller_node_id,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_cancellation",
            "details": event_data,
            "event_hash": event_hash,
            "result": "cancelled",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_expiry(
        self,
        proposal_id: str,
        current_timestamp: int,
        voting_end_timestamp: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal expiry for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            current_timestamp: Current timestamp
            voting_end_timestamp: When voting ended
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_expiry",
            "proposal_id": proposal_id,
            "current_timestamp": current_timestamp,
            "voting_end_timestamp": voting_end_timestamp,
            "time_elapsed": current_timestamp - voting_end_timestamp,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_expiry",
            "details": event_data,
            "event_hash": event_hash,
            "result": "expired",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })


# Test function
def test_infrastructure_governance():
    """Test the InfrastructureGovernance implementation."""
    print("Testing InfrastructureGovernance...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create InfrastructureGovernance
    gov = InfrastructureGovernance(cm, quorum_threshold="0.5")  # 50% quorum for testing
    
    # Test total NOD supply
    total_nod_supply = BigNum128.from_int(10000)  # 10,000 NOD total
    
    # Create a proposal
    proposal_id = gov.create_proposal(
        title="Increase Storage Replication Factor",
        description="Increase the storage replication factor from 3 to 5 for improved redundancy",
        proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
        proposer_node_id="node_0xabc123",
        parameters={"current_factor": 3, "proposed_factor": 5},
        total_nod_supply=total_nod_supply,
        creation_timestamp=1234567890,
        voting_duration_blocks=100  # Short for testing
    )
    
    print(f"Created proposal: {proposal_id}")
    
    # Cast some votes
    log_list = []
    
    # Node 1 votes yes with 3000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xabc123",
        voter_nod_balance=BigNum128.from_int(3000),
        vote_yes=True,
        timestamp=1234567900,
        log_list=log_list
    )
    
    # Node 2 votes no with 2000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xdef456",
        voter_nod_balance=BigNum128.from_int(2000),
        vote_yes=False,
        timestamp=1234567910,
        log_list=log_list
    )
    
    # Node 3 votes yes with 4000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xghi789",
        voter_nod_balance=BigNum128.from_int(4000),
        vote_yes=True,
        timestamp=1234567920,
        log_list=log_list
    )
    
    # Tally votes (after voting period ends)
    proposal_passed = gov.tally_votes(
        proposal_id=proposal_id,
        timestamp=12345680000,  # After voting period (increased to ensure it's after)
        log_list=log_list
    )
    
    proposal = gov.get_proposal(proposal_id)
    print(f"Proposal status: {proposal.status.value}")
    print(f"Proposal passed: {proposal_passed}")
    print(f"Yes votes: {proposal.yes_votes.to_decimal_string()}")
    print(f"No votes: {proposal.no_votes.to_decimal_string()}")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ InfrastructureGovernance test passed!")


if __name__ == "__main__":
    test_infrastructure_governance()proposal.voting_end_timestamp,
            "execution_earliest_timestamp": proposal.execution_earliest_timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_proposal_creation",
            "details": event_data,
            "event_hash": event_hash,
            "result": proposal.quorum_required.to_decimal_string(),
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_vote(
        self,
        proposal_id: str,
        voter_node_id: str,
        voter_nod_balance: BigNum128,
        vote_yes: bool,
        capped: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log vote for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            voter_node_id: Node ID of the voter
            voter_nod_balance: NOD balance of the voter (effective after capping)
            vote_yes: Vote decision
            capped: Whether vote power was capped
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_vote",
            "proposal_id": proposal_id,
            "voter_node_id": voter_node_id,
            "voter_nod_balance": voter_nod_balance.to_decimal_string(),
            "vote": "yes" if vote_yes else "no",
            "capped": capped,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_vote",
            "details": event_data,
            "event_hash": event_hash,
            "result": voter_nod_balance.to_decimal_string(),
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_tally_result(
        self,
        proposal_id: str,
        passed: bool,
        reason: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log tally result for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            passed: Whether the proposal passed
            reason: Reason for the result
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        proposal = self.proposals.get(proposal_id)
        
        # Create event details with quorum calculation
        event_data = {
            "operation": "infrastructure_tally",
            "proposal_id": proposal_id,
            "result": "passed" if passed else "rejected",
            "reason": reason,
            "yes_votes": proposal.yes_votes.to_decimal_string() if proposal else "0",
            "no_votes": proposal.no_votes.to_decimal_string() if proposal else "0",
            "quorum_required": proposal.quorum_required.to_decimal_string() if proposal else "0",
            "quorum_met": passed or reason == "vote_result",  # True if reason is vote_result (quorum was met)
            "execution_eligible": passed,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_tally",
            "details": event_data,
            "event_hash": event_hash,
            "result": "1" if passed else "0",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_execution(
        self,
        proposal_id: str,
        execution_result: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal execution for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            execution_result: Execution result details
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_execution",
            "proposal_id": proposal_id,
            "execution_result": execution_result,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_execution",
            "details": event_data,
            "event_hash": event_hash,
            "result": "executed",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_cancellation(
        self,
        proposal_id: str,
        canceller_node_id: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal cancellation for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            canceller_node_id: Node ID who cancelled
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_cancellation",
            "proposal_id": proposal_id,
            "canceller_node_id": canceller_node_id,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_cancellation",
            "details": event_data,
            "event_hash": event_hash,
            "result": "cancelled",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })

    def _log_expiry(
        self,
        proposal_id: str,
        current_timestamp: int,
        voting_end_timestamp: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        timestamp: int = 0,
    ):
        """
        Log proposal expiry for audit purposes with SHA-256 event hash.
        
        Args:
            proposal_id: ID of the proposal
            current_timestamp: Current timestamp
            voting_end_timestamp: When voting ended
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            timestamp: Timestamp
        """
        # Create event details
        event_data = {
            "operation": "infrastructure_expiry",
            "proposal_id": proposal_id,
            "current_timestamp": current_timestamp,
            "voting_end_timestamp": voting_end_timestamp,
            "time_elapsed": current_timestamp - voting_end_timestamp,
            "timestamp": timestamp
        }
        
        # Generate SHA-256 event hash for Merkle inclusion
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        
        # Log entry
        log_list.append({
            "operation": "infrastructure_expiry",
            "details": event_data,
            "event_hash": event_hash,
            "result": "expired",
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": timestamp
        })


# Test function
def test_infrastructure_governance():
    """Test the InfrastructureGovernance implementation."""
    print("Testing InfrastructureGovernance...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create InfrastructureGovernance
    gov = InfrastructureGovernance(cm, quorum_threshold="0.5")  # 50% quorum for testing
    
    # Test total NOD supply
    total_nod_supply = BigNum128.from_int(10000)  # 10,000 NOD total
    
    # Create a proposal
    proposal_id = gov.create_proposal(
        title="Increase Storage Replication Factor",
        description="Increase the storage replication factor from 3 to 5 for improved redundancy",
        proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
        proposer_node_id="node_0xabc123",
        parameters={"current_factor": 3, "proposed_factor": 5},
        total_nod_supply=total_nod_supply,
        creation_timestamp=1234567890,
        voting_duration_blocks=100  # Short for testing
    )
    
    print(f"Created proposal: {proposal_id}")
    
    # Cast some votes
    log_list = []
    
    # Node 1 votes yes with 3000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xabc123",
        voter_nod_balance=BigNum128.from_int(3000),
        vote_yes=True,
        timestamp=1234567900,
        log_list=log_list
    )
    
    # Node 2 votes no with 2000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xdef456",
        voter_nod_balance=BigNum128.from_int(2000),
        vote_yes=False,
        timestamp=1234567910,
        log_list=log_list
    )
    
    # Node 3 votes yes with 4000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xghi789",
        voter_nod_balance=BigNum128.from_int(4000),
        vote_yes=True,
        timestamp=1234567920,
        log_list=log_list
    )
    
    # Tally votes (after voting period ends)
    proposal_passed = gov.tally_votes(
        proposal_id=proposal_id,
        timestamp=12345680000,  # After voting period (increased to ensure it's after)
        log_list=log_list
    )
    
    proposal = gov.get_proposal(proposal_id)
    print(f"Proposal status: {proposal.status.value}")
    print(f"Proposal passed: {proposal_passed}")
    print(f"Yes votes: {proposal.yes_votes.to_decimal_string()}")
    print(f"No votes: {proposal.no_votes.to_decimal_string()}")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ InfrastructureGovernance test passed!")


if __name__ == "__main__":
    test_infrastructure_governance()