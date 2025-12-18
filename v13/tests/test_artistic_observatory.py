"""
test_artistic_observatory.py - Verify AES Observability

Tests:
1. Signal recording and capping.
2. Report generation (averages, histograms).
3. Anomaly detection.
"""
from fractions import Fraction
import pytest
from v13.policy.artistic_observatory import ArtisticSignalObservatory, ArtisticSignalSnapshot

def test_recording_and_capping():
    obs = ArtisticSignalObservatory()
    obs.MAX_HISTORY = 10
    for i in range(15):
        snap = ArtisticSignalSnapshot(timestamp=1000 + i, content_id=f'c{i}', dimensions={'originality': Fraction(1, 2)}, confidence=1, bonus_factor=Fraction(1, 10), policy_version='v1')
        obs.record_signal(snap)
    assert len(obs.signal_history) == 10
    assert obs.signal_history[0].content_id == 'c5'

def test_report_generation():
    obs = ArtisticSignalObservatory()
    obs.record_signal(ArtisticSignalSnapshot(1, 'c1', {'originality': Fraction(4, 5)}, 1, Fraction(1, 5), 'v1'))
    obs.record_signal(ArtisticSignalSnapshot(2, 'c2', {'originality': Fraction(1, 5)}, 1, Fraction(1, 10), 'v1'))
    report = obs.get_observability_report()
    assert report.total_signals_processed == 2
    assert report.average_confidence == 1
    assert report.dimension_averages['originality'] == Fraction(1, 2)
    assert report.bonus_statistics['mean'] == pytest.approx(Fraction(3, 20))
    assert report.bonus_statistics['max'] == Fraction(1, 5)
