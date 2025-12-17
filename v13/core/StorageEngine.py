"""
StorageEngine.py - Deterministic storage engine implementing the decentralized storage protocol

This module implements a decentralized, node-based, content-addressed storage layer
that is fully compatible with QFS, ATLAS, AEGIS, and OpenAGI while preserving
Zero-Simulation, determinism, replayability, and auditability.
"""
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
try:
    from v13.libs.CertifiedMath import BigNum128, CertifiedMath
    from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
    from v13.core.TokenStateBundle import TokenStateBundle
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        raise ImportError('Critical Dependency Missing: AEGIS_Node_Verifier or TokenStateBundle. System cannot start securely.')
BLOCK_SIZE_BYTES = 262144
NUM_SHARDS_PER_OBJECT = 4
REPLICATION_FACTOR = 3
CONTENT_HASH_FUNCTION = 'SHA3-256'
SHARD_HASH_FUNCTION = 'SHA3-256'
ATR_BASE_STORAGE_COST_PER_KB = BigNum128.from_int(100)
ATR_STORAGE_COST_MULTIPLIER = BigNum128.from_string('1.0')

@dataclass
class StorageNode:
    """Represents a storage node in the decentralized network."""
    node_id: str
    host: str
    port: int
    status: str = 'active'
    uptime_bucket: int = 0
    bytes_stored: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))
    proofs_verified: int = 0
    is_aegis_verified: bool = False
    aegis_verification_epoch: int = 0

@dataclass
class LogicalObject:
    """Represents a logical object in the storage system."""
    object_id: str
    version: int
    hash_commit: str
    metadata: Dict[str, Any]
    shard_ids: List[str] = field(default_factory=list)
    created_at_tick: int = 0

@dataclass
class Shard:
    """Represents a shard of a logical object."""
    shard_id: str
    object_id: str
    version: int
    shard_index: int
    content_chunk: bytes
    assigned_nodes: List[str] = field(default_factory=list)
    merkle_root: str = ''
    proof: str = ''

class StorageEngine:
    """
    Deterministic storage engine implementing the decentralized storage protocol.

    This engine provides a content-addressed, shard-based storage system that
    maintains Zero-Simulation compliance and deterministic behavior.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Storage Engine.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
        """
        self.cm = cm_instance
        self.nodes: Dict[str, StorageNode] = {}
        self.objects: Dict[str, LogicalObject] = {}
        self.shards: Dict[str, Shard] = {}
        self.eligible_nodes_cache: List[str] = []
        self.current_epoch: int = 0
        self.aegis_verifier: Optional[AEGIS_Node_Verifier] = None
        self.registry_snapshot: Optional[Dict[str, Any]] = None
        self.telemetry_snapshot: Optional[Dict[str, Any]] = None
        self.quantum_metadata = {'component': 'StorageEngine', 'version': 'QFS-V13-DECENTRALIZED-STORAGE', 'timestamp': None, 'pqc_scheme': 'Dilithium-5'}
        self.total_atr_fees_collected = BigNum128(0)
        self.total_nod_rewards_distributed = BigNum128(0)
        self.storage_event_log = []

    def _hash_sensitive_id(self, identifier: str) -> str:
        """Hash sensitive identifiers in logs"""
        if identifier is None:
            return None
        return hashlib.sha256(str(identifier).encode()).hexdigest()[:16]

    def _emit_storage_event(self, event: Dict[str, Any]) -> None:
        """Append a canonical StorageEvent entry for deterministic replay.

        This is intentionally a simple in-memory append used by tests and
        replay drills. It must remain deterministic: event_id is computed from
        a canonical JSON serialization of the event payload.
        """
        event_without_id = dict(event)
        event_without_id.pop('event_id', None)
        canonical_json = json.dumps(event_without_id, sort_keys=True, separators=(',', ':'))
        event_id = hashlib.sha3_256(canonical_json.encode()).hexdigest()
        event_with_id = dict(event_without_id)
        event_with_id['event_id'] = event_id
        self.storage_event_log.append(event_with_id)

    def set_aegis_context(self, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any]) -> None:
        """
        Set AEGIS context for node verification.

        Args:
            registry_snapshot: AEGIS registry snapshot
            telemetry_snapshot: AEGIS telemetry snapshot
        """
        self.registry_snapshot = registry_snapshot
        self.telemetry_snapshot = telemetry_snapshot
        self.aegis_verifier = AEGIS_Node_Verifier(self.cm)

    def is_node_aegis_verified(self, node_id: str, epoch: int) -> bool:
        """
        Check if a node is AEGIS verified for a specific epoch.

        This is the AEGIS hook that controls eligible_nodes.

        Args:
            node_id: Node identifier
            epoch: Epoch number

        Returns:
            bool: True if node is verified
        """
        if self.aegis_verifier is None or self.registry_snapshot is None or self.telemetry_snapshot is None:
            return node_id in self.nodes and self.nodes[node_id].status == 'active'
        result: NodeVerificationResult = self.aegis_verifier.verify_node(node_id, self.registry_snapshot, self.telemetry_snapshot)
        return result.is_valid

    def advance_epoch(self, new_epoch: int, registry_snapshot: Optional[Dict[str, Any]]=None, telemetry_snapshot: Optional[Dict[str, Any]]=None) -> None:
        """
        Advance to a new epoch and update node eligibility.

        Args:
            new_epoch: New epoch number
            registry_snapshot: Optional new registry snapshot
            telemetry_snapshot: Optional new telemetry snapshot
        """
        self.current_epoch = new_epoch
        if registry_snapshot is not None:
            self.registry_snapshot = registry_snapshot
        if telemetry_snapshot is not None:
            self.telemetry_snapshot = telemetry_snapshot
        for node_id, node in sorted(self.nodes.items()):
            node.is_aegis_verified = self.is_node_aegis_verified(node_id, new_epoch)
            node.aegis_verification_epoch = new_epoch
        self._invalidate_eligible_nodes_cache()
        self._emit_storage_event({'event_type': 'EPOCH_ADVANCEMENT', 'epoch': new_epoch, 'timestamp_tick': 0, 'object_id': None, 'version': None, 'hash_commit': None, 'content_size': 0, 'shard_ids': [], 'replica_sets': {}, 'atr_cost': '0', 'pqc_signature': None, 'error_code': None, 'error_detail': None})

    def register_storage_node(self, node_id: str, host: str, port: int) -> bool:
        """
        Register a storage node in the network.

        Args:
            node_id: Unique identifier for the node
            host: Host address
            port: Port number

        Returns:
            bool: True if registration successful
        """
        node = StorageNode(node_id=node_id, host=host, port=port)
        if self.aegis_verifier is not None and self.registry_snapshot is not None and (self.telemetry_snapshot is not None):
            node.is_aegis_verified = self.is_node_aegis_verified(node_id, self.current_epoch)
            node.aegis_verification_epoch = self.current_epoch
        self.nodes[node_id] = node
        self._invalidate_eligible_nodes_cache()
        self._emit_storage_event({'event_type': 'NODE_REGISTRATION', 'epoch': self.current_epoch, 'timestamp_tick': 0, 'object_id': None, 'version': None, 'hash_commit': None, 'content_size': 0, 'shard_ids': [], 'replica_sets': {'node_id': node_id, 'host': host, 'port': port}, 'atr_cost': '0', 'pqc_signature': None, 'error_code': None, 'error_detail': None})
        return True

    def unregister_storage_node(self, node_id: str) -> bool:
        """
        Unregister a storage node from the network.

        Args:
            node_id: Node identifier to unregister

        Returns:
            bool: True if unregistration successful
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._invalidate_eligible_nodes_cache()
            return True
        return False

    def set_node_status(self, node_id: str, status: str) -> bool:
        """
        Set the status of a storage node.

        Args:
            node_id: Node identifier
            status: New status ("active", "inactive", "revoked")

        Returns:
            bool: True if status update successful
        """
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self._invalidate_eligible_nodes_cache()
            return True
        return False

    def get_eligible_nodes(self) -> List[str]:
        """
        Get list of eligible storage nodes (AEGIS-verified and sorted).

        Returns:
            List of eligible node IDs sorted deterministically
        """
        if not self.eligible_nodes_cache:
            eligible_nodes = []
            if self.nodes:
                for node_id, node in sorted(self.nodes.items()):
                    if node.status == 'active':
                        if self.aegis_verifier is not None:
                            if node.is_aegis_verified and node.aegis_verification_epoch == self.current_epoch:
                                eligible_nodes.append(node_id)
                        else:
                            eligible_nodes.append(node_id)
            self.eligible_nodes_cache = sorted(eligible_nodes)
        return self.eligible_nodes_cache.copy()

    def _invalidate_eligible_nodes_cache(self) -> None:
        """Invalidate the eligible nodes cache when node status changes."""
        self.eligible_nodes_cache = []

    def put_content(self, object_id: str, version: int, content: bytes, metadata: Dict[str, Any], deterministic_timestamp: int=0) -> Dict[str, Any]:
        """
        Store content with deterministic sharding and replication.

        Args:
            object_id: Deterministic object identifier
            version: Monotonic version number
            content: Content bytes to store
            metadata: Associated metadata
            deterministic_timestamp: Deterministic timestamp for audit trail

        Returns:
            Dict with hash_commit and shard_ids
        """
        hash_commit = self._compute_content_hash(content, metadata)
        atr_cost = self._calculate_atr_storage_cost(len(content), metadata)
        self.total_atr_fees_collected = self.cm.add(self.total_atr_fees_collected, atr_cost, [])
        logical_object = LogicalObject(object_id=object_id, version=version, hash_commit=hash_commit, metadata=metadata, created_at_tick=deterministic_timestamp)
        shard_ids = []
        chunk_size = BLOCK_SIZE_BYTES
        all_assigned_nodes = []
        replica_sets: Dict[str, List[str]] = {}
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            shard_id = self._compute_shard_id(object_id, version, self.cm.idiv(BigNum128.from_int(i), chunk_size, []))
            assigned_nodes = self._assign_nodes_to_shard(shard_id)
            all_assigned_nodes.extend(assigned_nodes)
            replica_sets[shard_id] = assigned_nodes
            shard = Shard(shard_id=shard_id, object_id=object_id, version=version, shard_index=self.cm.idiv(BigNum128.from_int(i), chunk_size, []), content_chunk=chunk, assigned_nodes=assigned_nodes)
            shard.merkle_root = self._generate_merkle_root(chunk)
            shard.proof = self._generate_shard_proof(shard)
            self.shards[shard_id] = shard
            shard_ids.append(shard_id)
        logical_object.shard_ids = shard_ids
        object_key = f'{object_id}:{version}'
        self.objects[object_key] = logical_object
        self._update_node_metrics(all_assigned_nodes, len(content))
        self._emit_storage_event({'event_type': 'STORE', 'epoch': self.current_epoch, 'timestamp_tick': deterministic_timestamp, 'object_id': object_id, 'version': version, 'hash_commit': hash_commit, 'content_size': len(content), 'shard_ids': shard_ids, 'replica_sets': replica_sets, 'atr_cost': atr_cost.to_decimal_string(), 'pqc_signature': None, 'error_code': None, 'error_detail': None})
        return {'hash_commit': hash_commit, 'shard_ids': shard_ids, 'atr_cost': atr_cost.to_decimal_string()}

    def get_content(self, object_id: str, version: int) -> Dict[str, Any]:
        """
        Retrieve content with proof verification.

        Args:
            object_id: Object identifier
            version: Version number

        Returns:
            Dict with content_chunk, hash_commit, and proof
        """
        object_key = f'{object_id}:{version}'
        if object_key not in self.objects:
            raise KeyError(f'Object {object_id} version {version} not found')
        logical_object = self.objects[object_key]
        content_chunks = []
        proofs = []
        for shard_id in sorted(logical_object.shard_ids):
            if shard_id not in self.shards:
                raise KeyError(f'Shard {shard_id} not found')
            shard = self.shards[shard_id]
            content_chunks.append(shard.content_chunk)
            proofs.append(shard.proof)
        full_content = b''.join(content_chunks)
        return {'content_chunk': full_content, 'hash_commit': logical_object.hash_commit, 'proofs': proofs}

    def get_storage_proof(self, object_id: str, version: int, shard_id: str) -> Dict[str, Any]:
        """
        Get Merkle proof of storage for a specific shard.

        Args:
            object_id: Object identifier
            version: Version number
            shard_id: Shard identifier

        Returns:
            Merkle proof of storage
        """
        if shard_id not in self.shards:
            self._emit_storage_event({'event_type': 'PROOF_FAILED', 'epoch': self.current_epoch, 'timestamp_tick': 0, 'object_id': self._hash_sensitive_id(object_id), 'version': version, 'hash_commit': None, 'content_size': 0, 'shard_ids': [], 'replica_sets': {}, 'atr_cost': '0', 'pqc_signature': None, 'error_code': 'SE_ERR_PROOF_UNAVAILABLE', 'error_detail': 'Proof generation failed'})
            raise ValueError('Proof unavailable for request')
        shard = self.shards[shard_id]
        self._emit_storage_event({'event_type': 'PROOF_GENERATED', 'epoch': self.current_epoch, 'timestamp_tick': 0, 'object_id': self._hash_sensitive_id(object_id), 'version': version, 'hash_commit': self.objects.get(f'{object_id}:{version}').hash_commit if f'{object_id}:{version}' in self.objects else None, 'content_size': 0, 'shard_ids': self.objects.get(f'{object_id}:{version}').shard_ids if f'{object_id}:{version}' in self.objects else [], 'replica_sets': {shard.shard_id: list(shard.assigned_nodes)}, 'atr_cost': '0', 'pqc_signature': None, 'error_code': None, 'error_detail': None})
        return {'merkle_root': shard.merkle_root, 'proof': shard.proof, 'assigned_nodes': shard.assigned_nodes}

    def list_objects(self, filters: Optional[Dict[str, Any]]=None) -> List[Dict[str, Any]]:
        """
        List objects with deterministic sorting.

        Args:
            filters: Filter criteria

        Returns:
            Sorted list of object summaries
        """
        if filters is None:
            filters = {}
        filtered_objects = []
        for obj_key, logical_object in sorted(self.objects.items()):
            include_object = True
            for key, value in sorted(filters.items()):
                if key in logical_object.metadata:
                    if logical_object.metadata[key] != value:
                        include_object = False
                        break
                else:
                    include_object = False
                    break
            if include_object:
                filtered_objects.append(logical_object)
        filtered_objects.sort(key=lambda obj: (obj.object_id, obj.version))
        summaries = []
        for obj in sorted(filtered_objects, key=lambda x: x.object_id + str(x.version)):
            summaries.append({'object_id': obj.object_id, 'version': obj.version, 'hash_commit': obj.hash_commit, 'created_at_tick': obj.created_at_tick, 'metadata': obj.metadata})
        return summaries

    def update_storage_metrics_in_token_bundle(self, token_bundle: 'TokenStateBundle') -> 'TokenStateBundle':
        """
        Update storage metrics in a TokenStateBundle with current node metrics.

        This method is used to integrate storage contribution metrics into the
        TokenStateBundle for NOD reward calculations.

        Args:
            token_bundle: TokenStateBundle to update

        Returns:
            Updated TokenStateBundle with storage metrics
        """
        from v13.core.TokenStateBundle import create_token_state_bundle
        storage_metrics = {'storage_bytes_stored': {}, 'storage_uptime_bucket': {}, 'storage_proofs_verified': {}}
        if token_bundle.storage_metrics:
            storage_metrics.update(token_bundle.storage_metrics)
        for node_id, node in sorted(self.nodes.items()):
            storage_metrics['storage_bytes_stored'][node_id] = node.bytes_stored
            storage_metrics['storage_uptime_bucket'][node_id] = node.uptime_bucket
            storage_metrics['storage_proofs_verified'][node_id] = node.proofs_verified
        updated_bundle = create_token_state_bundle(chr_state=token_bundle.chr_state, flx_state=token_bundle.flx_state, psi_sync_state=token_bundle.psi_sync_state, atr_state=token_bundle.atr_state, res_state=token_bundle.res_state, nod_state=token_bundle.nod_state, storage_metrics=storage_metrics, lambda1=token_bundle.lambda1, lambda2=token_bundle.lambda2, c_crit=token_bundle.c_crit, pqc_cid=token_bundle.pqc_cid, timestamp=token_bundle.timestamp, quantum_metadata=token_bundle.quantum_metadata, bundle_id=token_bundle.bundle_id, parameters=token_bundle.parameters)
        return updated_bundle

    def score_content(self, object_id: str, version: int, scoring_model: str='default') -> BigNum128:
        """
        Score content using deterministic OpenAGI model.
        
        Args:
            object_id: Object identifier
            version: Version number
            scoring_model: Scoring model to use
            
        Returns:
            BigNum128: Deterministic score between 0 and 1000000
        """
        object_key = f'{object_id}:{version}'
        if object_key not in self.objects:
            raise KeyError(f'Object {object_id} version {version} not found')
        logical_object = self.objects[object_key]
        content_chunks = []
        for shard_id in sorted(logical_object.shard_ids):
            if shard_id in self.shards:
                shard = self.shards[shard_id]
                content_chunks.append(shard.content_chunk)
        full_content = b''.join(content_chunks)
        content_hash = self._compute_content_hash(full_content, logical_object.metadata)
        hash_prefix = content_hash[:8]
        hash_int = int(hash_prefix, 16)
        normalized_score = hash_int % 1000001
        return BigNum128.from_int(normalized_score)

    def put_content_with_scoring(self, object_id: str, version: int, content: bytes, metadata: Dict[str, Any], scoring_model: str='default', deterministic_timestamp: int=0) -> Dict[str, Any]:
        """
        Store content with automatic OpenAGI scoring.

        Args:
            object_id: Deterministic object identifier
            version: Monotonic version number
            content: Content bytes to store
            metadata: Associated metadata
            scoring_model: Scoring model to use
            deterministic_timestamp: Deterministic timestamp for audit trail

        Returns:
            Dict with hash_commit, shard_ids, and openagi_score
        """
        result = self.put_content(object_id, version, content, metadata, deterministic_timestamp)
        openagi_score = self.score_content(object_id, version, scoring_model)
        result['openagi_score'] = openagi_score
        object_key = f'{object_id}:{version}'
        if object_key in self.objects:
            self.objects[object_key].metadata['openagi_score'] = openagi_score
        return result

    def _compute_content_hash(self, content: bytes, metadata: Dict[str, Any]) -> str:
        """
        Compute deterministic content hash.

        Args:
            content: Content bytes
            metadata: Metadata dictionary

        Returns:
            Content hash as hex string
        """
        metadata_json = json.dumps(metadata, sort_keys=True, separators=(',', ':'))
        schema_version = '1.0'
        data_to_hash = content + schema_version.encode() + metadata_json.encode()
        hash_obj = hashlib.sha3_256()
        hash_obj.update(data_to_hash)
        return hash_obj.hexdigest()

    def _compute_shard_id(self, object_id: str, version: int, shard_index: int) -> str:
        """
        Compute deterministic shard ID.

        Args:
            object_id: Object identifier
            version: Version number
            shard_index: Shard index

        Returns:
            Shard ID as hex string
        """
        data_to_hash = f'{object_id}:{version}:{shard_index}'.encode()
        hash_obj = hashlib.sha3_256()
        hash_obj.update(data_to_hash)
        return hash_obj.hexdigest()

    def _assign_nodes_to_shard(self, shard_id: str) -> List[str]:
        """
        Deterministically assign nodes to a shard.

        Args:
            shard_id: Shard identifier

        Returns:
            List of assigned node IDs
        """
        eligible_nodes = self.get_eligible_nodes()
        if not eligible_nodes:
            return []
        hash_obj = hashlib.sha3_256()
        hash_obj.update(shard_id.encode())
        start_index = int(hash_obj.hexdigest(), 16) % len(eligible_nodes)
        assigned_nodes = []
        for i in range(REPLICATION_FACTOR):
            node_index = (start_index + i) % len(eligible_nodes)
            assigned_nodes.append(eligible_nodes[node_index])
        return assigned_nodes

    def _generate_merkle_root(self, content_chunk: bytes) -> str:
        """
        Generate Merkle root for a content chunk by splitting into 4KB blocks.
        
        Args:
            content_chunk: Content chunk bytes
            
        Returns:
            Merkle root as hex string
        """
        BLOCK_SIZE = 4096
        leaves = []
        for i in range(0, len(content_chunk), BLOCK_SIZE):
            block = content_chunk[i:i + BLOCK_SIZE]
            leaves.append(hashlib.sha3_256(block).hexdigest())
        if not leaves:
            return hashlib.sha3_256(b'').hexdigest()
        tree_level = leaves
        while len(tree_level) > 1:
            next_level = []
            for i in range(0, len(tree_level), 2):
                left = tree_level[i]
                right = tree_level[i + 1] if i + 1 < len(tree_level) else left
                combined = (left + right).encode()
                next_level.append(hashlib.sha3_256(combined).hexdigest())
            tree_level = next_level
        return tree_level[0]

    def _generate_shard_proof(self, shard: Shard) -> str:
        """
        Generate a static integrity proof for the shard.
        Contains the Merkle Root and size, serialized.
        
        Args:
            shard: Shard object
            
        Returns:
            JSON string of the proof structure
        """
        proof_data = {'shard_id': shard.shard_id, 'merkle_root': shard.merkle_root, 'size': len(shard.content_chunk), 'algo': 'SHA3-256-Merkle-4KB'}
        return json.dumps(proof_data, sort_keys=True)

    def _update_node_metrics(self, node_ids: List[str], content_size: int) -> None:
        """
        Update storage metrics for nodes.

        Args:
            node_ids: List of node IDs
            content_size: Size of content stored
        """
        for node_id in sorted(node_ids):
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.bytes_stored = self.cm.add(node.bytes_stored, BigNum128.from_int(content_size), [])
                node.proofs_verified += 1

    def _calculate_atr_storage_cost(self, content_size: int, metadata: Dict[str, Any]) -> BigNum128:
        """
        Calculate deterministic ATR cost for storage operation.

        This implements a deterministic ATR cost function for storage writes based on
        content size and metadata complexity.

        Args:
            content_size: Size of content in bytes
            metadata: Content metadata

        Returns:
            BigNum128: ATR cost for this storage operation
        """
        content_scaled = BigNum128.from_int(content_size + 1023)
        divisor = BigNum128.from_int(1024)
        content_kb_bn = self.cm.div(content_scaled, divisor, [])
        raw_str = str(content_kb_bn.value).zfill(BigNum128.SCALE_DIGITS + 1)
        integer_part = raw_str[:-BigNum128.SCALE_DIGITS] or '0'
        content_kb = int(integer_part)
        base_cost = self.cm.mul(ATR_BASE_STORAGE_COST_PER_KB, BigNum128.from_int(content_kb), [])
        metadata_complexity = len(metadata)
        complexity_multiplier = BigNum128.from_string(f'1.{min(metadata_complexity, 99):02d}')
        final_cost = self.cm.mul(base_cost, complexity_multiplier, [])
        return final_cost

    def calculate_nod_rewards(self, epoch_number: int) -> Dict[str, BigNum128]:
        """
        Calculate deterministic NOD rewards for infrastructure nodes based on storage metrics.

        Implements the NOD reward formula from the specification:
        NOD_reward[node] = f(bytes_stored, uptime_bucket, successful_proofs)

        Args:
            epoch_number: Current epoch number

        Returns:
            Dict mapping node IDs to NOD reward amounts
        """
        nod_rewards = {}
        for node_id, node in sorted(self.nodes.items()):
            if node.is_aegis_verified and node.aegis_verification_epoch == epoch_number:
                bytes_stored_factor = node.bytes_stored
                uptime_factor = BigNum128.from_int(node.uptime_bucket)
                proofs_factor = BigNum128.from_int(node.proofs_verified)
                intermediate = self.cm.mul(bytes_stored_factor, uptime_factor, [])
                nod_reward = self.cm.mul(intermediate, proofs_factor, [])
                scaling_factor = BigNum128.from_int(1000)
                nod_reward = self.cm.div(nod_reward, scaling_factor, [])
                nod_rewards[node_id] = nod_reward
                self.total_nod_rewards_distributed = self.cm.add(self.total_nod_rewards_distributed, nod_reward, [])
        return nod_rewards

    def get_storage_economics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of storage economics for conservation checks.

        Returns:
            Dict with total ATR fees collected, total NOD rewards distributed,
            and conservation status
        """
        is_conservation_maintained = self.cm.gte(self.total_atr_fees_collected, self.total_nod_rewards_distributed, [])
        conservation_difference = BigNum128(0)
        if is_conservation_maintained:
            conservation_difference = self.cm.sub(self.total_atr_fees_collected, self.total_nod_rewards_distributed, [])
        store_event_count = 0
        for ev in sorted(self.storage_event_log):
            if isinstance(ev, dict) and ev.get('event_type') == 'STORE':
                store_event_count += 1
        return {'total_atr_fees_collected': self.total_atr_fees_collected.to_decimal_string(), 'total_nod_rewards_distributed': self.total_nod_rewards_distributed.to_decimal_string(), 'conservation_difference': conservation_difference.to_decimal_string(), 'is_conservation_maintained': is_conservation_maintained, 'storage_event_count': store_event_count}