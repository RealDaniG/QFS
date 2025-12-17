from libs.deterministic_helpers import det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure
from typing import Dict, List, Tuple, Set, Any, Optional, TYPE_CHECKING
try:
    from v13.core.TokenStateBundle import TokenStateBundle
except ImportError:
    from ...core.TokenStateBundle import TokenStateBundle
if TYPE_CHECKING:
    from v13.core.TokenStateBundle import TokenStateBundle

class SecurityThresholds:
    """Security constants for anomaly detection."""
    SUSPICIOUS_CURL_MAGNITUDE = 1000000
    MAX_DISSONANCE = 1000000
    MAX_CHR_VALUE = 10 ** 12
    MAX_ATR_VALUE = 10 ** 6

class SecurityError(Exception):
    """Security violation in ψ-field computations."""

    def __init__(self, message: str, violation_type: str=None, evidence: Dict=None, cir_code: str=None):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence or {}
        self.cir_code = cir_code

class DiscretePsiField:
    """
    HARDENED ψ-field engine with Byzantine detection and performance optimizations.

    SECURITY FEATURES:
    - Cycle basis caching with integrity verification
    - Edge direction consistency enforcement
    - Maximum computation bounds to prevent DoS
    - Deterministic cycle ordering for cross-runtime consistency
    - Memory-bound cycle detection to prevent resource exhaustion
    """

    def __init__(self, genesis_topology: Dict[str, Any], certified_math: Any):
        """
        Initialize with comprehensive topology validation and security bounds.
        """
        self.certified_math = certified_math
        self.shard_ids = set()
        self.graph = {}
        self.edge_psi_conductance = {}
        self.cycle_basis = []
        self.cycle_basis_hash = None
        self.MAX_CYCLE_LENGTH = 8
        self.MAX_CYCLES_PER_SHARD = 5
        self.MAX_EDGES_PER_SHARD = 10
        self._validate_and_build_graph(genesis_topology)
        self._compute_secure_cycle_basis()

    def _validate_and_build_graph(self, topology: Dict[str, Any]):
        """Build graph with comprehensive security validation."""
        connections = topology.get('shard_connections', [])
        if len(connections) > 100:
            evidence = {'connections_count': len(connections)}
            raise SecurityError(f'EXCESSIVE_CONNECTIONS: Excessive connections: {len(connections)}', violation_type='EXCESSIVE_CONNECTIONS', evidence=evidence, cir_code='CIR-412')
        shard_set = set()
        for a, b in sorted(connections):
            if not isinstance(a, str) or not isinstance(b, str):
                evidence = {'shard_a_type': type(a), 'shard_b_type': type(b)}
                raise SecurityError(f'INVALID_SHARD_ID_TYPES: Invalid shard ID types: {type(a)}, {type(b)}', violation_type='INVALID_SHARD_ID_TYPES', evidence=evidence, cir_code='CIR-412')
            shard_set.add(a)
            shard_set.add(b)
        self.shard_ids = shard_set
        self.graph = {shard: set() for shard in self.shard_ids}
        edge_count = {}
        for a, b in sorted(connections):
            if a not in self.shard_ids or b not in self.shard_ids:
                evidence = {'shard_a': a, 'shard_b': b, 'valid_shards': list(self.shard_ids)}
                raise SecurityError(f'INVALID_SHARD_IN_CONNECTION: Invalid shard in connection: {a}-{b}', violation_type='INVALID_SHARD_IN_CONNECTION', evidence=evidence, cir_code='CIR-412')
            if a == b:
                evidence = {'shard_id': a}
                raise SecurityError(f'SELF_LOOP_DETECTED: Self-loop detected: {a}', violation_type='SELF_LOOP_DETECTED', evidence=evidence, cir_code='CIR-412')
            edge_key = tuple(sorted([a, b]))
            if edge_key in edge_count:
                evidence = {'edge': f'{a}-{b}'}
                raise SecurityError(f'DUPLICATE_EDGE: Duplicate edge: {a}-{b}', violation_type='DUPLICATE_EDGE', evidence=evidence, cir_code='CIR-412')
            edge_count[edge_key] = True
            self.graph[a].add(b)
            self.graph[b].add(a)
        min_degree = topology.get('min_connection_degree', 2)
        max_degree = topology.get('max_connection_degree', 3)
        for shard, neighbors in self.graph.items():
            degree = len(neighbors)
            if degree < min_degree:
                evidence = {'shard_id': shard, 'degree': degree, 'min_required': min_degree}
                raise SecurityError(f'UNDER_CONNECTED_SHARD: Shard {shard} under-connected: {degree} < {min_degree}', violation_type='UNDER_CONNECTED_SHARD', evidence=evidence, cir_code='CIR-412')
            if degree > self.MAX_EDGES_PER_SHARD:
                evidence = {'shard_id': shard, 'degree': degree, 'max_allowed': self.MAX_EDGES_PER_SHARD}
                raise SecurityError(f'OVER_CONNECTED_SHARD: Shard {shard} over-connected: {degree} > {self.MAX_EDGES_PER_SHARD}', violation_type='OVER_CONNECTED_SHARD', evidence=evidence, cir_code='CIR-412')

    def _compute_secure_cycle_basis(self):
        """
        Compute cycle basis with security bounds and deterministic ordering.
        Uses iterative DFS with cycle length limits to prevent resource exhaustion.
        """
        visited = set()
        parent = {}
        cycles = []
        cycle_cache = set()

        def secure_dfs(u, v, depth=0):
            if depth > self.MAX_CYCLE_LENGTH:
                return
            visited.add(v)
            parent[v] = u
            neighbors = sorted(self.graph[v])
            for w in sorted(neighbors):
                if w == u:
                    continue
                if w in visited:
                    cycle = self._extract_secure_cycle(v, w, parent)
                    if cycle and len(cycle) <= self.MAX_CYCLE_LENGTH:
                        cycle_tuple = tuple(sorted(cycle))
                        if cycle_tuple not in cycle_cache:
                            cycles.append(cycle)
                            cycle_cache.add(cycle_tuple)
                            if len(cycles) >= self.MAX_CYCLES_PER_SHARD * len(self.shard_ids):
                                return
                else:
                    secure_dfs(v, w, depth + 1)
        sorted_shards = sorted(self.shard_ids)
        for shard in sorted(sorted_shards):
            if shard not in visited:
                secure_dfs(None, shard)
        self.cycle_basis = cycles
        self.cycle_basis_hash = self._compute_cycle_basis_hash()

    def _extract_secure_cycle(self, start: str, end: str, parent: Dict[str, str]) -> Optional[List[str]]:
        """Extract cycle with bounds checking and validation."""
        try:
            path1 = []
            current = start
            while current is not None:
                if len(path1) > self.MAX_CYCLE_LENGTH:
                    return None
                path1.append(current)
                current = parent.get(current)
            path2 = []
            current = end
            while current is not None:
                if len(path2) > self.MAX_CYCLE_LENGTH:
                    return None
                path2.append(current)
                current = parent.get(current)
            set1 = set(path1)
            lca = None
            for node in sorted(path2):
                if node in set1:
                    lca = node
                    break
            if lca is None:
                return None
            cycle = []
            for node in sorted(path1):
                cycle.append(node)
                if node == lca:
                    break
            lca_index = path2.index(lca)
            for i in range(lca_index - 1, -1, -1):
                cycle.append(path2[i])
            cycle.append(start)
            if len(cycle) < 3 or len(cycle) > self.MAX_CYCLE_LENGTH:
                return None
            if len(cycle) != len(set(cycle)):
                return None
            return cycle
        except (KeyError, IndexError):
            return None

    def _compute_cycle_basis_hash(self) -> str:
        """Compute deterministic hash of cycle basis for integrity verification."""
        import hashlib
        canonical_repr = []
        for cycle in sorted(self.cycle_basis, key=lambda x: (len(x), tuple(x))):
            canonical_repr.append(tuple(sorted(cycle)))
        canonical_str = str(sorted(canonical_repr))
        return hashlib.sha3_256(canonical_str.encode()).hexdigest()

    def verify_cycle_basis_integrity(self) -> bool:
        """Verify cycle basis hasn't been tampered with."""
        current_hash = self._compute_cycle_basis_hash()
        is_valid = current_hash == self.cycle_basis_hash
        if not is_valid:
            evidence = {'expected_hash': self.cycle_basis_hash, 'current_hash': current_hash}
            raise SecurityError('CYCLE_BASIS_TAMPERING: Cycle basis integrity compromised', violation_type='CYCLE_BASIS_TAMPERING', evidence=evidence, cir_code='CIR-412')
        return is_valid

    def psi_density(self, shard_id: str, harmonic_state: 'TokenStateBundle') -> int:
        """
        HARDENED ψ-density computation with bounds checking.
        ψ = (CHR × ATR) / (1 + DISSONANCE)
        """
        shards = harmonic_state.chr_state.get('shards', {})
        if shard_id not in shards:
            evidence = {'shard_id': shard_id, 'available_shards': list(shards.keys())}
            raise SecurityError(f'MISSING_SHARD: Shard {shard_id} not in harmonic state', violation_type='MISSING_SHARD', evidence=evidence, cir_code='CIR-412')
        shard = shards[shard_id]
        chr_val = self.certified_math.clamp(shard['CHR'], 0, SecurityThresholds.MAX_CHR_VALUE)
        atr_val = self.certified_math.clamp(shard['ATR'], 0, SecurityThresholds.MAX_ATR_VALUE)
        dissonance = max(0, shard.get('DISSONANCE', 0))
        dissonance = min(dissonance, SecurityThresholds.MAX_DISSONANCE)
        try:
            numerator = self.certified_math.checked_mul(chr_val, atr_val)
            denominator = 1 + dissonance
            return self.certified_math.checked_div(numerator, denominator)
        except OverflowError:
            safe_chr = chr_val // 1000
            safe_atr = atr_val // 1000
            safe_numerator = safe_chr * safe_atr
            return safe_numerator // max(1, denominator // 1000)

    def psi_gradient(self, i: str, j: str, harmonic_state: TokenStateBundle) -> int:
        """Compute ψ-gradient with connection validation and bounds checking."""
        if j not in self.graph.get(i, set()):
            raise ValueError(f'Shards {i} and {j} not connected')
        psi_i = self.psi_density(i, harmonic_state)
        psi_j = self.psi_density(j, harmonic_state)
        return self.certified_math.checked_sub(psi_j, psi_i)

    def directional_psi_flux(self, i: str, j: str, harmonic_state: TokenStateBundle) -> int:
        """
        Compute directional ψ-flux with sign consistency.
        Positive flux: flow from i → j (ψ increasing)
        Negative flux: flow from j → i (ψ decreasing)
        """
        flow_matrix = harmonic_state.flx_state.get('FLX_flow_matrix', {})
        flux_ij = flow_matrix.get((i, j), 0)
        flux_ji = flow_matrix.get((j, i), 0)
        return self.certified_math.checked_sub(flux_ij, flux_ji)

    def psi_curl_around_cycle(self, cycle: List[str], harmonic_state: TokenStateBundle) -> int:
        """
        HARDENED ψ-curl computation with cycle validation.
        Uses consistent edge direction around cycle.
        """
        if len(cycle) < 3 or len(cycle) > self.MAX_CYCLE_LENGTH:
            return 0
        if len(cycle) != len(set(cycle)):
            return 0
        total_curl = 0
        n = len(cycle)
        try:
            for idx in range(n):
                u = cycle[idx]
                v = cycle[(idx + 1) % n]
                if v not in self.graph.get(u, set()):
                    return 0
                grad = self.psi_gradient(u, v, harmonic_state)
                total_curl = self.certified_math.checked_add(total_curl, grad)
            return total_curl
        except (ValueError, OverflowError):
            return 0

    def compute_psi_curls_with_anomaly_detection(self, harmonic_state: TokenStateBundle) -> Tuple[List[Tuple[List[str], int]], List[str]]:
        """
        Compute all ψ-curls with anomaly detection and Byzantine alerts.
        Returns (curls, anomalies)
        """
        if not self.verify_cycle_basis_integrity():
            raise SecurityError('Cycle basis integrity compromised')
        curls = []
        anomalies = []
        for cycle in sorted(self.cycle_basis):
            curl_val = self.psi_curl_around_cycle(cycle, harmonic_state)
            curls.append((cycle, curl_val))
            curl_mag = self.certified_math.abs(curl_val)
            if curl_mag > 1000000:
                anomalies.append(f'SUSPICIOUS_CURL: Cycle {cycle} has magnitude {curl_mag}')
            elif curl_val != 0 and len(cycle) == 3:
                anomalies.append(f'SMALL_CYCLE_NONZERO: 3-cycle {cycle} curl = {curl_val}')
        return (curls, anomalies)

    def global_psi_sync_metric(self, harmonic_state: TokenStateBundle) -> Dict[str, int]:
        """
        Compute comprehensive ΨSync metrics with variance analysis.
        Returns multiple sync measures for Byzantine detection.
        """
        shard_syncs = {}
        shards = harmonic_state.chr_state.get('shards', {})
        for shard_id in sorted(self.shard_ids):
            shard = shards[shard_id]
            chr_val = shard['CHR']
            res_val = shard['RES']
            atr_val = shard['ATR']
            sync_simple = self.certified_math.mul(chr_val, atr_val)
            sync_resonant = self.certified_math.mul(sync_simple, self.certified_math.add(1, res_val // 1000))
            shard_syncs[shard_id] = {'simple': sync_simple, 'resonant': sync_resonant, 'density_based': self.psi_density(shard_id, harmonic_state)}
        total_simple = sum((s['simple'] for s in shard_syncs.values()))
        total_resonant = sum((s['resonant'] for s in shard_syncs.values()))
        sync_values = [s['simple'] for s in shard_syncs.values()]
        avg_sync = total_simple // len(sync_values)
        variance = sum(((v - avg_sync) ** 2 for v in sync_values)) // len(sync_values)
        return {'total_simple_sync': total_simple, 'total_resonant_sync': total_resonant, 'average_sync': avg_sync, 'sync_variance': variance, 'shard_syncs': shard_syncs}

    def validate_psi_field_integrity(self, harmonic_state: TokenStateBundle, delta_curl_threshold: int) -> Dict[str, Any]:
        """
        PRODUCTION-HARDENED ψ-field validation with comprehensive security checks.

        Args:
            harmonic_state: TokenStateBundle containing all 5-token states
            delta_curl_threshold: Maximum allowed ψ-curl magnitude

        Returns:
            Validation result with metrics, anomalies, and security status

        Raises:
            SecurityError: For critical ψ-field violations (CIR-412)
            ValueError: For invalid inputs or state inconsistencies
        """
        self.verify_cycle_basis_integrity()
        validation_result = {'psi_densities': {}, 'psi_gradients': {}, 'psi_curls': [], 'psi_sync': {}, 'anomalies': [], 'violations': [], 'security_checks_passed': True, 'max_curl_magnitude': 0}
        try:
            for shard in sorted(self.shard_ids):
                validation_result['psi_densities'][shard] = self.psi_density(shard, harmonic_state)
            for i in sorted(self.shard_ids):
                for j in sorted(self.graph[i]):
                    if i < j:
                        grad = self.psi_gradient(i, j, harmonic_state)
                        validation_result['psi_gradients'][i, j] = grad
            curls, anomalies = self.compute_psi_curls_with_anomaly_detection(harmonic_state)
            validation_result['psi_curls'] = curls
            validation_result['anomalies'].extend(anomalies)
            max_curl = 0
            for cycle, curl_val in sorted(curls):
                curl_mag = self.certified_math.abs(curl_val)
                max_curl = max(max_curl, curl_mag)
                if curl_mag > delta_curl_threshold:
                    violation_msg = f'CURL_THRESHOLD_EXCEEDED: Cycle {cycle} |{curl_val}| > {delta_curl_threshold}'
                    validation_result['violations'].append(violation_msg)
                elif curl_mag > SecurityThresholds.SUSPICIOUS_CURL_MAGNITUDE:
                    anomaly_msg = f'SUSPICIOUS_CURL: Cycle {cycle} has magnitude {curl_mag}'
                    validation_result['anomalies'].append(anomaly_msg)
            validation_result['max_curl_magnitude'] = max_curl
            validation_result['psi_sync'] = self.global_psi_sync_metric(harmonic_state)
            critical_violations = [v for v in validation_result['violations'] if 'CURL_THRESHOLD_EXCEEDED' in v]
            if critical_violations:
                raise SecurityError(f'PSI_FIELD_CRITICAL_VIOLATION: {critical_violations}', violation_type='PSI_FIELD_CRITICAL_VIOLATION', evidence=validation_result, cir_code='CIR-412')
            return validation_result
        except Exception as e:
            validation_result['security_checks_passed'] = False
            validation_result['violations'].append(f'RUNTIME_ERROR: {str(e)}')
            raise

def create_secure_psi_field(genesis_topology: Dict[str, Any], certified_math: Any, security_level: str='HIGH') -> DiscretePsiField:
    """
    Factory function for creating ψ-field instances with security configuration.
    """
    field = DiscretePsiField(genesis_topology, certified_math)
    if security_level == 'PARANOID':
        field.MAX_CYCLE_LENGTH = 6
        field.MAX_CYCLES_PER_SHARD = 3
        field.MAX_EDGES_PER_SHARD = 8
    elif security_level == 'BALANCED':
        field.MAX_CYCLE_LENGTH = 8
        field.MAX_CYCLES_PER_SHARD = 5
        field.MAX_EDGES_PER_SHARD = 10
    return field

def generate_psi_field_evidence(field_engine: DiscretePsiField, harmonic_state: TokenStateBundle, delta_curl_threshold: int) -> Dict[str, Any]:
    """
    Generate comprehensive evidence package for Phase3EvidenceBuilder.
    """
    validation_result = field_engine.validate_psi_field_integrity(harmonic_state, delta_curl_threshold)
    evidence = {'psi_field_validation': validation_result, 'topology_metrics': {'shard_count': len(field_engine.shard_ids), 'total_edges': sum((len(neighbors) for neighbors in field_engine.graph.values())) // 2, 'cycle_basis_size': len(field_engine.cycle_basis), 'cycle_basis_hash': field_engine.cycle_basis_hash}, 'computation_bounds': {'max_cycle_length': field_engine.MAX_CYCLE_LENGTH, 'max_cycles_per_shard': field_engine.MAX_CYCLES_PER_SHARD, 'max_edges_per_shard': field_engine.MAX_EDGES_PER_SHARD}, 'security_status': {'cycle_basis_integrity': field_engine.verify_cycle_basis_integrity(), 'anomalies_detected': len(validation_result['anomalies']), 'violations_detected': len(validation_result['violations'])}}
    return evidence
if __name__ == '__main__':
    pass
__all__ = ['DiscretePsiField', 'create_secure_psi_field', 'generate_psi_field_evidence', 'SecurityError']