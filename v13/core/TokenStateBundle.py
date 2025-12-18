"""
TokenStateBundle.py - Deterministic Token State Bundle for QFS V13

Implements the TokenStateBundle class for creating deterministic,
AGI-signed snapshots of all token states that comply with
Zero-Simulation requirements and Post-Quantum Cryptography.
"""

import json
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    from ..libs.CertifiedMath import BigNum128, CertifiedMath
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
    except ImportError:
        from libs.CertifiedMath import BigNum128, CertifiedMath


@dataclass
class TokenStateBundle:
    """
    Immutable, PQC-signed snapshot of all token states.
    This is the single source of truth for the HSMF ActionCostEngine.

    All state values are represented as BigNum128 instances
    to maintain Zero-Simulation Compliance (no floats).

    System parameters (λ1, λ2, C_CRIT) are decoupled and validated separately
    to ensure they come from an AGI-signed source.
    """

    chr_state: Dict[str, Any]
    flx_state: Dict[str, Any]
    psi_sync_state: Dict[str, Any]
    atr_state: Dict[str, Any]
    res_state: Dict[str, Any]
    nod_state: Dict[str, Any]
    storage_metrics: Dict[str, Any]
    signature: str
    timestamp: int
    bundle_id: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]
    lambda1: BigNum128
    lambda2: BigNum128
    c_crit: BigNum128
    parameters: Dict[str, BigNum128]

    def __post_init__(self):
        """Validate the token state bundle upon creation."""
        if self.parameters is None:
            self.parameters = {
                "beta_penalty": BigNum128.from_int(100000000),
                "phi": BigNum128(1618033988749894848),
            }
        if self.storage_metrics is None:
            self.storage_metrics = {
                "storage_bytes_stored": {},
                "storage_uptime_bucket": {},
                "storage_proofs_verified": {},
            }
        self._validate_states()
        self._validate_parameters()

    def _validate_states(self):
        """Validate that all token states are properly structured."""
        required_states = [
            self.chr_state,
            self.flx_state,
            self.psi_sync_state,
            self.atr_state,
            self.res_state,
            self.nod_state,
        ]
        for i, state in enumerate(required_states):
            if not isinstance(state, dict):
                raise ValueError(f"Token state {i} must be a dictionary")
        if not isinstance(self.storage_metrics, dict):
            raise ValueError("Storage metrics must be a dictionary")
        required_storage_fields = [
            "storage_bytes_stored",
            "storage_uptime_bucket",
            "storage_proofs_verified",
        ]
        for i in range(len(required_storage_fields)):
            field = required_storage_fields[i]
            if field not in self.storage_metrics:
                self.storage_metrics[field] = {}

    def _validate_parameters(self):
        """Validate that system parameters are BigNum128 instances."""
        required_params = [self.lambda1, self.lambda2, self.c_crit]
        param_names = ["lambda1", "lambda2", "c_crit"]
        for param, name in zip(required_params, param_names):
            if not isinstance(param, BigNum128):
                raise ValueError(
                    f"System parameter {name} must be a BigNum128 instance"
                )

    def validate_signature(self, public_key_bytes: bytes) -> bool:
        """
        Verify the PQC signature using the PQC module.

        Args:
            public_key_bytes: Public key as bytes for signature validation

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            from ..libs.PQC import PQC
        except ImportError:
            try:
                from v13.libs.PQC import PQC
            except ImportError:
                try:
                    from libs.PQC import PQC
                except ImportError:
                    return False
        try:
            data_to_verify = self.to_dict(include_signature=False)
            signature_bytes = bytes.fromhex(self.signature)
            result = PQC.verify_signature(
                public_key=public_key_bytes,
                data=data_to_verify,
                signature=signature_bytes,
                log_list=[],
                pqc_cid=f"{self.pqc_cid}_VERIFY",
                quantum_metadata=self.quantum_metadata,
                deterministic_timestamp=self.timestamp,
            )
            return result.is_valid
        except Exception:
            return False

    def get_coherence_metric(self) -> BigNum128:
        """
        Retrieves the primary Survival Metric (S_CHR or C_system) needed
        for the ActionCostEngine's Survival Imperative check.

        Returns:
            BigNum128: The S_CHR value as a BigNum128 instance.
        """
        coherence_metric = self.chr_state.get("coherence_metric", "0.0")
        if isinstance(coherence_metric, BigNum128):
            return coherence_metric
        else:
            return BigNum128.from_string(str(coherence_metric))

    def get_resonance_metric(self) -> BigNum128:
        """
        Retrieves the Inertial Resistance Metric (S_RES or I_eff) needed
        for the base Action Cost calculation.

        Returns:
            BigNum128: The S_RES value as a BigNum128 instance.
        """
        resonance_str = self.res_state.get("inertial_metric", "0.0")
        return BigNum128.from_string(str(resonance_str))

    def get_flux_metric(self) -> BigNum128:
        """
        Retrieves the Flux Metric (S_FLX or ΔΛ) for the HSMF calculation.

        Returns:
            BigNum128: The S_FLX value as a BigNum128 instance.
        """
        flux_str = self.flx_state.get("scaling_metric", "0.0")
        return BigNum128.from_string(str(flux_str))

    def get_psi_sync_metric(self) -> BigNum128:
        """
        Retrieves the Psi Sync Metric (S_ΨSync or ΔH) for the HSMF calculation.

        Returns:
            BigNum128: The S_ΨSync value as a BigNum128 instance.
        """
        psi_sync_str = self.psi_sync_state.get("frequency_metric", "0.0")
        return BigNum128.from_string(str(psi_sync_str))

    def get_atr_metric(self) -> BigNum128:
        """
        Retrieves the Attractor Metric (S_ATR) for the HSMF calculation.

        Returns:
            BigNum128: The S_ATR value as a BigNum128 instance.
        """
        atr_str = self.atr_state.get("directional_metric", "0.0")
        return BigNum128.from_string(str(atr_str))

    def get_c_holo_proxy(self) -> BigNum128:
        """
        Retrieves the C_holo proxy metric (1 / (1 + total_dissonance)).

        Returns:
            BigNum128: The C_holo proxy value as a BigNum128 instance.
        """
        c_holo_str = self.chr_state.get("c_holo_proxy", "1.0")
        return BigNum128.from_string(str(c_holo_str))

    def to_dict(self, include_signature: bool = True) -> Dict[str, Any]:
        """
        Convert the TokenStateBundle to a dictionary representation.

        Args:
            include_signature: Whether to include the signature in the dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the bundle
        """
        chr_state_serializable = {}
        for key, value in sorted(self.chr_state.items()):
            if hasattr(value, "to_decimal_string"):
                chr_state_serializable[key] = value.to_decimal_string()
            else:
                chr_state_serializable[key] = value
        flx_state_serializable = {}
        for key, value in sorted(self.flx_state.items()):
            if isinstance(value, list):
                serialized_list = []
                for i in range(len(value)):
                    item = value[i]
                    if hasattr(item, "to_decimal_string"):
                        serialized_list.append(item.to_decimal_string())
                    else:
                        serialized_list.append(item)
                flx_state_serializable[key] = serialized_list
            elif hasattr(value, "to_decimal_string"):
                flx_state_serializable[key] = value.to_decimal_string()
            else:
                flx_state_serializable[key] = value
        psi_sync_state_serializable = {}
        for key, value in sorted(self.psi_sync_state.items()):
            if hasattr(value, "to_decimal_string"):
                psi_sync_state_serializable[key] = value.to_decimal_string()
            else:
                psi_sync_state_serializable[key] = value
        atr_state_serializable = {}
        for key, value in sorted(self.atr_state.items()):
            if hasattr(value, "to_decimal_string"):
                atr_state_serializable[key] = value.to_decimal_string()
            else:
                atr_state_serializable[key] = value
        res_state_serializable = {}
        for key, value in sorted(self.res_state.items()):
            if hasattr(value, "to_decimal_string"):
                res_state_serializable[key] = value.to_decimal_string()
            else:
                res_state_serializable[key] = value
        nod_state_serializable = {}
        for key, value in sorted(self.nod_state.items()):
            if hasattr(value, "to_decimal_string"):
                nod_state_serializable[key] = value.to_decimal_string()
            else:
                nod_state_serializable[key] = value
        storage_metrics_serializable = {}
        for key, value in sorted(self.storage_metrics.items()):
            if isinstance(value, dict):
                nested_dict = {}
                for nested_key, nested_value in sorted(value.items()):
                    if hasattr(nested_value, "to_decimal_string"):
                        nested_dict[nested_key] = nested_value.to_decimal_string()
                    else:
                        nested_dict[nested_key] = nested_value
                storage_metrics_serializable[key] = nested_dict
            elif hasattr(value, "to_decimal_string"):
                storage_metrics_serializable[key] = value.to_decimal_string()
            else:
                storage_metrics_serializable[key] = value
        parameters_serializable = {}
        for key, value in sorted(self.parameters.items()):
            if hasattr(value, "to_decimal_string"):
                parameters_serializable[key] = value.to_decimal_string()
            else:
                parameters_serializable[key] = value
        bundle_data = {
            "chr_state": chr_state_serializable,
            "flx_state": flx_state_serializable,
            "psi_sync_state": psi_sync_state_serializable,
            "atr_state": atr_state_serializable,
            "res_state": res_state_serializable,
            "nod_state": nod_state_serializable,
            "storage_metrics": storage_metrics_serializable,
            "timestamp": getattr(self, "timestamp", 0),
            "bundle_id": self.bundle_id,
            "pqc_cid": self.pqc_cid,
            "quantum_metadata": self.quantum_metadata,
            "lambda1": self.lambda1.to_decimal_string(),
            "lambda2": self.lambda2.to_decimal_string(),
            "c_crit": self.c_crit.to_decimal_string(),
            "parameters": parameters_serializable,
        }
        if include_signature and self.signature:
            bundle_data["signature"] = self.signature
        return bundle_data

    def serialize_for_hash(self) -> str:
        """
        Serialize the TokenStateBundle to a unique, deterministic string for hashing.
        This is required for QFS V13 to use the bundle as a graph node key.

        Returns:
            str: Deterministic JSON string representation of the bundle (excluding signature)
        """
        bundle_dict = self.to_dict(include_signature=False)
        return json.dumps(bundle_dict, sort_keys=True, separators=(",", ":"))

    def get_deterministic_hash(self, include_signature: bool = True) -> str:
        """
        Generate a deterministic SHA-256 hash of the TokenStateBundle.
        This is used for bundle identification and integrity verification.

        Args:
            include_signature: Whether to include the signature in the hash calculation

        Returns:
            str: SHA-256 hash as hexadecimal string
        """
        serialized = json.dumps(
            self.to_dict(include_signature=include_signature),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def check_survival_imperative(self) -> bool:
        """
        Check if the survival imperative is satisfied: S_CHR > C_CRIT.

        Returns:
            bool: True if survival imperative is satisfied
        """
        s_chr = self.get_coherence_metric()
        return s_chr.value > self.c_crit.value


def create_token_state_bundle(
    chr_state: Dict[str, Any],
    flx_state: Dict[str, Any],
    psi_sync_state: Dict[str, Any],
    atr_state: Dict[str, Any],
    res_state: Dict[str, Any],
    nod_state: Dict[str, Any],
    lambda1: BigNum128,
    lambda2: BigNum128,
    c_crit: BigNum128,
    pqc_cid: str,
    timestamp: int,
    storage_metrics: Optional[Dict[str, Any]] = None,
    quantum_metadata: Optional[Dict[str, Any]] = None,
    bundle_id: Optional[str] = None,
    parameters: Optional[Dict[str, BigNum128]] = None,
) -> TokenStateBundle:
    """
    Create a new TokenStateBundle with deterministic properties.

    Args:
        chr_state: Coheron token state
        flx_state: Flux token state
        psi_sync_state: ΨSync token state
        atr_state: Attractor token state
        res_state: Resonance token state
        nod_state: Node Operator Determination token state (NOD)
        lambda1: Weight for S_FLX component
        lambda2: Weight for S_PsiSync component
        c_crit: Critical coherence threshold
        pqc_cid: PQC correlation ID
        timestamp: Deterministic timestamp (required for Zero-Simulation compliance)
        storage_metrics: Storage contribution metrics per node (Phase 3 extension)
        quantum_metadata: Quantum metadata for audit trail
        bundle_id: Unique bundle identifier (defaults to hash)
        parameters: Configuration parameters (Section 3.2)

    Returns:
        TokenStateBundle: New token state bundle instance
    """
    if bundle_id is None:
        temp_bundle = TokenStateBundle(
            chr_state=chr_state,
            flx_state=flx_state,
            psi_sync_state=psi_sync_state,
            atr_state=atr_state,
            res_state=res_state,
            nod_state=nod_state,
            storage_metrics=storage_metrics
            or {
                "storage_bytes_stored": {},
                "storage_uptime_bucket": {},
                "storage_proofs_verified": {},
            },
            signature="",
            timestamp=timestamp,
            bundle_id="",
            pqc_cid=pqc_cid,
            quantum_metadata=quantum_metadata or {},
            lambda1=lambda1,
            lambda2=lambda2,
            c_crit=c_crit,
            parameters=parameters
            or {
                "beta_penalty": BigNum128.from_int(100000000),
                "phi": BigNum128(1618033988749894848),
            },
        )
        bundle_id = temp_bundle.get_deterministic_hash(include_signature=False)
    return TokenStateBundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        nod_state=nod_state,
        storage_metrics=storage_metrics
        or {
            "storage_bytes_stored": {},
            "storage_uptime_bucket": {},
            "storage_proofs_verified": {},
        },
        signature="",
        timestamp=timestamp,
        bundle_id=bundle_id,
        pqc_cid=pqc_cid,
        quantum_metadata=quantum_metadata or {},
        lambda1=lambda1,
        lambda2=lambda2,
        c_crit=c_crit,
        parameters=parameters
        or {
            "beta_penalty": BigNum128.from_int(100000000),
            "phi": BigNum128(1618033988749894848),
        },
    )


def load_token_state_bundle(bundle_data: Dict[str, Any]) -> TokenStateBundle:
    """
    Load a TokenStateBundle from serialized data.

    Args:
        bundle_data: Dictionary containing token state bundle data

    Returns:
        TokenStateBundle: Loaded token state bundle
    """
    parameters = {}
    if "parameters" in bundle_data:
        for key, value in sorted(bundle_data["parameters"].items()):
            parameters[key] = BigNum128.from_string(str(value))
    else:
        parameters = {
            "beta_penalty": BigNum128.from_string("100000000.0"),
            "phi": BigNum128.from_string("1.618033988749894848"),
        }
    storage_metrics = bundle_data.get("storage_metrics", {})
    if "storage_bytes_stored" in storage_metrics:
        converted_storage_bytes = {}
        for node_id, value in sorted(storage_metrics["storage_bytes_stored"].items()):
            if isinstance(value, str):
                converted_storage_bytes[node_id] = BigNum128.from_string(value)
            else:
                converted_storage_bytes[node_id] = value
        storage_metrics["storage_bytes_stored"] = converted_storage_bytes
    return TokenStateBundle(
        chr_state=bundle_data.get("chr_state", {}),
        flx_state=bundle_data.get("flx_state", {}),
        psi_sync_state=bundle_data.get("psi_sync_state", {}),
        atr_state=bundle_data.get("atr_state", {}),
        res_state=bundle_data.get("res_state", {}),
        nod_state=bundle_data.get("nod_state", {}),
        storage_metrics=storage_metrics,
        signature=bundle_data.get("signature", ""),
        timestamp=bundle_data.get("timestamp", 0),
        bundle_id=bundle_data.get("bundle_id", ""),
        pqc_cid=bundle_data.get("pqc_cid", ""),
        quantum_metadata=bundle_data.get("quantum_metadata", {}),
        lambda1=BigNum128.from_string(
            bundle_data.get("lambda1", "1.618033988749894848")
        ),
        lambda2=BigNum128.from_string(
            bundle_data.get("lambda2", "0.618033988749894848")
        ),
        c_crit=BigNum128.from_string(bundle_data.get("c_crit", "1.0")),
        parameters=parameters,
    )
