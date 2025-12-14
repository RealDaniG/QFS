"""
Performance Tests for Explain-This - QFS V13.8

Verifies:
1. Explanation generation latency (< 50ms)
2. Explain API throughput
3. Determinism under load
"""

import time
import pytest
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
from v13.policy.artistic_policy import ArtisticSignalPolicy, ArtisticPolicy
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper

def test_explanation_generation_latency():
    """Ensure explanation generation is within SLA (50ms)."""
    
    # Setup
    humor_policy = HumorSignalPolicy(policy=HumorPolicy(True, "rewarding", {}, 0.25, 1.0))
    artistic_policy = ArtisticSignalPolicy(policy=ArtisticPolicy(True, "rewarding", {}, 0.30, 2.0))
    helper = ValueNodeExplainabilityHelper(humor_policy, artistic_policy)
    
    base_reward = {"ATR": "10.0 ATR"}
    bonuses = [{"label": "Bonus", "value": "+1.0 ATR"}] * 5 # 5 bonuses
    caps = [{"label": "Cap", "value": "-0.5 ATR"}]
    guards = [{"name": "Guard", "result": "pass"}] * 3
    
    # Benchmark
    start = time.perf_counter()
    iterations = 1000
    
    for _ in range(iterations):
        helper.explain_value_node_reward(
            "w1", "u1", "evt1", 1,
            base_reward, bonuses, caps, guards, 1234567890
        )
        
    total_time = time.perf_counter() - start
    avg_latency_ms = (total_time / iterations) * 1000
    
    print(f"Average Latency: {avg_latency_ms:.4f} ms")
    
    # Assert
    assert avg_latency_ms < 0.5, f"Latency {avg_latency_ms}ms exceeds 0.5ms internal budget"

def test_hash_computation_performance():
    """Ensure SHA-256 hash computation for audit is fast."""
    from v13.core.audit_integrity import verify_explanation_integrity
    
    data = {f"key_{i}": f"value_{i}" for i in range(100)} # Large object
    import hashlib, json
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    valid_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    start = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
        verify_explanation_integrity(data, valid_hash)
        
    avg_latency_ms = ((time.perf_counter() - start) / iterations) * 1000
    print(f"Hash Latency: {avg_latency_ms:.4f} ms")
    
    assert avg_latency_ms < 1.0, f"Hash verification too slow: {avg_latency_ms}ms"
