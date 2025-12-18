import hashlib
import json
from typing import Any, Dict, List, Mapping, Tuple
import pytest
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath

def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

def _state_hash(summary: Mapping[str, Any]) -> str:
    core = {'object_count': summary.get('object_count'), 'objects': summary.get('objects')}
    return hashlib.sha3_256(_canonical_json(core).encode()).hexdigest()

def replay_storage_events(events: List[Mapping[str, Any]]) -> Dict[str, Any]:
    """Pure replay helper: rebuild a snapshot from StorageEvents.

    This function intentionally does not touch disk/network and does not
    instantiate StorageEngine.

    Snapshot includes:
    - objects: object_key -> {object_id, version, hash_commit, content_size, shard_ids, replica_sets, epoch}
    - proof_accounting: node_id -> {generated:int, failed:int}
    - counts
    """
    objects: Dict[str, Dict[str, Any]] = {}
    proof_accounting: Dict[str, Dict[str, int]] = {}
    for ev in sorted(events):
        event_type = ev.get('event_type')
        if event_type == 'STORE':
            object_id = ev.get('object_id')
            version = ev.get('version')
            if object_id is None or version is None:
                continue
            object_key = f'{object_id}:{version}'
            objects[object_key] = {'object_id': object_id, 'version': version, 'hash_commit': ev.get('hash_commit'), 'content_size': ev.get('content_size'), 'shard_ids': list(ev.get('shard_ids') or []), 'replica_sets': ev.get('replica_sets') or {}, 'epoch': ev.get('epoch')}
            continue
        if event_type == 'PROOF_GENERATED':
            replica_sets = ev.get('replica_sets') or {}
            for _, nodes in sorted(replica_sets.items()):
                for node_id in sorted(nodes):
                    proof_accounting.setdefault(node_id, {'generated': 0, 'failed': 0})
                    proof_accounting[node_id]['generated'] += 1
            continue
        if event_type == 'PROOF_FAILED':
            proof_accounting.setdefault('__unassigned__', {'generated': 0, 'failed': 0})
            proof_accounting['__unassigned__']['failed'] += 1
            continue
    summary = {'object_count': len(objects), 'objects': objects, 'proof_accounting': proof_accounting}
    return summary

def _live_snapshot(engine: StorageEngine) -> Dict[str, Any]:
    objects: Dict[str, Dict[str, Any]] = {}
    for object_key, obj in sorted(engine.objects.items()):
        replica_sets: Dict[str, List[str]] = {}
        for shard_id in sorted(obj.shard_ids):
            replica_sets[shard_id] = list(engine.shards[shard_id].assigned_nodes)
        content_size = sum((len(engine.shards[shard_id].content_chunk) for shard_id in obj.shard_ids))
        objects[object_key] = {'object_id': obj.object_id, 'version': obj.version, 'hash_commit': obj.hash_commit, 'content_size': content_size, 'shard_ids': list(obj.shard_ids), 'replica_sets': replica_sets, 'epoch': engine.current_epoch}
    return {'object_count': len(objects), 'objects': objects}

def _live_proof_accounting(engine: StorageEngine, shard_ids: List[str], object_id: str, version: int) -> Dict[str, Dict[str, int]]:
    accounting: Dict[str, Dict[str, int]] = {}
    for shard_id in sorted(shard_ids):
        proof = engine.get_storage_proof(object_id, version, shard_id)
        for node_id in proof.get('assigned_nodes') or []:
            accounting.setdefault(node_id, {'generated': 0, 'failed': 0})
            accounting[node_id]['generated'] += 1
    return accounting

def test_storageengine_replay_snapshot_matches_live() -> None:
    cm = CertifiedMath()
    engine = StorageEngine(cm)
    engine.register_storage_node('node1', '127.0.0.1', 8001)
    engine.register_storage_node('node2', '127.0.0.1', 8002)
    engine.register_storage_node('node3', '127.0.0.1', 8003)
    engine.register_storage_node('node4', '127.0.0.1', 8004)
    engine.advance_epoch(1)
    engine.put_content(object_id='obj_a', version=1, content=b'A' * 1000, metadata={'author': 'u1', 'tags': ['x']}, deterministic_timestamp=10)
    engine.put_content(object_id='obj_b', version=1, content=b'B' * 2000, metadata={'author': 'u2', 'tags': ['y']}, deterministic_timestamp=11)
    events = list(engine.storage_event_log)
    replayed = replay_storage_events(events)
    live = _live_snapshot(engine)
    assert replayed['object_count'] == live['object_count']
    assert set(replayed['objects'].keys()) == set(live['objects'].keys())
    for k in sorted(live['objects'].keys()):
        assert replayed['objects'][k]['object_id'] == live['objects'][k]['object_id']
        assert replayed['objects'][k]['version'] == live['objects'][k]['version']
        assert replayed['objects'][k]['hash_commit'] == live['objects'][k]['hash_commit']
        assert replayed['objects'][k]['content_size'] == live['objects'][k]['content_size']
        assert replayed['objects'][k]['shard_ids'] == live['objects'][k]['shard_ids']
        assert replayed['objects'][k]['replica_sets'] == live['objects'][k]['replica_sets']
        assert replayed['objects'][k]['epoch'] == live['objects'][k]['epoch']

def test_storageengine_replay_state_hash_matches_live() -> None:
    cm = CertifiedMath()
    engine = StorageEngine(cm)
    engine.register_storage_node('node1', '127.0.0.1', 8001)
    engine.register_storage_node('node2', '127.0.0.1', 8002)
    engine.register_storage_node('node3', '127.0.0.1', 8003)
    engine.advance_epoch(7)
    engine.put_content(object_id='obj_hash', version=1, content=b'Z' * 4096, metadata={'author': 'u3', 'tags': ['z'], 'created_at_tick': 7}, deterministic_timestamp=99)
    events = list(engine.storage_event_log)
    replayed = replay_storage_events(events)
    live = _live_snapshot(engine)
    assert _state_hash(replayed) == _state_hash(live)

def test_storageengine_replay_proof_accounting_matches_live() -> None:
    cm = CertifiedMath()
    engine = StorageEngine(cm)
    engine.register_storage_node('node1', '127.0.0.1', 8001)
    engine.register_storage_node('node2', '127.0.0.1', 8002)
    engine.register_storage_node('node3', '127.0.0.1', 8003)
    engine.register_storage_node('node4', '127.0.0.1', 8004)
    engine.advance_epoch(2)
    store_res = engine.put_content(object_id='obj_proof', version=1, content=b'P' * 1024, metadata={'author': 'u4'}, deterministic_timestamp=123)
    shard_ids = list(store_res['shard_ids'])
    live_proofs = _live_proof_accounting(engine, shard_ids, 'obj_proof', 1)
    replayed = replay_storage_events(list(engine.storage_event_log))
    replay_proofs = replayed.get('proof_accounting') or {}
    assert set(replay_proofs.keys()) >= set(live_proofs.keys())
    for node_id in sorted(live_proofs):
        assert replay_proofs[node_id]['generated'] == live_proofs[node_id]['generated']
