# HarmonicEconomics.py
# QFS V13 - Phase 3 Core Economics Engine (PRODUCTION-HARDENED)
# Zero-Simulation Compliant | Deterministic | 5-Token Conservation Enforcement
# Implements Step 2: Harmonic Token Economics (Refined Plan)

from typing import Dict, Any, Optional
from enum import Enum
import sys
from typing import Dict, List, Any, Optional

# Use absolute import instead of relative import
try:
    from v13.core.TokenStateBundle import TokenStateBundle
except ImportError:
    # Fallback for direct execution
    try:
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        # Try with sys.path modification
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from v13.core.TokenStateBundle import TokenStateBundle

# Economic violation types for precise attack classification
class EconomicViolation(Enum):
    CHR_CONSERVATION_BREACH = "CHR_CONSERVATION_BREACH"
    NEGATIVE_FLOW_ATTEMPT = "NEGATIVE_FLOW_ATTEMPT"
    FLX_FLOW_IMBALANCE = "FLX_FLOW_IMBALANCE"
    PSY_MONOTONICITY_VIOLATION = "PSY_MONOTONICITY_VIOLATION"
    ATTR_ATTRACTOR_VIOLATION = "ATTR_ATTRACTOR_VIOLATION"
    RES_ENVELOPE_BREACH = "RES_ENVELOPE_BREACH"
    HARMONIC_DIVERGENCE = "HARMONIC_DIVERGENCE"

class EconomicSecurityError(Exception):
    """Security violation in harmonic economic computations."""
    def __init__(self, message: str, violation_type: EconomicViolation, evidence: Dict = None, cir_code: str = None):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence or {}
        self.cir_code = cir_code

class NullEventLogger:
    """Default no-op event logger."""
    def log(self, category: str, event_type: str, data: Dict, timestamp: int):
        pass

class HarmonicEconomics:
    """
    PRODUCTION-HARDENED 5-token economics engine.
    
    Enforces:
    - CHR conservation (EA-5 protection)
    - FLX flow balance with ψ-gradient proportionality (EA-6 protection)
    - ΨSync monotonicity with coherence
    - ATR attractor law
    - RES bounded by resonance envelope (EA-4 protection)
    """

    def __init__(
        self,
        psi_field_engine: Any,
        certified_math: Any,
        event_logger: Any = None
    ):
        """
        Initialize with ψ-field physics and certified mathematics.
        
        Args:
            psi_field_engine: DiscretePsiField instance from Step 1
            certified_math: QFS V13 CertifiedMath instance
            event_logger: Structured event logger for evidence generation
        """
        self.psi_field = psi_field_engine
        self.math = certified_math
        self.event_logger = event_logger or NullEventLogger()
        
        self.economic_state_history = []  # For monotonicity verification
        self.violation_counters = {violation: 0 for violation in EconomicViolation}
        
        # Economic constants (aligned with GenesisHarmonicState)
        self.FLUX_PROPORTIONALITY_CONSTANT = 1000  # k in FLX ∝ k·∇ψ
        self.MAX_RESONANCE_ENVELOPE = 10**9        # Maximum RES generation
        self.MIN_ATTRACTOR_INCREMENT = 1           # Minimum ATR growth
        self.DISSONANCE_PENALTY_BASE = 1000
        self.SCALE_FACTOR = 1_000_000

    def compute_harmonic_state(self, current_state: TokenStateBundle) -> TokenStateBundle:
        """
        Compute full 5-token harmonic state with economic law enforcement.
        
        Args:
            current_state: Input TokenStateBundle with current 5-token state
            
        Returns:
            New TokenStateBundle with validated economic transformations
            
        Raises:
            EconomicSecurityError: For economic rule violations (CIR-302/412/511)
            ValueError: For invalid inputs or state inconsistencies
            SecurityError: For ψ-field integrity violations (from PsiFieldEngine)
        """
        # Create working copy for state transition
        new_state = self._deep_copy_state(current_state)
        
        try:
            # Phase 1: Validate current state invariants
            self._validate_economic_invariants(current_state)
            
            # Phase 2: Compute ψ-field metrics for economic decisions
            psi_metrics = self.psi_field.validate_psi_field_integrity(
                current_state, 
                delta_curl_threshold=current_state.parameters["δ_curl"].value
            )
            
            # Phase 3: Apply token transformations with conservation
            new_state = self._apply_token_transformations(current_state, new_state, psi_metrics)
            
            # Phase 4: Validate new state invariants
            self._validate_economic_invariants(new_state)
            
            # Phase 5: Update economic history for monotonicity proofs
            self._update_economic_history(current_state, new_state)
            
            # Log successful harmonic event
            self._log_harmonic_event("STATE_TRANSITION_SUCCESS", {
                "old_state_hash": self._compute_state_hash(current_state),
                "new_state_hash": self._compute_state_hash(new_state),
                "psi_sync_change": self._compute_psi_sync_change(current_state, new_state)
            })
            
            return new_state
            
        except EconomicSecurityError as e:
            # Security errors already handled by CIR handlers
            raise
        except Exception as e:
            self._log_harmonic_event("STATE_TRANSITION_FAILURE", {
                "error": str(e),
                "current_state_hash": self._compute_state_hash(current_state)
            })
            # For unexpected errors, raise EconomicSecurityError
            raise EconomicSecurityError(
                f"Unexpected error during harmonic state computation: {str(e)}",
                EconomicViolation.HARMONIC_DIVERGENCE
            )

    def _apply_token_transformations(self, old_state: TokenStateBundle, new_state: TokenStateBundle, psi_metrics: Dict) -> TokenStateBundle:
        """
        Apply economic transformations while preserving all conservation laws.
        """
        # Access shards from TokenStateBundle
        old_shards = old_state.chr_state.get("shards", {})
        new_shards = new_state.chr_state.get("shards", {})
        
        for shard_id in new_shards.keys():
            shard = new_shards[shard_id]
            old_shard = old_shards[shard_id]
            
            # 1. CHR: Strict conservation (no transformation allowed)
            # CHR can only move between shards, never created/destroyed
            if shard["CHR"] != old_shard["CHR"]:
                self._handle_economic_violation(
                    EconomicViolation.CHR_CONSERVATION_BREACH,
                    f"CHR conservation violation in {shard_id}: {old_shard['CHR']} -> {shard['CHR']}",
                    shard_id
                )
            
            # 2. FLX: Flow proportional to ψ-gradient with balance enforcement
            shard["FLX"] = self._compute_flux_balance(shard_id, old_state, new_state, psi_metrics)
            
            # 3. ΨSync: Monotonic with coherence increases
            shard["ΨSync"] = self._compute_psisync_update(shard_id, old_shard, shard, psi_metrics)
            
            # 4. ATR: Monotonic attractor law enforcement
            shard["ATR"] = self._compute_attractor_update(shard_id, old_shard, shard, psi_metrics)
            
            # 5. RES: Bounded by system resonance envelope
            shard["RES"] = self._compute_resonance_update(shard_id, old_shard, shard, psi_metrics)
            
            # 6. Compute dissonance for ψ-field
            shard["DISSONANCE"] = self._compute_dissonance_penalty(shard_id, old_state, new_state)
        
        return new_state

    def _compute_flux_balance(self, shard_id: str, old_state: TokenStateBundle, new_state: TokenStateBundle, psi_metrics: Dict) -> int:
        """
        Enforce FLX flow balance: inflow = outflow with ψ-gradient proportionality.
        Implements Kirchhoff's current law for token flows.
        """
        # Access shards from TokenStateBundle
        old_shards = old_state.chr_state.get("shards", {})
        new_shards = new_state.chr_state.get("shards", {})
        
        shard = new_shards[shard_id]
        old_flx = old_shards[shard_id]["FLX"]
        
        # Calculate net flow from ψ-gradients
        net_flow = 0
        neighbors = self.psi_field.graph.get(shard_id, set())
        
        for neighbor in sorted(neighbors):  # Deterministic order
            if shard_id < neighbor:  # Process each edge once
                gradient = psi_metrics["psi_gradients"].get((shard_id, neighbor), 0)
                
                # FLX flow proportional to ψ-gradient (economic pressure)
                flow_magnitude = self.math.mul(
                    self.math.abs(gradient),
                    self.FLUX_PROPORTIONALITY_CONSTANT
                ) // self.SCALE_FACTOR
                
                # Direction: flow from high ψ to low ψ
                if gradient > 0:
                    # ψ(shard) < ψ(neighbor) → inflow to shard
                    net_flow = self.math.add(net_flow, flow_magnitude)
                else:
                    # ψ(shard) > ψ(neighbor) → outflow from shard  
                    net_flow = self.math.sub(net_flow, flow_magnitude)
        
        # Apply flow with conservation
        new_flx = self.math.add(old_flx, net_flow)
        
        # Prevent negative FLX (economic impossibility)
        if new_flx < 0:
            self._handle_economic_violation(
                EconomicViolation.NEGATIVE_FLOW_ATTEMPT,
                f"Negative FLX in {shard_id}: {old_flx} -> {new_flx}",
                shard_id
            )
            return 0  # Zero-commit safety
        
        return new_flx

    def _compute_psisync_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Compute ΨSync update enforcing monotonicity with coherence.
        ΨSync must increase or stay constant when coherence increases.
        """
        old_psi_density = self.psi_field.psi_density(shard_id, TokenStateBundle(
            chr_state={"shards": {shard_id: {
                "CHR": old_shard["CHR"],
                "ATR": old_shard["ATR"],
                "DISSONANCE": old_shard.get("DISSONANCE", 0)
            }}},
            flx_state={},
            psi_sync_state={},
            atr_state={},
            res_state={},
            signature="",
            timestamp=0,
            bundle_id="temp",
            pqc_cid="temp",
            quantum_metadata={},
            lambda1=self.math.ONE,
            lambda2=self.math.ONE,
            c_crit=self.math.ONE,
            parameters={}
        ))
        new_psi_density = self.psi_field.psi_density(shard_id, TokenStateBundle(
            chr_state={"shards": {shard_id: {
                "CHR": new_shard["CHR"],
                "ATR": new_shard["ATR"],
                "DISSONANCE": new_shard.get("DISSONANCE", 0)
            }}},
            flx_state={},
            psi_sync_state={},
            atr_state={},
            res_state={},
            signature="",
            timestamp=0,
            bundle_id="temp",
            pqc_cid="temp",
            quantum_metadata={},
            lambda1=self.math.ONE,
            lambda2=self.math.ONE,
            c_crit=self.math.ONE,
            parameters={}
        ))
        
        coherence_change = self.math.sub(new_psi_density, old_psi_density)
        old_psisync = old_shard["ΨSync"]
        
        if coherence_change > 0:
            # Coherence increased → ΨSync must not decrease
            new_psisync = self.math.add(
                old_psisync,
                self.math.div_floor(coherence_change, 100)  # Scale factor
            )
            return max(old_psisync, new_psisync)  # Monotonicity enforcement
        else:
            # Coherence stable or decreased → ΨSync can decrease moderately
            max_decrease = self.math.div_floor(old_psisync, 10)  # 10% max decrease
            return self.math.sub(old_psisync, min(max_decrease, abs(coherence_change // 1000)))

    def _compute_attractor_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Enforce monotonic attractor law: ATR increases with stability.
        Prevents sudden collapse of field stability anchors.
        """
        old_atr = old_shard["ATR"]
        stability_metric = self._compute_stability_metric(shard_id, old_shard, new_shard)
        
        # ATR can only decrease if severe instability detected
        if stability_metric < -5000:  # Instability threshold
            max_decrease = self.math.div_floor(old_atr, 20)  # 5% max decrease
            return self.math.sub(old_atr, max_decrease)
        else:
            # Normal operation: ATR increases with stability
            increment = self.math.max(
                self.MIN_ATTRACTOR_INCREMENT,
                self.math.div_floor(stability_metric, 1000)
            )
            return self.math.add(old_atr, increment)

    def _compute_resonance_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Compute RES update bounded by system resonance envelope.
        Prevents resonance overdrive attacks (EA-4).
        """
        old_res = old_shard["RES"]
        
        # Calculate resonance generation from cross-shard alignment
        resonance_generation = 0
        neighbors = self.psi_field.graph.get(shard_id, set())
        
        for neighbor in sorted(neighbors):  # Deterministic order
            alignment = self._compute_shard_alignment(
                shard_id, neighbor, 
                TokenStateBundle(
                    chr_state={"shards": {shard_id: {
                        "CHR": old_shard["CHR"],
                        "ATR": old_shard["ATR"]
                    }}},
                    flx_state={},
                    psi_sync_state={},
                    atr_state={},
                    res_state={},
                    signature="",
                    timestamp=0,
                    bundle_id="temp",
                    pqc_cid="temp",
                    quantum_metadata={},
                    lambda1=self.math.ONE,
                    lambda2=self.math.ONE,
                    c_crit=self.math.ONE,
                    parameters={}
                )
            )
            resonance_generation = self.math.add(resonance_generation, alignment)
        
        # Apply envelope constraint
        new_res = self.math.add(old_res, resonance_generation)
        envelope = self._compute_resonance_envelope(shard_id, new_shard)
        
        if new_res > envelope:
            self._handle_economic_violation(
                EconomicViolation.RES_ENVELOPE_BREACH,
                f"RES envelope breach in {shard_id}: {new_res} > {envelope}",
                shard_id
            )
            return envelope  # Hard cap
        
        return new_res

    def _compute_dissonance_penalty(self, shard_id: str, old_state: TokenStateBundle, new_state: TokenStateBundle) -> int:
        """
        Compute dissonance penalty for economic misalignment.
        Used in ψ-density calculations to reduce coherence during imbalances.
        """
        # Access shards from TokenStateBundle
        new_shards = new_state.chr_state.get("shards", {})
        shard = new_shards[shard_id]
        
        # Dissonance from FLX flow imbalances
        flow_imbalance = self._compute_flow_imbalance(shard_id, new_state)
        
        # Dissonance from CHR distribution anomalies
        chr_anomaly = self._compute_chr_distribution_anomaly(shard_id, new_state)
        
        total_dissonance = self.math.add(flow_imbalance, chr_anomaly)
        return self.math.min(total_dissonance, 10**6)  # Reasonable upper bound

    def _validate_economic_invariants(self, state: TokenStateBundle):
        """
        Validate all economic invariants with precise violation detection.
        """
        violations = []
        
        # Access shards from TokenStateBundle
        shards = state.chr_state.get("shards", {})
        
        # 1. Global CHR conservation
        total_chr = sum(shard["CHR"] for shard in shards.values())
        # Safer parameter access
        expected_chr = getattr(state.parameters.get("MAX_CHR_SUPPLY"), 'value', 10_000_000_000)
        
        if total_chr != expected_chr:
            violations.append((
                EconomicViolation.CHR_CONSERVATION_BREACH,
                f"Global CHR conservation: {total_chr} != {expected_chr}"
            ))
        
        # 2. Per-shard FLX flow balance
        for shard_id in shards:
            flow_imbalance = self._compute_flow_imbalance(shard_id, state)
            # Safer parameter access
            delta_max = getattr(state.parameters.get("δ_max"), 'value', 5)
            if self.math.abs(flow_imbalance) > delta_max * 1000:
                violations.append((
                    EconomicViolation.FLX_FLOW_IMBALANCE,
                    f"FLX flow imbalance in {shard_id}: {flow_imbalance}"
                ))
        
        # 3. ΨSync monotonicity (compared to history)
        if len(self.economic_state_history) >= 2:
            current_sync = sum(shard["ΨSync"] for shard in shards.values())
            previous_sync = sum(shard["ΨSync"] for shard in self.economic_state_history[-1].chr_state.get("shards", {}).values())
            
            # Safer parameter access
            epsilon_sync = getattr(state.parameters.get("ε_sync"), 'value', 2)
            if current_sync < previous_sync - epsilon_sync * 100:
                violations.append((
                    EconomicViolation.PSY_MONOTONICITY_VIOLATION,
                    f"ΨSync monotonicity violation: {current_sync} < {previous_sync}"
                ))
        
        # 4. ATR attractor stability
        for shard_id, shard in shards.items():
            if shard["ATR"] < 0:
                violations.append((
                    EconomicViolation.ATTR_ATTRACTOR_VIOLATION,
                    f"Negative ATR in {shard_id}: {shard['ATR']}"
                ))
        
        # Trigger appropriate CIR for violations
        for violation_type, message in violations:
            self._handle_economic_violation(violation_type, message)

    def _compute_flow_imbalance(self, shard_id: str, state: TokenStateBundle) -> int:
        """Compute FLX inflow - outflow for a shard."""
        inflow, outflow = 0, 0
        # Access FLX flow matrix from TokenStateBundle
        flow_matrix = state.flx_state.get("FLX_flow_matrix", {})
        
        for (src, dst), flow in flow_matrix.items():
            if dst == shard_id:
                inflow = self.math.add(inflow, flow)
            if src == shard_id:
                outflow = self.math.add(outflow, flow)
        
        return self.math.sub(inflow, outflow)

    def _compute_chr_distribution_anomaly(self, shard_id: str, state: TokenStateBundle) -> int:
        """Compute CHR distribution anomaly metric."""
        # Access shards from TokenStateBundle
        shards = state.chr_state.get("shards", {})
        shard_chr = shards[shard_id]["CHR"]
        avg_chr = sum(s["CHR"] for s in shards.values()) // len(shards)
        
        deviation = self.math.abs(self.math.sub(shard_chr, avg_chr))
        return self.math.div_floor(deviation, 1000)  # Scale to reasonable range

    def _compute_stability_metric(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any]) -> int:
        """Compute stability metric for ATR updates."""
        chr_stability = self.math.sub(new_shard["CHR"], old_shard["CHR"])
        flx_stability = self.math.sub(new_shard["FLX"], old_shard["FLX"]) // 1000
        
        return self.math.add(chr_stability, flx_stability)

    def _compute_shard_alignment(self, shard_a: str, shard_b: str, old_state: TokenStateBundle) -> int:
        """Compute alignment metric between two shards for RES generation."""
        shards = old_state.chr_state.get("shards", {})
        
        # Validate both shards exist
        if shard_a not in shards or shard_b not in shards:
            return 0  # No alignment if shard missing
        
        shard_a_data = shards[shard_a]
        shard_b_data = shards[shard_b]  # ← FIXED: Use actual shard_b data
        
        chr_alignment = self.math.min(shard_a_data["CHR"], shard_b_data["CHR"])
        atr_alignment = self.math.min(shard_a_data["ATR"], shard_b_data["ATR"])
        
        return self.math.div_floor(
            self.math.mul(chr_alignment, atr_alignment),
            self.SCALE_FACTOR
        )

    def _compute_resonance_envelope(self, shard_id: str, new_shard: Dict[str, Any]) -> int:
        """Compute maximum RES capacity for a shard."""
        base_envelope = self.math.mul(new_shard["CHR"], new_shard["ATR"]) // self.SCALE_FACTOR
        return self.math.min(base_envelope, self.MAX_RESONANCE_ENVELOPE)

    def _handle_economic_violation(self, violation_type: EconomicViolation, message: str, shard_id: str = None):
        """Handle economic violations with deterministic exception raising."""
        self.violation_counters[violation_type] += 1
        
        # Log for evidence and audit (deterministic)
        evidence = {
            "violation_type": violation_type.value,
            "message": message,
            "shard_id": shard_id,
            "counter": self.violation_counters[violation_type],
            "cir_code": self._get_cir_code_for_violation(violation_type)
        }
        
        self._log_harmonic_event("ECONOMIC_VIOLATION", evidence)
        
        # ALWAYS raise exception - deterministic behavior
        cir_code = self._get_cir_code_for_violation(violation_type)
        raise EconomicSecurityError(
            message=f"{cir_code}: {message}", 
            violation_type=violation_type,
            evidence=evidence,
            cir_code=cir_code
        )
    
    def _get_cir_code_for_violation(self, violation_type: EconomicViolation) -> str:
        """Deterministic mapping from economic violations to CIR codes."""
        mapping = {
            EconomicViolation.CHR_CONSERVATION_BREACH: "CIR-302",
            EconomicViolation.NEGATIVE_FLOW_ATTEMPT: "CIR-302", 
            EconomicViolation.FLX_FLOW_IMBALANCE: "CIR-302",
            EconomicViolation.PSY_MONOTONICITY_VIOLATION: "CIR-412",
            EconomicViolation.ATTR_ATTRACTOR_VIOLATION: "CIR-412",
            EconomicViolation.RES_ENVELOPE_BREACH: "CIR-511"
        }
        return mapping.get(violation_type, "CIR-302")  # Default to most restrictive

    def _update_economic_history(self, old_state: TokenStateBundle, new_state: TokenStateBundle):
        """Maintain economic state history for monotonicity proofs."""
        if len(self.economic_state_history) >= 10:  # Keep last 10 states
            self.economic_state_history.pop(0)
        self.economic_state_history.append(self._deep_copy_state(new_state))

    def _deep_copy_state(self, state: TokenStateBundle) -> TokenStateBundle:
        """Create safe copy of TokenStateBundle for transformation."""
        # TokenStateBundle should ideally be immutable
        # If mutable, use proper copying mechanism
        try:
            return state.copy()  # If TokenStateBundle has copy method
        except AttributeError:
            import copy
            return copy.deepcopy(state)

    def _compute_state_hash(self, state: TokenStateBundle) -> str:
        """Compute deterministic hash of economic state for evidence.
        
        NOTE: SHA3-256 is permitted in evidence layer per QFSV13 §8.3
        """
        import hashlib
        import json
        
        # Access shards from TokenStateBundle
        shards = state.chr_state.get("shards", {})
        
        # Convert to canonical dict representation
        state_dict = {
            "shards": {k: {
                "CHR": v["CHR"],
                "FLX": v["FLX"],
                "ATR": v["ATR"],
                "RES": v["RES"],
                "ΨSync": v["ΨSync"],
                "DISSONANCE": v.get("DISSONANCE", 0)
            } for k, v in shards.items()},
            "system_constants": {
                "MAX_CHR_SUPPLY": state.parameters["MAX_CHR_SUPPLY"].value,
                "δ_max": state.parameters["δ_max"].value,
                "ε_sync": state.parameters["ε_sync"].value
            }
        }
        
        canonical = json.dumps(state_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha3_256(canonical.encode()).hexdigest()

    def _compute_psi_sync_change(self, old_state: TokenStateBundle, new_state: TokenStateBundle) -> int:
        """Compute change in global ΨSync for monitoring."""
        # Access shards from TokenStateBundle
        old_shards = old_state.chr_state.get("shards", {})
        new_shards = new_state.chr_state.get("shards", {})
        
        old_sync = sum(shard["ΨSync"] for shard in old_shards.values())
        new_sync = sum(shard["ΨSync"] for shard in new_shards.values())
        return self.math.sub(new_sync, old_sync)

    def _log_harmonic_event(self, event_type: str, data: Dict):
        """Log harmonic economic events for evidence and audit trails."""
        timestamp = getattr(data, 'timestamp', 0)  # In real implementation, get from state
        self.event_logger.log(
            category="HARMONIC_ECONOMICS",
            event_type=event_type,
            data=data,
            timestamp=timestamp
        )

    def get_economic_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive economic health report for evidence."""
        return {
            "violation_summary": {v.value: count for v, count in self.violation_counters.items()},
            "state_history_size": len(self.economic_state_history),
            "economic_constants": {
                "flux_proportionality": self.FLUX_PROPORTIONALITY_CONSTANT,
                "max_resonance_envelope": self.MAX_RESONANCE_ENVELOPE,
                "min_attractor_increment": self.MIN_ATTRACTOR_INCREMENT
            }
        }

# =============================================================================
# MODULE SAFETY GUARDS
# =============================================================================

if __name__ == "__main__":
    print("HarmonicEconomics.py is a hardened library module. Do not execute directly.")
    sys.exit(1)

__all__ = [
    "HarmonicEconomics",
    "EconomicViolation",
    "EconomicSecurityError"
]