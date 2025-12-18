"""
Tests for ArtisticSignalAddon (AES) - QFS V13.8

Verifies:
1. Deterministic evaluation of all 5 dimensions.
2. Compliance with SignalAddon contract (pure, no side effects).
3. Zero-Sim compliance (no randomness, no wall-clock time).
4. AEGIS integration (metadata pass-through).
"""
import pytest
from v13.ATLAS.src.signals.artistic import ArtisticSignalAddon
from v13.ATLAS.src.signals.base import SignalResult

@pytest.fixture
def addon():
    return ArtisticSignalAddon()

def test_dimensions_pure_evaluation(addon):
    """Verify that all 5 dimensions return normalized scores [0,1] deterministically."""
    content = 'This is a test content with some structure.\n\nIt has multiple paragraphs.'
    context = {'views': 100, 'saves': 10}
    result1 = addon.evaluate(content, context)
    result2 = addon.evaluate(content, context)
    assert result1.result_hash == result2.result_hash
    dims = result1.metadata['dimensions']
    assert 'composition' in dims
    assert 'originality' in dims
    assert 'emotional_resonance' in dims
    assert 'technical_execution' in dims
    assert 'cultural_context' in dims
    for dim, score in dims.items():
        assert 0 <= score <= 1, f'Dimension {dim} score {score} out of bounds'

def test_aegis_metadata_integration(addon):
    """Verify AEGIS reputation is passed through metadata."""
    content = 'Artistic content.'
    context = {'views': 100, 'aegis_verification': {'verified': True, 'reputation_tier': 'veteran', 'user_id': 'did:key:z123'}}
    result = addon.evaluate(content, context)
    aegis_ctx = result.metadata['aegis_context']
    assert aegis_ctx['verified'] is True
    assert aegis_ctx['reputation_tier'] == 'veteran'
    assert aegis_ctx['user_id'] == 'did:key:z123'

def test_zero_sim_compliance(addon):
    """Verify no randomness is used (heuristic)."""
    content = 'Same input'
    context = {}
    results = set()
    for _ in range(100):
        res = addon.evaluate(content, context)
        results.add(res.result_hash)
    assert len(results) == 1, 'Non-deterministic output detected'

def test_technical_execution(addon):
    """Test technical execution heuristic (markdown detection)."""
    res_plain = addon.evaluate('Just text', {})
    score_plain = res_plain.metadata['dimensions']['technical_execution']
    res_rich = addon.evaluate('**Bold** and *Italic*.', {})
    score_rich = res_rich.metadata['dimensions']['technical_execution']
    assert score_rich > score_plain, 'Rich text should score higher on technical execution'

def test_emotional_resonance(addon):
    """Test emotional resonance based on saves/views."""
    content = 'Valid content'
    ctx_high = {'views': 100, 'saves': 50}
    res_high = addon.evaluate(content, ctx_high)
    ctx_low = {'views': 100, 'saves': 1}
    res_low = addon.evaluate(content, ctx_low)
    score_high = res_high.metadata['dimensions']['emotional_resonance']
    score_low = res_low.metadata['dimensions']['emotional_resonance']
    assert score_high > score_low, 'Higher save rate should imply higher resonance'
