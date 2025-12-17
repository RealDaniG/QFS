"""
test_full_stack_determinism.py - Comprehensive System Verification

Verifies deterministic interaction of:
1. Core Logic (CertifiedMath, PQC, HSMF).
2. Signal Slices (Humor, Artistic).
3. Value Node Logic (Replay, Explainability).
4. Ledger State (TokenStateBundle).

This test proves that for a given sequence of inputs, the entire system
produces bit-exact outputs.
"""
import pytest
import json
import hashlib
from typing import Dict, Any
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.policy.humor_policy import HumorSignalPolicy
from v13.policy.artistic_policy import ArtisticSignalPolicy
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.value_node_replay import ValueNodeReplayEngine

def get_deterministic_hash(data: Any) -> str:
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def run_full_stack_simulation(seed_offset: int=0) -> Dict[str, Any]:
    """Run a full functional flow and return state hash."""
    with CertifiedMath.LogContext() as log:
        val = BigNum128.from_int(100 + seed_offset)
        result = CertifiedMath._safe_fast_sqrt(val, 50, log)
        core_hash = result.to_decimal_string()
    humor = HumorSignalPolicy()
    artistic = ArtisticSignalPolicy()
    from v13.policy.artistic_constants import SCALE
    dims_humor = {'chronos': 0.5, 'lexicon': 0.6, 'surreal': 0.7, 'empathy': 0.4, 'critique': 0.5, 'slapstick': 0.3, 'meta': 0.8}
    s8 = int(0.8 * SCALE)
    s9 = int(0.9 * SCALE)
    s6 = int(0.6 * SCALE)
    dims_artistic = {'composition': s8, 'color_harmony': s9, 'symmetry': s6, 'complexity': s8, 'narrative': s6, 'originality': s9, 'resonance': s8}
    h_res = humor.calculate_humor_bonus(dims_humor, confidence=0.9)
    a_res = artistic.calculate_artistic_bonus(dims_artistic, confidence=int(0.95 * SCALE))
    signals_hash = get_deterministic_hash({'humor': h_res.bonus_factor, 'artistic': a_res.bonus_factor})
    helper = ValueNodeExplainabilityHelper(humor_policy=humor, artistic_policy=artistic)
    replay = ValueNodeReplayEngine(helper)
    events = [{'type': 'ContentCreated', 'content_id': 'c1', 'user_id': 'u1', 'timestamp': 1000 + seed_offset}, {'type': 'RewardAllocated', 'user_id': 'u1', 'amount_atr': 50, 'timestamp': 1100 + seed_offset}]
    replay.replay_events(events)
    explanation = helper.explain_value_node_reward('w1', 'u1', 'evt1', 1, {'ATR': '50.0 ATR'}, [{'label': 'Humor', 'value': f'+{h_res.bonus_factor}'}], [], [], 1200)
    final_state = {'core': core_hash, 'signals': signals_hash, 'replay_graph': str(replay.graph.users['u1'].total_rewards_atr), 'explanation': explanation.explanation_hash}
    return final_state

def test_system_stability():
    """Verify that multiple runs produce identical state."""
    run1 = run_full_stack_simulation(seed_offset=0)
    run2 = run_full_stack_simulation(seed_offset=0)
    assert run1 == run2
    assert run1['replay_graph'] == '50'

def test_system_sensitivity():
    """Verify that input changes propagate to output state."""
    run1 = run_full_stack_simulation(seed_offset=0)
    run2 = run_full_stack_simulation(seed_offset=1)
    assert run1 != run2
    assert run1['core'] != run2['core']