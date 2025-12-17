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
try:
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle
    from ...libs.economics.economic_constants import NOD_DEFAULT_QUORUM_THRESHOLD, MIN_QUORUM_THRESHOLD, MAX_QUORUM_THRESHOLD, BLOCK_TIME_SECONDS, GOVERNANCE_VOTING_WINDOW_BLOCKS, GOVERNANCE_EXECUTION_DELAY_BLOCKS, GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS, GOVERNANCE_EMERGENCY_QUORUM, MAX_NOD_VOTING_POWER_RATIO
    from .AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
except ImportError:
    try:
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
        from v13.libs.economics.economic_constants import NOD_DEFAULT_QUORUM_THRESHOLD, MIN_QUORUM_THRESHOLD, MAX_QUORUM_THRESHOLD, BLOCK_TIME_SECONDS, GOVERNANCE_VOTING_WINDOW_BLOCKS, GOVERNANCE_EXECUTION_DELAY_BLOCKS, GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS, GOVERNANCE_EMERGENCY_QUORUM, MAX_NOD_VOTING_POWER_RATIO
        from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
        from v13.libs.economics.economic_constants import NOD_DEFAULT_QUORUM_THRESHOLD, MIN_QUORUM_THRESHOLD, MAX_QUORUM_THRESHOLD, BLOCK_TIME_SECONDS, GOVERNANCE_VOTING_WINDOW_BLOCKS, GOVERNANCE_EXECUTION_DELAY_BLOCKS, GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS, GOVERNANCE_EMERGENCY_QUORUM, MAX_NOD_VOTING_POWER_RATIO
        from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult

class GovernanceProposalType(Enum):
    """Types of infrastructure governance proposals"""
    STORAGE_REPLICATION_FACTOR = 'storage_replication_factor'
    AI_MODEL_VERSION_APPROVAL = 'ai_model_version_approval'
    NETWORK_BANDWIDTH_PARAMETERS = 'network_bandwidth_parameters'
    INFRASTRUCTURE_UPGRADE = 'infrastructure_upgrade'
    SECURITY_PATCH_DEPLOYMENT = 'security_patch_deployment'

class ProposalStatus(Enum):
    """Status of governance proposals"""
    ACTIVE = 'active'
    PASSED = 'passed'
    REJECTED = 'rejected'
    EXECUTED = 'executed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

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
    execution_earliest_timestamp: int
    status: ProposalStatus
    yes_votes: BigNum128
    no_votes: BigNum128
    quorum_required: BigNum128
    total_nod_supply_snapshot: BigNum128
    voters: Dict[str, bool]
    executed: bool
    execution_result: Optional[Dict[str, Any]] = None
    execution_payload: Optional[Dict[str, Any]] = None

class InfrastructureGovernance:
    """
    Manager for infrastructure-only governance using NOD token voting power.
    
    Manages infrastructure-only governance decisions using NOD token voting power,
    with firewall separation from social governance, using CertifiedMath public API
    for all calculations and maintaining full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath, quorum_threshold: BigNum128=None):
        """
        Initialize the Infrastructure Governance system with V13.6 AEGIS verification.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
            quorum_threshold: Minimum percentage of total NOD supply required for quorum (default: 0.66)
        """
        self.cm = cm_instance
        self.aegis_node_verifier = AEGIS_Node_Verifier(cm_instance)
        if quorum_threshold is None:
            self.quorum_threshold = NOD_DEFAULT_QUORUM_THRESHOLD
        else:
            if self.cm.lt(quorum_threshold, MIN_QUORUM_THRESHOLD, [], None, None):
                raise ValueError(f'Quorum threshold {quorum_threshold.to_decimal_string()} below minimum {MIN_QUORUM_THRESHOLD.to_decimal_string()}')
            if self.cm.gt(quorum_threshold, MAX_QUORUM_THRESHOLD, [], None, None):
                raise ValueError(f'Quorum threshold {quorum_threshold.to_decimal_string()} above maximum {MAX_QUORUM_THRESHOLD.to_decimal_string()}')
            self.quorum_threshold = quorum_threshold
        self.proposals: Dict[str, InfrastructureProposal] = {}
        self.last_proposal_timestamp: int = 0
        assert hasattr(TokenStateBundle, '__init__'), 'TokenStateBundle must be available for verification'

    def create_proposal(self, title: str, description: str, proposal_type: GovernanceProposalType, proposer_node_id: str, parameters: Dict[str, Any], total_nod_supply: BigNum128, creation_timestamp: int, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], voting_duration_blocks: int=None, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> str:
        """
        Create a new infrastructure governance proposal.
        
        V13.6: Now requires AEGIS registry + telemetry snapshots for NOD-I2 compliance.
        
        Args:
            title: Title of the proposal
            description: Detailed description of the proposal
            proposal_type: Type of infrastructure proposal
            proposer_node_id: Node ID of the proposer
            parameters: Proposal parameters
            total_nod_supply: Total NOD token supply
            creation_timestamp: Timestamp when proposal is created
            registry_snapshot: AEGIS registry snapshot (hash-anchored, versioned)
            telemetry_snapshot: AEGIS telemetry snapshot (hash-anchored, versioned)
            voting_duration_blocks: Duration of voting period in blocks (default from constants)
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            str: Unique proposal ID
        """
        if log_list is None:
            log_list = []
        if self.last_proposal_timestamp > 0:
            cooldown_blocks = GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS.value
            cooldown_seconds = cooldown_blocks * BLOCK_TIME_SECONDS.value
            time_since_last = creation_timestamp - self.last_proposal_timestamp
            if time_since_last < cooldown_seconds:
                raise ValueError(f'Proposal cooldown not satisfied: {time_since_last}s < {cooldown_seconds}s required')
        if not self._is_valid_active_node(proposer_node_id, registry_snapshot, telemetry_snapshot, log_list):
            raise ValueError(f'Proposer {proposer_node_id} is not a valid active node (AEGIS verification failed)')
        self._validate_proposal_parameters(proposal_type, parameters)
        if voting_duration_blocks is None:
            voting_duration_blocks = GOVERNANCE_VOTING_WINDOW_BLOCKS.value
        proposal_data = f'{proposer_node_id}:{creation_timestamp}:{title}'
        proposal_id = hashlib.sha256(proposal_data.encode()).hexdigest()[:32]
        quorum_required = self.cm.mul(total_nod_supply, self.quorum_threshold, log_list, pqc_cid, quantum_metadata)
        voting_end_timestamp = creation_timestamp + voting_duration_blocks * BLOCK_TIME_SECONDS.value
        execution_delay_seconds = GOVERNANCE_EXECUTION_DELAY_BLOCKS.value * BLOCK_TIME_SECONDS.value
        execution_earliest_timestamp = voting_end_timestamp + execution_delay_seconds
        proposal = InfrastructureProposal(proposal_id=proposal_id, title=title, description=description, proposal_type=proposal_type, proposer_node_id=proposer_node_id, parameters=parameters, creation_timestamp=creation_timestamp, voting_end_timestamp=voting_end_timestamp, execution_earliest_timestamp=execution_earliest_timestamp, status=ProposalStatus.ACTIVE, yes_votes=BigNum128(0), no_votes=BigNum128(0), quorum_required=quorum_required, total_nod_supply_snapshot=total_nod_supply, voters={}, executed=False, execution_result=None)
        self.proposals[proposal_id] = proposal
        self.last_proposal_timestamp = creation_timestamp
        self._log_proposal_creation(proposal, total_nod_supply, log_list, pqc_cid, quantum_metadata, creation_timestamp)
        return proposal_id

    def _is_valid_active_node(self, node_id: str, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: Optional[List[Dict[str, Any]]]=None) -> bool:
        """
        Verify that a node ID corresponds to a valid active AEGIS node.
        
        V13.6: Replaced stub with AEGIS_Node_Verifier integration for structural enforcement.
        Uses deterministic registry + telemetry snapshots (hash-anchored) to ensure NOD-I2
        compliance: only verified nodes can participate in governance.
        
        Args:
            node_id: Node ID to verify
            registry_snapshot: AEGIS registry snapshot (hash-anchored, versioned)
            telemetry_snapshot: AEGIS telemetry snapshot (hash-anchored, versioned)
            log_list: Optional audit log list
            
        Returns:
            bool: True if node is valid and active (passes all AEGIS verification checks)
        """
        if log_list is None:
            log_list = []
        verification_result = self.aegis_node_verifier.verify_node(node_id=node_id, registry_snapshot=registry_snapshot, telemetry_snapshot=telemetry_snapshot, log_list=log_list)
        if not verification_result.is_valid:
            log_list.append({'operation': 'governance_node_verification_failed', 'node_id': node_id, 'status': verification_result.status.value, 'reason_code': verification_result.reason_code, 'reason_message': verification_result.reason_message})
        return verification_result.is_valid

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
            if 'proposed_factor' not in parameters:
                raise ValueError("STORAGE_REPLICATION_FACTOR requires 'proposed_factor' parameter")
            factor = parameters['proposed_factor']
            if not isinstance(factor, int) or factor < 1 or factor > 10:
                raise ValueError(f'Storage replication factor must be between 1 and 10, got {factor}')
        elif proposal_type == GovernanceProposalType.AI_MODEL_VERSION_APPROVAL:
            if 'model_version' not in parameters or 'model_hash' not in parameters:
                raise ValueError("AI_MODEL_VERSION_APPROVAL requires 'model_version' and 'model_hash' parameters")
            model_hash = parameters['model_hash']
            if not isinstance(model_hash, str) or len(model_hash) != 64:
                raise ValueError(f'model_hash must be 64-character hex string, got {model_hash}')
        elif proposal_type == GovernanceProposalType.NETWORK_BANDWIDTH_PARAMETERS:
            if 'max_bandwidth_mbps' not in parameters:
                raise ValueError("NETWORK_BANDWIDTH_PARAMETERS requires 'max_bandwidth_mbps' parameter")
            bandwidth = parameters['max_bandwidth_mbps']
            if not isinstance(bandwidth, (int, float)) or bandwidth <= 0 or bandwidth > 10000:
                raise ValueError(f'Bandwidth must be between 0 and 10000 Mbps, got {bandwidth}')

    def cast_vote(self, proposal_id: str, voter_node_id: str, voter_nod_balance: BigNum128, vote_yes: bool, timestamp: int, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None):
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
        if proposal_id not in self.proposals:
            raise ValueError(f'Proposal {proposal_id} not found')
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f'Proposal {proposal_id} is not active (status: {proposal.status.value})')
        if timestamp > proposal.voting_end_timestamp:
            raise ValueError(f'Voting period for proposal {proposal_id} has ended')
        if voter_node_id in proposal.voters:
            raise ValueError(f'Node {voter_node_id} has already voted on proposal {proposal_id}')
        if voter_nod_balance.value <= 0:
            raise ValueError('Voter must have positive NOD balance to vote')
        max_vote_power = self.cm.mul(proposal.total_nod_supply_snapshot, MAX_NOD_VOTING_POWER_RATIO, log_list, pqc_cid, quantum_metadata)
        effective_vote_power = voter_nod_balance
        capped = False
        if self.cm.gt(voter_nod_balance, max_vote_power, log_list, pqc_cid, quantum_metadata):
            effective_vote_power = max_vote_power
            capped = True
            if log_list is not None:
                log_list.append({'operation': 'vote_power_capped', 'proposal_id': proposal_id, 'voter_node_id': voter_node_id, 'original_balance': voter_nod_balance.to_decimal_string(), 'effective_power': effective_vote_power.to_decimal_string(), 'cap_ratio': MAX_NOD_VOTING_POWER_RATIO.to_decimal_string(), 'timestamp': timestamp})
        if vote_yes:
            proposal.yes_votes = self.cm.add(proposal.yes_votes, effective_vote_power, log_list, pqc_cid, quantum_metadata)
        else:
            proposal.no_votes = self.cm.add(proposal.no_votes, effective_vote_power, log_list, pqc_cid, quantum_metadata)
        proposal.voters[voter_node_id] = True
        self._log_vote(proposal_id, voter_node_id, effective_vote_power, vote_yes, capped, log_list, pqc_cid, quantum_metadata, timestamp)

    def tally_votes(self, proposal_id: str, timestamp: int, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> bool:
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
        if proposal_id not in self.proposals:
            raise ValueError(f'Proposal {proposal_id} not found')
        proposal = self.proposals[proposal_id]
        if timestamp < proposal.voting_end_timestamp:
            raise ValueError(f'Voting period for proposal {proposal_id} has not ended yet')
        total_votes = self.cm.add(proposal.yes_votes, proposal.no_votes, log_list, pqc_cid, quantum_metadata)
        quorum_met = self.cm.gte(total_votes, proposal.quorum_required, log_list, pqc_cid, quantum_metadata)
        if not quorum_met:
            proposal.status = ProposalStatus.REJECTED
            self._log_tally_result(proposal_id, False, 'insufficient_quorum', log_list, pqc_cid, quantum_metadata, timestamp)
            return False
        yes_wins = self.cm.gt(proposal.yes_votes, proposal.no_votes, log_list, pqc_cid, quantum_metadata)
        if yes_wins:
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
        self._log_tally_result(proposal_id, yes_wins, 'vote_result', log_list, pqc_cid, quantum_metadata, timestamp)
        return yes_wins

    def execute_proposal(self, proposal_id: str, current_timestamp: int, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
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
        if proposal_id not in self.proposals:
            raise ValueError(f'Proposal {proposal_id} not found')
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.PASSED:
            raise ValueError(f'Proposal {proposal_id} is not in PASSED status (current status: {proposal.status.value})')
        if proposal.executed:
            raise ValueError(f'Proposal {proposal_id} has already been executed')
        if current_timestamp < proposal.execution_earliest_timestamp:
            remaining_seconds = proposal.execution_earliest_timestamp - current_timestamp
            raise ValueError(f'Timelock not satisfied: {remaining_seconds}s remaining until {proposal.execution_earliest_timestamp}')
        execution_result = {'success': True, 'proposal_id': proposal_id, 'proposal_type': proposal.proposal_type.value, 'parameters_applied': proposal.parameters, 'execution_timestamp': current_timestamp, 'timelock_satisfied': current_timestamp >= proposal.execution_earliest_timestamp}
        if proposal.proposal_type == GovernanceProposalType.STORAGE_REPLICATION_FACTOR:
            proposed_factor = proposal.parameters.get('proposed_factor')
            execution_result['applied_config'] = {'storage_replication_factor': proposed_factor}
        elif proposal.proposal_type == GovernanceProposalType.AI_MODEL_VERSION_APPROVAL:
            model_version = proposal.parameters.get('model_version')
            model_hash = proposal.parameters.get('model_hash')
            execution_result['applied_config'] = {'approved_model_version': model_version, 'model_hash': model_hash}
        proposal.executed = True
        proposal.status = ProposalStatus.EXECUTED
        proposal.execution_result = execution_result
        self._log_execution(proposal_id, execution_result, log_list, pqc_cid, quantum_metadata, current_timestamp)
        return execution_result

    def cancel_proposal(self, proposal_id: str, canceller_node_id: str, current_timestamp: int, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None):
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
        if proposal_id not in self.proposals:
            raise ValueError(f'Proposal {proposal_id} not found')
        proposal = self.proposals[proposal_id]
        if canceller_node_id != proposal.proposer_node_id:
            raise ValueError(f'Only proposer {proposal.proposer_node_id} can cancel this proposal')
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f'Can only cancel ACTIVE proposals (current status: {proposal.status.value})')
        proposal.status = ProposalStatus.CANCELLED
        self._log_cancellation(proposal_id, canceller_node_id, log_list, pqc_cid, quantum_metadata, current_timestamp)

    def expire_stale_proposals(self, current_timestamp: int, log_list: List[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> List[str]:
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
        active_proposals = [(p_id, p) for p_id, p in self.proposals.items() if p.status == ProposalStatus.ACTIVE]
        active_proposals.sort(key=lambda x: x[0])
        for proposal_id, proposal in sorted(active_proposals):
            if current_timestamp > proposal.voting_end_timestamp:
                proposal.status = ProposalStatus.EXPIRED
                expired_ids.append(proposal_id)
                self._log_expiry(proposal_id, current_timestamp, proposal.voting_end_timestamp, log_list, pqc_cid, quantum_metadata, current_timestamp)
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

    def _log_proposal_creation(self, proposal: InfrastructureProposal, total_nod_supply: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_proposal_creation', 'proposal_id': proposal.proposal_id, 'title': proposal.title, 'proposal_type': proposal.proposal_type.value, 'proposer_node_id': proposal.proposer_node_id, 'total_nod_supply': total_nod_supply.to_decimal_string(), 'total_nod_supply_snapshot': proposal.total_nod_supply_snapshot.to_decimal_string(), 'quorum_required': proposal.quorum_required.to_decimal_string(), 'creation_timestamp': proposal.creation_timestamp, 'voting_end_timestamp': proposal.voting_end_timestamp, 'execution_earliest_timestamp': proposal.execution_earliest_timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_proposal_creation', 'details': event_data, 'event_hash': event_hash, 'result': proposal.quorum_required.to_decimal_string(), 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_vote(self, proposal_id: str, voter_node_id: str, voter_nod_balance: BigNum128, vote_yes: bool, capped: bool, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_vote', 'proposal_id': proposal_id, 'voter_node_id': voter_node_id, 'voter_nod_balance': voter_nod_balance.to_decimal_string(), 'vote': 'yes' if vote_yes else 'no', 'capped': capped, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_vote', 'details': event_data, 'event_hash': event_hash, 'result': voter_nod_balance.to_decimal_string(), 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_tally_result(self, proposal_id: str, passed: bool, reason: str, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_tally', 'proposal_id': proposal_id, 'result': 'passed' if passed else 'rejected', 'reason': reason, 'yes_votes': proposal.yes_votes.to_decimal_string() if proposal else '0', 'no_votes': proposal.no_votes.to_decimal_string() if proposal else '0', 'quorum_required': proposal.quorum_required.to_decimal_string() if proposal else '0', 'quorum_met': passed or reason == 'vote_result', 'execution_eligible': passed, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_tally', 'details': event_data, 'event_hash': event_hash, 'result': '1' if passed else '0', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_execution(self, proposal_id: str, execution_result: Dict[str, Any], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_execution', 'proposal_id': proposal_id, 'execution_result': execution_result, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_execution', 'details': event_data, 'event_hash': event_hash, 'result': 'executed', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_cancellation(self, proposal_id: str, canceller_node_id: str, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_cancellation', 'proposal_id': proposal_id, 'canceller_node_id': canceller_node_id, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_cancellation', 'details': event_data, 'event_hash': event_hash, 'result': 'cancelled', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_expiry(self, proposal_id: str, current_timestamp: int, voting_end_timestamp: int, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_expiry', 'proposal_id': proposal_id, 'current_timestamp': current_timestamp, 'voting_end_timestamp': voting_end_timestamp, 'time_elapsed': current_timestamp - voting_end_timestamp, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_expiry', 'details': event_data, 'event_hash': event_hash, 'result': 'expired', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

def test_infrastructure_governance():
    """Test the InfrastructureGovernance implementation."""
    cm = CertifiedMath()
    gov = InfrastructureGovernance(cm, quorum_threshold='0.5')
    total_nod_supply = BigNum128.from_int(10000)
    proposal_id = gov.create_proposal(title='Increase Storage Replication Factor', description='Increase the storage replication factor from 3 to 5 for improved redundancy', proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR, proposer_node_id='node_0xabc123', parameters={'current_factor': 3, 'proposed_factor': 5}, total_nod_supply=total_nod_supply, creation_timestamp=1234567890, voting_duration_blocks=100)
    log_list = []
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xabc123', voter_nod_balance=BigNum128.from_int(3000), vote_yes=True, timestamp=1234567900, log_list=log_list)
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xdef456', voter_nod_balance=BigNum128.from_int(2000), vote_yes=False, timestamp=1234567910, log_list=log_list)
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xghi789', voter_nod_balance=BigNum128.from_int(4000), vote_yes=True, timestamp=1234567920, log_list=log_list)
    proposal_passed = gov.tally_votes(proposal_id=proposal_id, timestamp=12345680000, log_list=log_list)
    proposal = gov.get_proposal(proposal_id)
if __name__ == '__main__':
    test_infrastructure_governance()

    def _log_vote(self, proposal_id: str, voter_node_id: str, voter_nod_balance: BigNum128, vote_yes: bool, capped: bool, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_vote', 'proposal_id': proposal_id, 'voter_node_id': voter_node_id, 'voter_nod_balance': voter_nod_balance.to_decimal_string(), 'vote': 'yes' if vote_yes else 'no', 'capped': capped, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_vote', 'details': event_data, 'event_hash': event_hash, 'result': voter_nod_balance.to_decimal_string(), 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_tally_result(self, proposal_id: str, passed: bool, reason: str, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_tally', 'proposal_id': proposal_id, 'result': 'passed' if passed else 'rejected', 'reason': reason, 'yes_votes': proposal.yes_votes.to_decimal_string() if proposal else '0', 'no_votes': proposal.no_votes.to_decimal_string() if proposal else '0', 'quorum_required': proposal.quorum_required.to_decimal_string() if proposal else '0', 'quorum_met': passed or reason == 'vote_result', 'execution_eligible': passed, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_tally', 'details': event_data, 'event_hash': event_hash, 'result': '1' if passed else '0', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_execution(self, proposal_id: str, execution_result: Dict[str, Any], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_execution', 'proposal_id': proposal_id, 'execution_result': execution_result, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_execution', 'details': event_data, 'event_hash': event_hash, 'result': 'executed', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_cancellation(self, proposal_id: str, canceller_node_id: str, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_cancellation', 'proposal_id': proposal_id, 'canceller_node_id': canceller_node_id, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_cancellation', 'details': event_data, 'event_hash': event_hash, 'result': 'cancelled', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

    def _log_expiry(self, proposal_id: str, current_timestamp: int, voting_end_timestamp: int, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, timestamp: int=0):
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
        event_data = {'operation': 'infrastructure_expiry', 'proposal_id': proposal_id, 'current_timestamp': current_timestamp, 'voting_end_timestamp': voting_end_timestamp, 'time_elapsed': current_timestamp - voting_end_timestamp, 'timestamp': timestamp}
        event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        log_list.append({'operation': 'infrastructure_expiry', 'details': event_data, 'event_hash': event_hash, 'result': 'expired', 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': timestamp})

def test_infrastructure_governance():
    """Test the InfrastructureGovernance implementation."""
    cm = CertifiedMath()
    gov = InfrastructureGovernance(cm, quorum_threshold='0.5')
    total_nod_supply = BigNum128.from_int(10000)
    proposal_id = gov.create_proposal(title='Increase Storage Replication Factor', description='Increase the storage replication factor from 3 to 5 for improved redundancy', proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR, proposer_node_id='node_0xabc123', parameters={'current_factor': 3, 'proposed_factor': 5}, total_nod_supply=total_nod_supply, creation_timestamp=1234567890, voting_duration_blocks=100)
    log_list = []
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xabc123', voter_nod_balance=BigNum128.from_int(3000), vote_yes=True, timestamp=1234567900, log_list=log_list)
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xdef456', voter_nod_balance=BigNum128.from_int(2000), vote_yes=False, timestamp=1234567910, log_list=log_list)
    gov.cast_vote(proposal_id=proposal_id, voter_node_id='node_0xghi789', voter_nod_balance=BigNum128.from_int(4000), vote_yes=True, timestamp=1234567920, log_list=log_list)
    proposal_passed = gov.tally_votes(proposal_id=proposal_id, timestamp=12345680000, log_list=log_list)
    proposal = gov.get_proposal(proposal_id)
if __name__ == '__main__':
    test_infrastructure_governance()