"""
test_aes_vectors.py - Verification of Deterministic AES Vector Generation

Verifies:
1. Feature extraction logic (mocks metadata).
2. Deterministic vector computation.
3. Stable hashing of ArtisticVector.
"""
import pytest
from v13.policy.artistic_policy import ArtisticSignalPolicy
from v13.policy.artistic_constants import SCALE, PHI

@pytest.fixture
def policy():
    return ArtisticSignalPolicy()

def test_composition_extractor(policy):
    """Test composition scoring."""
    metadata = {'width': 1618, 'height': 1000, 'elements': []}
    vector = policy.compute_vector('test1', metadata, [])
    assert vector.composition > SCALE // 3

def test_vector_determinism(policy):
    """Test that same input produces identical vector hash."""
    metadata = {'width': 1000, 'height': 1000, 'palette': [{'hue': 0}, {'hue': 137507764}], 'elements': [{'x': 500, 'y': 500, 'type': 'circle'}]}
    v1 = policy.compute_vector('content_A', metadata, ['event1'])
    v2 = policy.compute_vector('content_A', metadata, ['event1'])
    assert v1.vector_hash == v2.vector_hash
    assert v1.composition == v2.composition
    assert v1.color_harmony == v2.color_harmony
    metadata_diff = metadata.copy()
    metadata_diff['width'] = 1001
    v3 = policy.compute_vector('content_A', metadata_diff, ['event1'])
    assert v1.vector_hash != v3.vector_hash

def test_originality_and_resonance_decay(policy):
    """Test decay based on event count."""
    metadata = {}
    v0 = policy.compute_vector('c1', metadata, [])
    assert v0.originality == SCALE
    assert v0.resonance == SCALE
    v10 = policy.compute_vector('c1', metadata, ['e'] * 10)
    assert v10.originality == SCALE - 10 * SCALE // 100
    assert v10.resonance == SCALE - 10 * SCALE // 50

def test_color_harmony_golden_angle(policy):
    """Test color harmony extractor explicitly."""
    metadata = {'palette': [{'hue': 0}, {'hue': 137507764}]}
    v = policy.compute_vector('c_color', metadata, [])
    assert v.color_harmony == SCALE
    metadata_bad = {'palette': [{'hue': 0}, {'hue': 10000000}]}
    v_bad = policy.compute_vector('c_bad', metadata_bad, [])
    assert v_bad.color_harmony < v.color_harmony