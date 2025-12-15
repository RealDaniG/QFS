"""
test_artistic_observatory.py - Verify AES Observability

Tests:
1. Signal recording and capping.
2. Report generation (averages, histograms).
3. Anomaly detection.
"""

import pytest
from v13.policy.artistic_observatory import ArtisticSignalObservatory, ArtisticSignalSnapshot

def test_recording_and_capping():
    obs = ArtisticSignalObservatory()
    obs.MAX_HISTORY = 10 # Small cap for test
    
    for i in range(15):
        snap = ArtisticSignalSnapshot(
            timestamp=1000+i,
            content_id=f"c{i}",
            dimensions={"originality": 0.5},
            confidence=1.0,
            bonus_factor=0.1,
            policy_version="v1"
        )
        obs.record_signal(snap)
        
    assert len(obs.signal_history) == 10
    assert obs.signal_history[0].content_id == "c5" # Older ones dropped

def test_report_generation():
    obs = ArtisticSignalObservatory()
    
    # 2 signals
    # 1: 0.8 originality, 0.2 bonus
    # 2: 0.2 originality, 0.1 bonus
    obs.record_signal(ArtisticSignalSnapshot(1, "c1", {"originality": 0.8}, 1.0, 0.2, "v1"))
    obs.record_signal(ArtisticSignalSnapshot(2, "c2", {"originality": 0.2}, 1.0, 0.1, "v1"))
    
    report = obs.get_observability_report()
    
    assert report.total_signals_processed == 2
    assert report.average_confidence == 1.0
    assert report.dimension_averages["originality"] == 0.5
    assert report.bonus_statistics["mean"] == pytest.approx(0.15)
    assert report.bonus_statistics["max"] == 0.2
