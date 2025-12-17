"""
aegis_api.py - Secure API Gateway for QFS V13 with Telemetry Snapshot Infrastructure

Implements the AEGIS API Gateway for receiving transaction bundles,
validating PQC signatures, instantiating log contexts, and committing
validated state updates with PQC-signed finality seals.

V13.6 ENHANCEMENTS:
- Deterministic AEGIS telemetry snapshots (hash-anchored, versioned)
- AEGIS offline/degraded safe degradation policy
- Constitutional guard integration
- NOD-I4 deterministic replay support
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from ..libs.CertifiedMath import BigNum128, CertifiedMath
from ..core.TokenStateBundle import TokenStateBundle
from ..core.HSMF import HSMF
from ...libs.TreasuryEngine import TreasuryEngine
from ..handlers.CIR302_Handler import CIR302_Handler
from ..libs.PQC import PQC
from ..core.DRV_Packet import DRV_Packet


class AEGISStatus(Enum):
    """AEGIS system operational status."""

    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class AEGISOfflineError(Exception):
    """Raised when AEGIS is offline and telemetry cannot be retrieved."""

    pass


@dataclass
class AEGISTelemetrySnapshot:
    """
    Immutable, versioned AEGIS telemetry snapshot for deterministic replay.

    Constitutional Requirements (NOD-I4):
    - SHA-256 hash of entire snapshot
    - Block height anchoring
    - Schema version for forward compatibility
    - Completeness validation (reject partial data)

    This dataclass replaces live API calls to ensure bit-for-bit replay.
    """

    snapshot_version: str
    block_height: int
    snapshot_timestamp: int
    node_metrics: Dict[str, Dict[str, Any]]
    schema_version: str
    snapshot_hash: str = ""

    def compute_hash(self) -> str:
        """
        Compute deterministic SHA-256 hash of snapshot.

        Returns:
            str: 64-character hex hash
        """
        hash_data = {
            "snapshot_version": self.snapshot_version,
            "block_height": self.block_height,
            "snapshot_timestamp": self.snapshot_timestamp,
            "schema_version": self.schema_version,
            "node_metrics": self.node_metrics,
        }
        data_json = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data_json.encode("utf-8")).hexdigest()

    def validate_completeness(self) -> tuple[bool, Optional[str]]:
        """
        Validate snapshot completeness and structural integrity.

        Constitutional requirement: Reject partial/ambiguous data.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not self.snapshot_version:
            return (False, "Missing snapshot_version")
        if self.block_height < 0:
            return (False, f"Invalid block_height: {self.block_height}")
        if self.snapshot_timestamp <= 0:
            return (False, f"Invalid snapshot_timestamp: {self.snapshot_timestamp}")
        if not self.schema_version:
            return (False, "Missing schema_version")
        if not self.node_metrics or not isinstance(self.node_metrics, dict):
            return (False, "Missing or invalid node_metrics")
        if self.snapshot_hash:
            expected_hash = self.compute_hash()
            if self.snapshot_hash != expected_hash:
                return (
                    False,
                    f"Hash mismatch: expected {expected_hash}, got {self.snapshot_hash}",
                )
        supported_schemas = ["NODE_METRICS_V1"]
        if self.schema_version not in supported_schemas:
            return (False, f"Unsupported schema_version: {self.schema_version}")
        if self.schema_version == "NODE_METRICS_V1":
            for node_id, metrics in sorted(self.node_metrics.items()):
                if not isinstance(metrics, dict):
                    return (False, f"Node {node_id} metrics must be dict")
                required_fields = ["uptime_ratio", "health_score"]
                for field in sorted(required_fields):
                    if field not in metrics:
                        return (
                            False,
                            f"Node {node_id} missing required field: {field}",
                        )
        return (True, None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            "snapshot_version": self.snapshot_version,
            "block_height": self.block_height,
            "snapshot_timestamp": self.snapshot_timestamp,
            "node_metrics": self.node_metrics,
            "schema_version": self.schema_version,
            "snapshot_hash": self.snapshot_hash,
        }


@dataclass
class AEGISRegistrySnapshot:
    """
    Immutable, versioned AEGIS registry snapshot for deterministic node verification.

    Contains:
    - Node registry entries (PQC keys, registration timestamps, revocation status)
    - Block height anchoring
    - SHA-256 hash for integrity
    """

    snapshot_version: str
    block_height: int
    snapshot_timestamp: int
    nodes: Dict[str, Dict[str, Any]]
    schema_version: str
    snapshot_hash: str = ""

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of registry snapshot."""
        hash_data = {
            "snapshot_version": self.snapshot_version,
            "block_height": self.block_height,
            "snapshot_timestamp": self.snapshot_timestamp,
            "schema_version": self.schema_version,
            "nodes": self.nodes,
        }
        data_json = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data_json.encode("utf-8")).hexdigest()

    def validate_completeness(self) -> tuple[bool, Optional[str]]:
        """Validate registry snapshot completeness."""
        if not self.snapshot_version:
            return (False, "Missing snapshot_version")
        if self.block_height < 0:
            return (False, f"Invalid block_height: {self.block_height}")
        if not self.schema_version:
            return (False, "Missing schema_version")
        if not self.nodes or not isinstance(self.nodes, dict):
            return (False, "Missing or invalid nodes")
        if self.snapshot_hash:
            expected_hash = self.compute_hash()
            if self.snapshot_hash != expected_hash:
                return (
                    False,
                    f"Hash mismatch: expected {expected_hash}, got {self.snapshot_hash}",
                )
        return (True, None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "snapshot_version": self.snapshot_version,
            "block_height": self.block_height,
            "snapshot_timestamp": self.snapshot_timestamp,
            "nodes": self.nodes,
            "schema_version": self.schema_version,
            "snapshot_hash": self.snapshot_hash,
        }


@dataclass
class APIResponse:
    """Response from the AEGIS API."""

    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    finality_seal: Optional[str]
    pqc_cid: Optional[str]


class AEGIS_API:
    """
    Secure API Gateway for QFS V13.

    Receives transaction bundles, validates PQC signatures, instantiates log contexts,
    and commits validated state updates with PQC-signed finality seals.
    """

    def __init__(
        self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None
    ):
        """
        Initialize the AEGIS API Gateway with V13.6 telemetry snapshot infrastructure.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing API responses
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.hsmf = HSMF(cm_instance)
        self.treasury_engine = TreasuryEngine(cm_instance, pqc_key_pair)
        self.cir302_handler = CIR302_Handler(cm_instance, pqc_key_pair)
        self.quantum_metadata = {
            "component": "AEGIS_API",
            "version": "QFS-V13.6-TELEMETRY",
            "timestamp": None,
            "pqc_scheme": "Dilithium-5",
        }
        self.aegis_status = AEGISStatus.OPERATIONAL
        self.snapshot_cache: Dict[int, AEGISTelemetrySnapshot] = {}
        self.registry_cache: Dict[int, AEGISRegistrySnapshot] = {}
        self.aegis_offline_triggered = False

    def get_telemetry_snapshot(
        self,
        block_height: int,
        deterministic_timestamp: int,
        log_list: List[Dict[str, Any]],
    ) -> AEGISTelemetrySnapshot:
        """
        Get deterministic AEGIS telemetry snapshot for given block height.

        Constitutional Requirements:
        - Versioned, hash-anchored snapshot (NOD-I4)
        - Completeness validation (reject partial data)
        - Block height anchoring for replay

        For replay: Fetch historical snapshot by block_height from cache/ledger.
        For live: Query AEGIS (stub), hash result, cache for future replay.

        Args:
            block_height: Block height to query telemetry for
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            log_list: Audit log list

        Returns:
            AEGISTelemetrySnapshot: Versioned, hash-anchored snapshot

        Raises:
            AEGISOfflineError: If AEGIS is offline/degraded
            ValueError: If snapshot is incomplete or invalid
        """
        if block_height in self.snapshot_cache:
            cached_snapshot = self.snapshot_cache[block_height]
            log_list.append(
                {
                    "operation": "aegis_snapshot_cache_hit",
                    "block_height": block_height,
                    "snapshot_hash": cached_snapshot.snapshot_hash,
                    "timestamp": deterministic_timestamp,
                }
            )
            return cached_snapshot
        if self.aegis_status == AEGISStatus.OFFLINE:
            raise AEGISOfflineError(f"AEGIS offline at block {block_height}")
        raw_telemetry = self._query_aegis_telemetry(block_height)
        snapshot = AEGISTelemetrySnapshot(
            snapshot_version="AEGIS_SNAPSHOT_V1",
            block_height=block_height,
            snapshot_timestamp=deterministic_timestamp,
            node_metrics=raw_telemetry,
            schema_version="NODE_METRICS_V1",
        )
        snapshot.snapshot_hash = snapshot.compute_hash()
        is_valid, error_message = snapshot.validate_completeness()
        if not is_valid:
            log_list.append(
                {
                    "operation": "aegis_snapshot_validation_failed",
                    "block_height": block_height,
                    "error": error_message,
                    "timestamp": deterministic_timestamp,
                }
            )
            raise ValueError(f"Incomplete AEGIS telemetry snapshot: {error_message}")
        self.snapshot_cache[block_height] = snapshot
        log_list.append(
            {
                "operation": "aegis_snapshot_created",
                "block_height": block_height,
                "snapshot_hash": snapshot.snapshot_hash,
                "schema_version": snapshot.schema_version,
                "node_count": len(snapshot.node_metrics),
                "timestamp": deterministic_timestamp,
            }
        )
        return snapshot

    def get_registry_snapshot(
        self,
        block_height: int,
        deterministic_timestamp: int,
        log_list: List[Dict[str, Any]],
    ) -> AEGISRegistrySnapshot:
        """
        Get deterministic AEGIS registry snapshot for given block height.

        Args:
            block_height: Block height to query registry for
            deterministic_timestamp: Deterministic timestamp
            log_list: Audit log list

        Returns:
            AEGISRegistrySnapshot: Versioned, hash-anchored registry snapshot

        Raises:
            AEGISOfflineError: If AEGIS is offline
            ValueError: If snapshot is incomplete
        """
        if block_height in self.registry_cache:
            return self.registry_cache[block_height]
        if self.aegis_status == AEGISStatus.OFFLINE:
            raise AEGISOfflineError(f"AEGIS offline at block {block_height}")
        raw_registry = self._query_aegis_registry(block_height)
        snapshot = AEGISRegistrySnapshot(
            snapshot_version="AEGIS_REGISTRY_V1",
            block_height=block_height,
            snapshot_timestamp=deterministic_timestamp,
            nodes=raw_registry,
            schema_version="NODE_REGISTRY_V1",
        )
        snapshot.snapshot_hash = snapshot.compute_hash()
        is_valid, error_message = snapshot.validate_completeness()
        if not is_valid:
            log_list.append(
                {
                    "operation": "aegis_registry_validation_failed",
                    "block_height": block_height,
                    "error": error_message,
                    "timestamp": deterministic_timestamp,
                }
            )
            raise ValueError(f"Incomplete AEGIS registry snapshot: {error_message}")
        self.registry_cache[block_height] = snapshot
        log_list.append(
            {
                "operation": "aegis_registry_snapshot_created",
                "block_height": block_height,
                "snapshot_hash": snapshot.snapshot_hash,
                "node_count": len(snapshot.nodes),
                "timestamp": deterministic_timestamp,
            }
        )
        return snapshot

    def _query_aegis_telemetry(self, block_height: int) -> Dict[str, Dict[str, Any]]:
        """
        Query AEGIS for raw telemetry data (STUB).

        In production, this would:
        - Call AEGIS REST API or gRPC endpoint
        - Authenticate with PQC credentials
        - Handle network errors and retries
        - Enforce rate limits

        For now, returns mock data for testing.

        Args:
            block_height: Block height to query

        Returns:
            Dict[str, Dict[str, Any]]: node_id → metrics
        """
        return {
            "node_alpha": {
                "uptime_ratio": "0.98",
                "health_score": "0.95",
                "conflict_detected": False,
            },
            "node_beta": {
                "uptime_ratio": "0.92",
                "health_score": "0.88",
                "conflict_detected": False,
            },
        }

    def _query_aegis_registry(self, block_height: int) -> Dict[str, Dict[str, Any]]:
        """
        Query AEGIS registry for node entries (STUB).

        Args:
            block_height: Block height to query

        Returns:
            Dict[str, Dict[str, Any]]: node_id → registry entry
        """
        return {
            "node_alpha": {
                "pqc_public_key": "0x" + "a" * 64,
                "pqc_scheme": "Dilithium5",
                "revoked": False,
                "registration_timestamp": 1000000,
            },
            "node_beta": {
                "pqc_public_key": "0x" + "b" * 64,
                "pqc_scheme": "Dilithium5",
                "revoked": False,
                "registration_timestamp": 1000100,
            },
        }

    def _trigger_aegis_offline_policy(
        self, log_list: List[Dict[str, Any]], timestamp: int
    ):
        """
        Trigger AEGIS offline/degraded safe degradation policy.

        Constitutional Requirements (Global AEGIS Offline Policy):
        - Freeze NOD allocation
        - Freeze infrastructure governance
        - Allow user rewards to continue (cached state)
        - Prohibit any telemetry approximation
        - Maintain zero-simulation integrity

        Args:
            log_list: Audit log list
            timestamp: Deterministic timestamp
        """
        if not self.aegis_offline_triggered:
            self.aegis_offline_triggered = True
            self.aegis_status = AEGISStatus.OFFLINE
            log_list.append(
                {
                    "operation": "aegis_offline_policy_triggered",
                    "policy": "freeze_nod_governance_allow_user_rewards",
                    "timestamp": timestamp,
                    "severity": "CRITICAL",
                }
            )

    def process_transaction_bundle(
        self, drv_packet: DRV_Packet, token_bundle: TokenStateBundle, f_atr: BigNum128
    ) -> APIResponse:
        """
        Process a transaction bundle through the full QFS V13 pipeline.

        Args:
            drv_packet: DRV_Packet with PQC signature and deterministic timestamp
            token_bundle: Current token state bundle
            f_atr: Directional force from Utility Oracle

        Returns:
            APIResponse with result and finality seal
        """
        try:
            if not drv_packet.verify_signature(
                self.pqc_public_key if self.pqc_public_key else b""
            ):
                return APIResponse(
                    success=False,
                    data=None,
                    error="Invalid DRV_Packet PQC signature",
                    finality_seal=None,
                    pqc_cid="",
                )
            chain_validation = DRV_Packet.validate_chain(None, drv_packet)
            if not chain_validation.is_valid:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"Invalid DRV_Packet sequence or chain: {chain_validation.error_message}",
                    finality_seal=None,
                    pqc_cid="",
                )
            with CertifiedMath.LogContext() as log_list:
                hsmf_result = self.hsmf.validate_action_bundle(
                    token_bundle=token_bundle,
                    f_atr=f_atr,
                    drv_packet_sequence=drv_packet.sequence,
                    log_list=log_list,
                    pqc_cid=drv_packet.pqc_signature.hex()
                    if drv_packet.pqc_signature
                    else "",
                    quantum_metadata=drv_packet.metadata,
                    raise_on_failure=False,
                )
                if not hsmf_result.is_valid:
                    system_state = {
                        "token_bundle": token_bundle.to_dict(),
                        "drv_packet": drv_packet.to_dict(),
                        "hsmf_errors": hsmf_result.errors,
                        "log_list": log_list,
                    }
                    quarantine_result = self.cir302_handler.trigger_quarantine(
                        reason="HSMF validation failed", system_state=system_state
                    )
                    return APIResponse(
                        success=False,
                        data=None,
                        error="HSMF validation failed",
                        finality_seal=quarantine_result.finality_seal,
                        pqc_cid=quarantine_result.pqc_cid,
                    )
                treasury_result = self.treasury_engine.compute_rewards(
                    hsmf_result=hsmf_result, token_bundle=token_bundle
                )
                if not treasury_result.is_valid:
                    system_state = {
                        "token_bundle": token_bundle.to_dict(),
                        "drv_packet": drv_packet.to_dict(),
                        "treasury_errors": treasury_result.validation_errors,
                        "log_list": log_list,
                    }
                    quarantine_result = self.cir302_handler.trigger_quarantine(
                        reason="Treasury computation failed", system_state=system_state
                    )
                    return APIResponse(
                        success=False,
                        data=None,
                        error="Treasury computation failed",
                        finality_seal=quarantine_result.finality_seal,
                        pqc_cid=quarantine_result.pqc_cid,
                    )
                log_hash = CertifiedMath.get_log_hash(log_list)
                pqc_cid = self._generate_pqc_cid(
                    drv_packet, token_bundle, hsmf_result, treasury_result
                )
                self.quantum_metadata["timestamp"] = str(drv_packet.ttsTimestamp)
                response_data = {
                    "token_bundle": token_bundle.to_dict(),
                    "hsmf_result": {
                        "is_valid": hsmf_result.is_valid,
                        "c_holo": hsmf_result.raw_metrics.get(
                            "c_holo", BigNum128(0)
                        ).to_decimal_string(),
                        "s_flx": hsmf_result.raw_metrics.get(
                            "s_flx", BigNum128(0)
                        ).to_decimal_string(),
                        "s_psi_sync": hsmf_result.raw_metrics.get(
                            "s_psi_sync", BigNum128(0)
                        ).to_decimal_string(),
                        "f_atr": hsmf_result.raw_metrics.get(
                            "f_atr", BigNum128(0)
                        ).to_decimal_string(),
                    },
                    "treasury_result": {
                        "is_valid": treasury_result.is_valid,
                        "total_allocation": treasury_result.total_allocation.to_decimal_string(),
                        "rewards_count": len(treasury_result.rewards),
                    },
                    "log_hash": log_hash,
                    "pqc_cid": pqc_cid,
                    "quantum_metadata": self.quantum_metadata,
                }
                finality_seal = self._sign_finality_seal(response_data, log_list)
                return APIResponse(
                    success=True,
                    data=response_data,
                    error=None,
                    finality_seal=finality_seal,
                    pqc_cid=pqc_cid,
                )
        except Exception as e:
            system_state = {
                "token_bundle": token_bundle.to_dict() if token_bundle else {},
                "drv_packet": drv_packet.to_dict() if drv_packet else {},
                "error": str(e),
            }
            quarantine_result = self.cir302_handler.trigger_quarantine(
                reason=f"Unexpected API error: {str(e)}", system_state=system_state
            )
            return APIResponse(
                success=False,
                data=None,
                error=f"Unexpected API error: {str(e)}",
                finality_seal=quarantine_result.finality_seal,
                pqc_cid=quarantine_result.pqc_cid,
            )

    def _sign_finality_seal(
        self, response_data: Dict[str, Any], log_list: List[Dict[str, Any]]
    ) -> str:
        """
        Sign the finality seal for a validated transaction bundle.

        Args:
            response_data: Response data to sign
            log_list: Log list for PQC operation

        Returns:
            str: Hex representation of PQC signature
        """
        if not self.pqc_private_key:
            return ""
        try:
            response_json = json.dumps(
                response_data, sort_keys=True, separators=(",", ":")
            )
            signature = PQC.sign_data(
                self.pqc_private_key, response_json.encode("utf-8"), log_list
            )
            return signature.hex()
        except Exception as e:
            return ""

    def _generate_pqc_cid(
        self,
        drv_packet: DRV_Packet,
        token_bundle: TokenStateBundle,
        hsmf_result: Any,
        treasury_result: Any,
    ) -> str:
        """
        Generate deterministic PQC correlation ID.

        Args:
            drv_packet: DRV_Packet
            token_bundle: Token state bundle
            hsmf_result: HSMF validation result
            treasury_result: Treasury computation result

        Returns:
            str: Deterministic PQC correlation ID
        """
        data_to_hash = {
            "drv_packet_hash": drv_packet.get_hash(),
            "token_bundle_hash": token_bundle.get_deterministic_hash(),
            "hsmf_valid": hsmf_result.is_valid
            if hasattr(hsmf_result, "is_valid")
            else False,
            "treasury_valid": treasury_result.is_valid
            if hasattr(treasury_result, "is_valid")
            else False,
            "timestamp": drv_packet.ttsTimestamp,
        }
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]


def test_aegis_api():
    """Test the AEGIS_API implementation."""
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    with PQC.LogContext() as pqc_log:
        keypair = PQC.generate_keypair(pqc_log)
        pqc_keypair = (bytes(keypair.private_key), keypair.public_key)
    api = AEGIS_API(cm, pqc_keypair)
    quantum_metadata = {"source": "test", "timestamp": "0", "pqc_scheme": "Dilithium-5"}
    drv_packet = DRV_Packet(
        ttsTimestamp=1234567890,
        sequence=1,
        seed="test_seed",
        metadata={"test": "data"},
        previous_hash="0" * 64,
        pqc_cid="test_pqc_cid",
        quantum_metadata=quantum_metadata,
    )
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85",
    }
    parameters = {
        "beta_penalty": CertifiedMath.from_string("100000000.0"),
        "phi": CertifiedMath.from_string("1.618033988749894848"),
    }
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_signature",
        timestamp=1234567890,
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=CertifiedMath.from_string("0.3"),
        lambda2=CertifiedMath.from_string("0.2"),
        c_crit=CertifiedMath.from_string("0.9"),
        parameters=parameters,
    )
    f_atr = CertifiedMath.from_string("0.85")
    result = api.process_transaction_bundle(drv_packet, token_bundle, f_atr)


if __name__ == "__main__":
    test_aegis_api()
