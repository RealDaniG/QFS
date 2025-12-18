from v13.core.StorageEngine import StorageEngine
from v13.core.storage_economic_views import compute_storage_metrics_from_events
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_storage_metrics_from_events_matches_live_bytes_stored() -> None:
    cm = CertifiedMath()
    engine = StorageEngine(cm)
    engine.register_storage_node('node1', '127.0.0.1', 8001)
    engine.register_storage_node('node2', '127.0.0.1', 8002)
    engine.register_storage_node('node3', '127.0.0.1', 8003)
    engine.advance_epoch(3)
    engine.put_content(object_id='obj_metrics', version=1, content=b'M' * 100, metadata={'author': 'u'}, deterministic_timestamp=1)
    view = compute_storage_metrics_from_events(list(engine.storage_event_log))
    for node_id, node in engine.nodes.items():
        assert view.bytes_stored_per_node.get(node_id, BigNum128.from_int(0)).value == node.bytes_stored.value

def test_storage_metrics_proof_counts_deterministic() -> None:
    cm = CertifiedMath()
    engine = StorageEngine(cm)
    engine.register_storage_node('node1', '127.0.0.1', 8001)
    engine.register_storage_node('node2', '127.0.0.1', 8002)
    engine.register_storage_node('node3', '127.0.0.1', 8003)
    engine.advance_epoch(4)
    res = engine.put_content(object_id='obj_metrics_proof', version=1, content=b'Q' * 200, metadata={'author': 'u'}, deterministic_timestamp=2)
    for shard_id in res['shard_ids']:
        engine.get_storage_proof('obj_metrics_proof', 1, shard_id)
    v1 = compute_storage_metrics_from_events(list(engine.storage_event_log))
    v2 = compute_storage_metrics_from_events(list(engine.storage_event_log))
    assert v1 == v2
    assert v1.proof_failures == 0
    assert sum(v1.proofs_generated_per_node.values()) > 0
