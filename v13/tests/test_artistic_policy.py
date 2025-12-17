"""
test_artistic_policy.py - Validation of Artistic Policy Logic (GUT Edition)

Verifies:
1. Deterministic bonus calculation with integer scaling.
2. AEGIS reputation tier weighting.
3. Config hash stability.
4. Stats accumulation.
"""
import pytest
from v13.policy.artistic_policy import ArtisticSignalPolicy, ArtisticPolicy
from v13.policy.artistic_constants import SCALE

@pytest.fixture
def policy():
    return ArtisticSignalPolicy()

def test_deterministic_hash(policy):
    """Policy config hash must be stable."""
    h1 = policy.policy.hash
    h2 = policy.policy.hash
    assert h1 == h2
    assert len(h1) == 64

def test_basic_bonus_calculation(policy):
    """Verify base bonus logic without AEGIS."""
    half_scale = SCALE // 2
    dims = {'composition': half_scale, 'color_harmony': half_scale, 'symmetry': half_scale, 'complexity': half_scale, 'narrative': half_scale, 'originality': half_scale, 'resonance': half_scale}
    result = policy.calculate_artistic_bonus(dims, confidence=SCALE)
    assert result.bonus_factor == 0.3
    assert result.cap_applied == 0.3
    conf_low = int(0.4 * SCALE)
    result_low_conf = policy.calculate_artistic_bonus(dims, confidence=conf_low)
    assert abs(result_low_conf.bonus_factor - 0.2) < 0.0001
    assert result_low_conf.cap_applied is None

def test_aegis_reputation_boost(policy):
    """Verify AEGIS tier adjustments."""
    dims = {'originality': SCALE, 'composition': 0, 'color_harmony': 0, 'symmetry': 0, 'complexity': 0, 'narrative': 0, 'resonance': 0}
    res_new = policy.calculate_artistic_bonus(dims, confidence=SCALE, aegis_context={'reputation_tier': 'new'})
    assert res_new.weights_applied['originality'] == 200000000
    assert abs(res_new.bonus_factor - 0.2) < 0.0001
    res_vet = policy.calculate_artistic_bonus(dims, confidence=SCALE, aegis_context={'reputation_tier': 'veteran'})
    assert res_vet.weights_applied['originality'] == 350000000
    assert res_vet.bonus_factor == 0.3
    assert 'veteran_originality_boost' in res_vet.reputation_adjustments
    dims_res = {'resonance': SCALE, 'originality': 0, 'composition': 0, 'color_harmony': 0, 'symmetry': 0, 'complexity': 0, 'narrative': 0}
    res_est = policy.calculate_artistic_bonus(dims_res, confidence=SCALE, aegis_context={'reputation_tier': 'established'})
    assert res_est.weights_applied['resonance'] == 200000000
    assert abs(res_est.bonus_factor - 0.2) < 0.0001
    assert 'established_resonance_boost' in res_est.reputation_adjustments

def test_stats_rolling_window(policy):
    """Verify stats don't grow indefinitely."""
    dims = {'composition': SCALE // 2}
    for i in range(150):
        policy.calculate_artistic_bonus(dims, confidence=SCALE)
    stats = policy.observation_stats
    assert stats.total_signals_processed == 150
    assert len(stats.dimension_distributions['composition']) == 100
    assert len(stats.bonus_distribution) == 100