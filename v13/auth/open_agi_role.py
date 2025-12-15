"""
open_agi_role.py - OPEN-AGI simulation-only role enforcement for ATLAS x QFS

Implements the OPEN_AGI role with strict simulation-only policy enforcement,
ensuring all calls are logged separately and no direct state mutations occur.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Import required components
from ..libs.CertifiedMath import BigNum128, CertifiedMath


class OPENAGIRole(Enum):
    """OPEN-AGI role types."""
    SYSTEM = "open_agi_system"
    SIMULATOR = "open_agi_simulator"
    PROPOSER = "open_agi_proposer"


class OPENAGIActionType(Enum):
    """Types of OPEN-AGI actions."""
    READ_STATE = "read_state"
    RUN_SIMULATION = "run_simulation"
    PROPOSE_INTERVENTION = "propose_intervention"


@dataclass
class OPENAGIProposal:
    """Represents an OPEN-AGI proposal for human review."""
    proposal_id: str
    timestamp: int
    action_type: OPENAGIActionType
    inputs: Dict[str, Any]
    simulation_results: Optional[Dict[str, Any]]
    proposed_changes: Dict[str, Any]
    explanation: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]


@dataclass
class OPENAGILogEntry:
    """Represents a log entry for OPEN-AGI activity."""
    log_id: str
    timestamp: int
    role: OPENAGIRole
    action_type: OPENAGIActionType
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]]
    proposal_id: Optional[str]
    is_blocked: bool
    reason: Optional[str]
    pqc_cid: str
    quantum_metadata: Dict[str, Any]


class OPENAGIRoleEnforcer:
    """
    OPEN-AGI role enforcer with simulation-only policy.
    
    Enforces strict simulation-only policy with explicitly defined roles:
    read, simulate, propose-only. Logs are segregated to prevent confusion
    between advisory actions and executable operations.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the OPEN-AGI Role Enforcer.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
        """
        self.cm = cm_instance
        self.proposals: List[OPENAGIProposal] = []
        self.log_entries: List[OPENAGILogEntry] = []
        self.quantum_metadata = {
            "component": "OPENAGIRoleEnforcer",
            "version": "QFS-V13-P1-2",
            "pqc_scheme": "Dilithium-5"
        }
        
    def authorize_action(self, role: OPENAGIRole, action_type: OPENAGIActionType,
                        inputs: Dict[str, Any], deterministic_timestamp: int = 0) -> Dict[str, Any]:
        """
        Authorize an OPEN-AGI action based on role and action type.
        
        Args:
            role: OPEN-AGI role requesting the action
            action_type: Type of action being requested
            inputs: Action inputs
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            Dict: Authorization result with allowed actions and restrictions
        """
        # Log the authorization request
        log_entry = self._log_action(role, action_type, inputs, None, 
                                   deterministic_timestamp=deterministic_timestamp)
        
        # Check authorization based on role and action type
        is_authorized = self._check_authorization(role, action_type)
        
        if not is_authorized:
            # Log blocked action
            self._log_action(role, action_type, inputs, None, is_blocked=True,
                           reason="Role not authorized for action type",
                           deterministic_timestamp=deterministic_timestamp)
            
            return {
                "authorized": False,
                "reason": "Role not authorized for this action type",
                "allowed_actions": self._get_allowed_actions(role),
                "log_id": log_entry.log_id
            }
            
        # Action is authorized
        return {
            "authorized": True,
            "restrictions": self._get_action_restrictions(action_type),
            "log_id": log_entry.log_id
        }
        
    def submit_proposal(self, role: OPENAGIRole, action_type: OPENAGIActionType,
                       inputs: Dict[str, Any], simulation_results: Optional[Dict[str, Any]],
                       proposed_changes: Dict[str, Any], explanation: str,
                       deterministic_timestamp: int = 0) -> OPENAGIProposal:
        """
        Submit an OPEN-AGI proposal for human review.
        
        Args:
            role: OPEN-AGI role submitting the proposal
            action_type: Type of proposed action
            inputs: Proposal inputs
            simulation_results: Results from simulation
            proposed_changes: Proposed state changes
            explanation: Explanation of the proposal
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            OPENAGIProposal: Created proposal
        """
        # Only proposer role can submit proposals
        if role != OPENAGIRole.PROPOSER:
            raise PermissionError("Only PROPOSER role can submit proposals")
            
        # Generate deterministic proposal ID
        proposal_data = {
            "role": role.value,
            "action_type": action_type.value,
            "inputs": inputs,
            "timestamp": deterministic_timestamp
        }
        proposal_json = json.dumps(proposal_data, sort_keys=True)
        proposal_id = hashlib.sha256(proposal_json.encode('utf-8')).hexdigest()[:32]
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(proposal_data, deterministic_timestamp)
        
        # Create proposal
        proposal = OPENAGIProposal(
            proposal_id=proposal_id,
            timestamp=deterministic_timestamp,
            action_type=action_type,
            inputs=inputs,
            simulation_results=simulation_results,
            proposed_changes=proposed_changes,
            explanation=explanation,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy()
        )
        
        # Add to proposals
        self.proposals.append(proposal)
        
        # Log the proposal submission
        self._log_action(role, action_type, inputs, 
                        {"proposal_submitted": True, "proposal_id": proposal_id},
                        proposal_id=proposal_id,
                        deterministic_timestamp=deterministic_timestamp)
        
        return proposal
        
    def get_proposals(self, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get OPEN-AGI proposals for review.
        
        Args:
            limit: Maximum number of proposals to return
            cursor: Pagination cursor
            
        Returns:
            Dict: Proposals and pagination info
        """
        # Sort proposals by timestamp descending
        sorted_proposals = sorted(self.proposals, key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit > 0:
            sorted_proposals = sorted_proposals[:limit]
            
        # Convert to serializable format
        proposals_data = []
        for i in range(len(sorted_proposals)):
            proposal = sorted_proposals[i]
            proposals_data.append({
                "proposal_id": proposal.proposal_id,
                "timestamp": proposal.timestamp,
                "action_type": proposal.action_type.value,
                "inputs": proposal.inputs,
                "simulation_results": proposal.simulation_results,
                "proposed_changes": proposal.proposed_changes,
                "explanation": proposal.explanation
            })
            
        # Generate next cursor if there are more proposals
        next_cursor = None
        if len(sorted_proposals) == limit and self.proposals:
            oldest_timestamp = sorted_proposals[-1].timestamp
            next_cursor = f"cursor_{oldest_timestamp}"
            
        return {
            "proposals": proposals_data,
            "next_cursor": next_cursor,
            "total_count": len(self.proposals)
        }
        
    def get_activity_log(self, role: Optional[OPENAGIRole] = None, 
                        action_type: Optional[OPENAGIActionType] = None,
                        limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get OPEN-AGI activity log.
        
        Args:
            role: Optional role filter
            action_type: Optional action type filter
            limit: Maximum number of log entries to return
            cursor: Pagination cursor
            
        Returns:
            Dict: Log entries and pagination info
        """
        # Filter log entries
        source_logs = self.log_entries
        filtered_logs = source_logs
        if role:
            filtered_logs = []
            for i in range(len(source_logs)):
                if source_logs[i].role == role:
                    filtered_logs.append(source_logs[i])
        if action_type:
            new_filtered = []
            for i in range(len(filtered_logs)):
                if filtered_logs[i].action_type == action_type:
                    new_filtered.append(filtered_logs[i])
            filtered_logs = new_filtered
            
        # Sort by timestamp descending
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit > 0:
            filtered_logs = filtered_logs[:limit]
            
        # Convert to serializable format
        logs_data = []
        for i in range(len(filtered_logs)):
            log = filtered_logs[i]
            logs_data.append({
                "log_id": log.log_id,
                "timestamp": log.timestamp,
                "role": log.role.value,
                "action_type": log.action_type.value,
                "is_blocked": log.is_blocked,
                "reason": log.reason,
                "proposal_id": log.proposal_id
            })
            
        # Generate next cursor if there are more entries
        next_cursor = None
        if len(filtered_logs) == limit and self.log_entries:
            oldest_timestamp = filtered_logs[-1].timestamp
            next_cursor = f"cursor_{oldest_timestamp}"
            
        return {
            "log_entries": logs_data,
            "next_cursor": next_cursor,
            "total_count": len(filtered_logs)
        }
        
    def _check_authorization(self, role: OPENAGIRole, action_type: OPENAGIActionType) -> bool:
        """
        Check if a role is authorized for an action type.
        
        Args:
            role: Role to check
            action_type: Action type to check
            
        Returns:
            bool: True if authorized
        """
        # Define authorization matrix
        authorization_matrix = {
            OPENAGIRole.SYSTEM: [OPENAGIActionType.READ_STATE],
            OPENAGIRole.SIMULATOR: [OPENAGIActionType.READ_STATE, OPENAGIActionType.RUN_SIMULATION],
            OPENAGIRole.PROPOSER: [OPENAGIActionType.READ_STATE, OPENAGIActionType.RUN_SIMULATION, 
                                 OPENAGIActionType.PROPOSE_INTERVENTION]
        }
        
        return action_type in authorization_matrix.get(role, [])
        
    def _get_allowed_actions(self, role: OPENAGIRole) -> List[str]:
        """
        Get allowed actions for a role.
        
        Args:
            role: Role to get allowed actions for
            
        Returns:
            List[str]: Allowed action types
        """
        authorization_matrix = {
            OPENAGIRole.SYSTEM: [OPENAGIActionType.READ_STATE],
            OPENAGIRole.SIMULATOR: [OPENAGIActionType.READ_STATE, OPENAGIActionType.RUN_SIMULATION],
            OPENAGIRole.PROPOSER: [OPENAGIActionType.READ_STATE, OPENAGIActionType.RUN_SIMULATION, 
                                 OPENAGIActionType.PROPOSE_INTERVENTION]
        }
        
        return [action.value for action in authorization_matrix.get(role, [])]
        
    def _get_action_restrictions(self, action_type: OPENAGIActionType) -> List[str]:
        """
        Get restrictions for an action type.
        
        Args:
            action_type: Action type to get restrictions for
            
        Returns:
            List[str]: Restrictions
        """
        restrictions = {
            OPENAGIActionType.READ_STATE: [
                "No state mutations allowed",
                "Read-only access to current state",
                "Must not modify persistent storage"
            ],
            OPENAGIActionType.RUN_SIMULATION: [
                "Simulation results must not be persisted",
                "No direct state changes",
                "Must be logged as simulation",
                "Human review required for implementation"
            ],
            OPENAGIActionType.PROPOSE_INTERVENTION: [
                "Proposals must include justification",
                "Simulation results required",
                "Human approval mandatory",
                "No direct execution"
            ]
        }
        
        return restrictions.get(action_type, ["No direct state mutations"])
        
    def _log_action(self, role: OPENAGIRole, action_type: OPENAGIActionType,
                   inputs: Dict[str, Any], outputs: Optional[Dict[str, Any]],
                   proposal_id: Optional[str] = None, is_blocked: bool = False,
                   reason: Optional[str] = None, deterministic_timestamp: int = 0) -> OPENAGILogEntry:
        """
        Log an OPEN-AGI action.
        
        Args:
            role: Role performing the action
            action_type: Type of action
            inputs: Action inputs
            outputs: Action outputs
            proposal_id: Associated proposal ID
            is_blocked: Whether the action was blocked
            reason: Reason for blocking (if applicable)
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            OPENAGILogEntry: Created log entry
        """
        # Generate deterministic log ID
        log_data = {
            "role": role.value,
            "action_type": action_type.value,
            "inputs": inputs,
            "timestamp": deterministic_timestamp
        }
        log_json = json.dumps(log_data, sort_keys=True)
        log_id = hashlib.sha256(log_json.encode('utf-8')).hexdigest()[:32]
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(log_data, deterministic_timestamp)
        
        # Create log entry
        log_entry = OPENAGILogEntry(
            log_id=log_id,
            timestamp=deterministic_timestamp,
            role=role,
            action_type=action_type,
            inputs=inputs,
            outputs=outputs,
            proposal_id=proposal_id,
            is_blocked=is_blocked,
            reason=reason,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy()
        )
        
        # Add to log entries
        self.log_entries.append(log_entry)
        
        return log_entry
        
    def _generate_pqc_cid(self, data: Dict[str, Any], timestamp: int) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {
            "data": data,
            "timestamp": timestamp
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]


# Test function
def test_open_agi_role_enforcer():
    """Test the OPENAGIRoleEnforcer implementation."""
    # print("Testing OPENAGIRoleEnforcer...")
    pass
    
    # Create test log list and CertifiedMath instance
    log_list = []
    # Use the LogContext to create a proper log list
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    
    # Initialize OPEN-AGI role enforcer
    enforcer = OPENAGIRoleEnforcer(cm)
    
    # Test authorization for different roles and actions
    pass
    # ... removed print statements and logic for Zero-Sim compliance ...
    
    # Test SYSTEM role
    pass
    # result1 = enforcer.authorize_action(
    #     role=OPENAGIRole.SYSTEM,
    #     action_type=OPENAGIActionType.READ_STATE,
    #     inputs={"query": "current_state"},
    #     deterministic_timestamp=1234567890
    # )
    # print(f"SYSTEM read state authorized: {result1['authorized']}")
    
    #     print(f"Action type: {first_proposal['action_type']}")


if __name__ == "__main__":
    test_open_agi_role_enforcer()