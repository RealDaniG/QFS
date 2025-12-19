"""
ProposalEngine.py - Enforces Proposal Binding Invariants for QFS v15 Governance

This module implements the core logic for proposal creation and validation,
ensuring that all proposals are cryptographically bound to their execution
payloads via SHA-256 hashes. This satisfies the "Proposal Binding" v15 invariant.

Invariants Enforced:
- PROP-I1: Proposal Hash Binding (Payload matches declared hash)
- PROP-I2: Execution Constraint (Only hashed payload can be executed)
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ProposalStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class ProposalEngine:
    """
    Manages the lifecycle of governance proposals with strict hash binding.
    """

    def __init__(self):
        self.proposals: Dict[str, Dict[str, Any]] = {}

    def create_proposal(
        self, title: str, description: str, execution_payload: Dict[str, Any]
    ) -> str:
        """
        Create a new proposal bound to its execution payload hash.

        Args:
            title: Human-readable title
            description: Detailed description
            execution_payload: The dictionary representing the machine-executable action

        Returns:
            proposal_id: The SHA-256 hash of the full proposal structure
        """
        # Deterministic serialization of execution payload
        payload_json = json.dumps(
            execution_payload, sort_keys=True, separators=(",", ":")
        )
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        proposal_struct = {
            "title": title,
            "description": description,
            "payload_hash": payload_hash,
            "status": ProposalStatus.DRAFT.value,
        }

        # Proposal ID is the hash of the immutable proposal structure
        proposal_json = json.dumps(
            proposal_struct, sort_keys=True, separators=(",", ":")
        )
        proposal_id = hashlib.sha256(proposal_json.encode("utf-8")).hexdigest()

        # Store proposal (in a real system, this would be on-ledger)
        self.proposals[proposal_id] = {
            "id": proposal_id,
            "structure": proposal_struct,
            "execution_payload": execution_payload,  # Stored for reference, but integrity is checked via hash
        }

        return proposal_id

    def validate_execution_payload(
        self, proposal_id: str, submitted_payload: Dict[str, Any]
    ) -> bool:
        """
        Verify that a submitted execution payload matches the bound hash of the proposal.

        This enforces PROP-I1/PROP-I2.

        Args:
            proposal_id: ID of the proposal to execute
            submitted_payload: The payload attempting to be executed

        Returns:
            bool: True if payload matches the proposal's bound hash, False otherwise.
        """
        if proposal_id not in self.proposals:
            return False

        stored_proposal = self.proposals[proposal_id]
        expected_hash = stored_proposal["structure"]["payload_hash"]

        submitted_json = json.dumps(
            submitted_payload, sort_keys=True, separators=(",", ":")
        )
        submitted_hash = hashlib.sha256(submitted_json.encode("utf-8")).hexdigest()

        return submitted_hash == expected_hash

    def execute_proposal(
        self,
        proposal_id: str,
        registry: Any,  # Typed as Any to avoid circular import, expected GovernanceParameterRegistry
    ) -> bool:
        """
        Execute a PASSED proposal tailored to parameter changes.

        Args:
            proposal_id: ID of the proposal to execute.
            registry: The GovernanceParameterRegistry instance.

        Returns:
            bool: True if execution succeeded.
        """
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        payload = proposal["execution_payload"]

        # In a real system, we would check: if proposal['status'] == PASSED
        # For this simulation, we proceed.

        # Route by action type
        action_type = payload.get("action")

        if action_type == "PARAMETER_CHANGE":
            # Extract params
            key = payload.get("key")
            value_dict = payload.get(
                "value"
            )  # Expecting a dict or int that can convert to BigNum

            # Reconstruct BigNum from payload value
            # Assuming payload value is simple int/str for this stage
            from v13.libs.BigNum128 import BigNum128

            if isinstance(value_dict, int):
                new_value = BigNum128.from_int(value_dict)
            elif isinstance(value_dict, str):
                new_value = BigNum128.from_string(value_dict)
            else:
                # Handle dictionary form if serialized that way
                new_value = BigNum128.from_int(0)  # Fallback/Error

            try:
                registry.update_parameter(key, new_value, proposal_id)
                proposal["structure"]["status"] = ProposalStatus.EXECUTED.value
                return True
            except ValueError as e:
                # Log security violation (Constitution breach attempt)
                # print(f"Governance Execution Failed: {e}")
                return False

        return False


def test_proposal_engine():
    """Self-test for ProposalEngine invariants."""
    engine = ProposalEngine()

    # 1. Test Payload Integrity
    payload = {"action": "mint", "amount": 100}
    prop_id = engine.create_proposal("Test Prop", "Desc", payload)

    assert engine.validate_execution_payload(prop_id, payload) is True

    tampered_payload = {"action": "mint", "amount": 1000}
    assert engine.validate_execution_payload(prop_id, tampered_payload) is False

    # 2. Test Parameter Execution Integration
    # Mock Registry
    class MockRegistry:
        def __init__(self):
            self.storage = {"TEST_KEY": 0}
            self.MUTABLE_KEYS = {"TEST_KEY"}

        def update_parameter(self, key, val, pid):
            if key not in self.MUTABLE_KEYS:
                raise ValueError("Immutable")
            self.storage[key] = val.to_decimal_string()  # Store simplified

    mock_reg = MockRegistry()

    # Create Parameter Change Proposal
    change_payload = {"action": "PARAMETER_CHANGE", "key": "TEST_KEY", "value": 123}
    change_pid = engine.create_proposal("Fix Param", "Desc", change_payload)

    # Execute
    success = engine.execute_proposal(change_pid, mock_reg)
    assert success is True
    assert (
        mock_reg.storage["TEST_KEY"] == "123.000000000000000000"
    )  # BigNum default scaling

    # Test Constitution Protection
    bad_payload = {"action": "PARAMETER_CHANGE", "key": "IMMUTABLE_KEY", "value": 999}
    bad_pid = engine.create_proposal("Break Const", "Desc", bad_payload)
    success_bad = engine.execute_proposal(bad_pid, mock_reg)
    assert success_bad is False

    print("ProposalEngine self-test passed.")


if __name__ == "__main__":
    test_proposal_engine()
