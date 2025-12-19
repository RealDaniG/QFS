"""
PoE Artifact Generator for v15.3
Generates schema-compliant Proof-of-Execution artifacts
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess


class PoEArtifactGenerator:
    """Generates v1.0 schema-compliant PoE artifacts."""

    def __init__(self, evidence_dir: str = "evidence/poe_artifacts"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.poe_version = "1.0"

    def _get_commit_hash(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"

    def _sha3_512_hash(self, data: bytes) -> str:
        """Generate SHA3-512 hash."""
        h = hashlib.sha3_512()
        h.update(data)
        return f"sha3_512:{h.hexdigest()}"

    def _canonical_serialize(self, data: Any) -> str:
        """Canonical JSON serialization."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def generate_artifact(
        self,
        proposal_id: str,
        proposal_hash: str,
        epoch: int,
        cycle: int,
        parameter_key: str,
        execution_phase: str,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        vote_breakdown: Dict[str, Any],
        execution_trace: list,
        nod_address: str = "NOD_0x0000000000000000",
    ) -> Dict[str, Any]:
        """
        Generate schema-compliant PoE artifact.

        Args:
            proposal_id: Unique proposal identifier
            proposal_hash: SHA3-512 hash of proposal
            epoch: Governance epoch number
            cycle: Cycle within epoch
            parameter_key: Parameter being changed
            execution_phase: Phase (PROPOSAL, VOTE, EXECUTION)
            before_state: State before execution
            after_state: State after execution
            vote_breakdown: Voting results
            execution_trace: List of operations performed
            nod_address: NOD operator address

        Returns:
            PoE artifact dict conforming to v1.0 schema
        """

        # Generate artifact ID
        artifact_id = f"GOV-{epoch:03d}-{execution_phase[:4]}-{cycle:02d}"

        # Hash states
        before_state_hash = self._sha3_512_hash(
            self._canonical_serialize(before_state).encode()
        )
        after_state_hash = self._sha3_512_hash(
            self._canonical_serialize(after_state).encode()
        )

        # Hash execution trace
        execution_trace_hash = self._sha3_512_hash(
            self._canonical_serialize(execution_trace).encode()
        )

        # Build artifact (without signatures first)
        artifact = {
            "poe_version": self.poe_version,
            "artifact_id": artifact_id,
            "proposal_hash": proposal_hash,
            "governance_scope": {
                "epoch": epoch,
                "cycle": cycle,
                "parameter_key": parameter_key,
            },
            "execution_phase": execution_phase,
            "before_state_hash": before_state_hash,
            "after_state_hash": after_state_hash,
            "vote_breakdown": vote_breakdown,
            "execution_trace_hash": execution_trace_hash,
            "proof_hash": "",  # Computed below
            "signatures": {
                "nod_address": nod_address,
                "dilithium_signature": "base64:PLACEHOLDER",  # TODO: Real PQC signature
                "signature_timestamp": datetime.utcnow().isoformat() + "Z",
            },
            "runtime_info": {
                "code_commit_hash": self._get_commit_hash(),
                "build_hash": "sha3_512:PLACEHOLDER",  # TODO: Real build hash
                "deterministic_session_timestamp_hash": self._sha3_512_hash(
                    datetime.utcnow().isoformat().encode()
                ),
                "python_version": "3.11.7",
                "certifiedmath_version": "1.0.0",
            },
            "replay_instructions": {
                "command": f"python replay_gov_cycle.py --artifact_id {artifact_id}",
                "inputs_file": f"evidence/{artifact_id}-inputs.json",
                "expected_output_hash": "",  # Computed below
            },
        }

        # Compute proof hash (hash of all fields except signatures)
        proof_data = {
            k: v for k, v in artifact.items() if k not in ["signatures", "proof_hash"]
        }
        proof_hash = self._sha3_512_hash(self._canonical_serialize(proof_data).encode())
        artifact["proof_hash"] = proof_hash

        # Set expected output hash (same as proof hash for now)
        artifact["replay_instructions"]["expected_output_hash"] = proof_hash

        return artifact

    def save_artifact(self, artifact: Dict[str, Any]) -> Path:
        """
        Save PoE artifact to file.

        Args:
            artifact: PoE artifact dict

        Returns:
            Path to saved artifact file
        """
        artifact_id = artifact["artifact_id"]
        filepath = self.evidence_dir / f"{artifact_id}.json"

        with open(filepath, "w") as f:
            json.dump(artifact, f, indent=2, sort_keys=True)

        return filepath

    def load_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Load PoE artifact from file.

        Args:
            artifact_id: Artifact ID to load

        Returns:
            PoE artifact dict or None if not found
        """
        filepath = self.evidence_dir / f"{artifact_id}.json"

        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            return json.load(f)

    def verify_artifact(self, artifact: Dict[str, Any]) -> tuple[bool, str]:
        """
        Verify PoE artifact integrity.

        Args:
            artifact: PoE artifact to verify

        Returns:
            (is_valid, message)
        """
        # Check schema version
        if artifact.get("poe_version") != self.poe_version:
            return False, f"Unsupported PoE version: {artifact.get('poe_version')}"

        # Check mandatory fields
        required_fields = [
            "artifact_id",
            "proposal_hash",
            "governance_scope",
            "execution_phase",
            "before_state_hash",
            "after_state_hash",
            "vote_breakdown",
            "execution_trace_hash",
            "proof_hash",
            "signatures",
            "runtime_info",
            "replay_instructions",
        ]

        for field in required_fields:
            if field not in artifact:
                return False, f"Missing required field: {field}"

        # Verify proof hash
        proof_data = {
            k: v for k, v in artifact.items() if k not in ["signatures", "proof_hash"]
        }
        expected_proof_hash = self._sha3_512_hash(
            self._canonical_serialize(proof_data).encode()
        )

        if artifact["proof_hash"] != expected_proof_hash:
            return (
                False,
                f"Proof hash mismatch: {artifact['proof_hash']} != {expected_proof_hash}",
            )

        return True, "Artifact is valid"


# Global instance
_poe_generator = None


def get_poe_generator() -> PoEArtifactGenerator:
    """Get global PoE generator instance."""
    global _poe_generator
    if _poe_generator is None:
        _poe_generator = PoEArtifactGenerator()
    return _poe_generator
