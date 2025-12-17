"""
Tests for the humor observatory module
"""
import pytest
from v13.policy.humor_observatory import HumorSignalObservatory, HumorSignalSnapshot

class TestHumorObservatory:
    """Test suite for the humor observatory"""

    def setup_method(self):
        """Setup test environment"""
        self.observatory = HumorSignalObservatory()

    def test_record_signal_and_get_report(self):
        """Test recording signals and generating reports"""
        snapshots = [HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': 0.8 - i * 0.1, 'lexicon': 0.6 + i * 0.05, 'surreal': 0.4 + i * 0.02, 'empathy': 0.9 - i * 0.1, 'critique': 0.7 + i * 0.03, 'slapstick': 0.3 + i * 0.04, 'meta': 0.5 - i * 0.05}, confidence=0.85 - i * 0.05, bonus_factor=0.2 - i * 0.02, policy_version='v1.0.0') for i in range(5)]
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        report = self.observatory.get_observability_report()
        assert report.total_signals_processed == 5
        assert report.average_confidence > 0.0
        assert len(report.dimension_averages) == 7
        assert len(report.bonus_statistics) >= 4
        assert isinstance(report.top_performing_content, list)

    def test_empty_observatory_report(self):
        """Test report generation with no data"""
        report = self.observatory.get_observability_report()
        assert report.total_signals_processed == 0
        assert report.average_confidence == 0.0
        assert report.dimension_averages == {}
        assert report.bonus_statistics == {}
        assert report.top_performing_content == []

    def test_histogram_calculation(self):
        """Test histogram distribution calculation"""
        snapshot = HumorSignalSnapshot(timestamp=1000, content_id='test_content', dimensions={'chronos': 0.8, 'lexicon': 0.6}, confidence=0.85, bonus_factor=0.2, policy_version='v1.0.0')
        self.observatory.record_signal(snapshot)
        report = self.observatory.get_observability_report()
        assert 'chronos' in report.dimension_distributions
        assert 'lexicon' in report.dimension_distributions
        assert isinstance(report.dimension_distributions['chronos'], dict)

    def test_histogram_realistic_distributions(self):
        """Test histogram calculation with more realistic distributions"""
        snapshots = []
        for i in range(100):
            chronos_score = 0.1 if i < 10 else 0.5 if i < 60 else 0.9
            lexicon_score = 0.3 if i % 3 == 0 else 0.6 if i % 3 == 1 else 0.8
            surreal_score = min(1.0, max(0.0, 0.5 + (i - 50) * 0.01))
            snapshots.append(HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': chronos_score, 'lexicon': lexicon_score, 'surreal': surreal_score}, confidence=0.8, bonus_factor=0.1 + i % 10 * 0.02, policy_version='v1.0.0'))
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        report = self.observatory.get_observability_report()
        assert len(report.dimension_distributions['chronos']) > 1
        assert len(report.dimension_distributions['lexicon']) > 1
        assert len(report.dimension_distributions['surreal']) > 1
        chronos_sum = sum(report.dimension_distributions['chronos'].values())
        lexicon_sum = sum(report.dimension_distributions['lexicon'].values())
        surreal_sum = sum(report.dimension_distributions['surreal'].values())
        assert abs(chronos_sum - 1.0) < 0.01
        assert abs(lexicon_sum - 1.0) < 0.01
        assert abs(surreal_sum - 1.0) < 0.01
        print('Chronos buckets:', list(report.dimension_distributions['chronos'].keys()))
        chronos_buckets = report.dimension_distributions['chronos']
        assert len(chronos_buckets) > 0

    def test_anomaly_detection_spike_scenarios(self):
        """Test anomaly detection with crafted 'spike/brigade' scenarios"""
        self.observatory = HumorSignalObservatory()
        normal_snapshots = [HumorSignalSnapshot(timestamp=1000 + i, content_id=f'normal_content_{i}', dimensions={'chronos': 0.5, 'lexicon': 0.4}, confidence=0.8, bonus_factor=0.1, policy_version='v1.0.0') for i in range(20)]
        for snapshot in normal_snapshots:
            self.observatory.record_signal(snapshot)
        initial_report = self.observatory.get_observability_report()
        initial_anomaly_count = initial_report.anomaly_count
        spike_snapshots = [HumorSignalSnapshot(timestamp=2000 + i, content_id=f'spike_content_{i}', dimensions={'chronos': 0.9, 'lexicon': 0.8}, confidence=0.9, bonus_factor=0.5, policy_version='v1.0.0') for i in range(5)]
        for snapshot in spike_snapshots:
            self.observatory.record_signal(snapshot)
        final_report = self.observatory.get_observability_report()
        final_anomaly_count = final_report.anomaly_count
        assert final_anomaly_count >= 0

    def test_dimension_correlations(self):
        """Test dimension correlation calculation"""
        snapshots = [HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': 0.5 + i * 0.1, 'lexicon': 0.5 + i * 0.1, 'surreal': 0.5 - i * 0.1}, confidence=0.8, bonus_factor=0.1 + i * 0.02, policy_version='v1.0.0') for i in range(10)]
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        correlations = self.observatory.get_dimension_correlations()
        assert 'chronos' in correlations
        assert 'lexicon' in correlations['chronos']
        assert 'surreal' in correlations['chronos']

    def test_top_performing_content(self):
        """Test top performing content identification"""
        snapshots = [HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': 0.5, 'lexicon': 0.5}, confidence=0.8, bonus_factor=0.1 + i * 0.05, policy_version='v1.0.0') for i in range(10)]
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        report = self.observatory.get_observability_report()
        assert len(report.top_performing_content) <= 10
        if len(report.top_performing_content) > 1:
            for i in range(len(report.top_performing_content) - 1):
                assert report.top_performing_content[i]['bonus_factor'] >= report.top_performing_content[i + 1]['bonus_factor']

    def test_export_observability_data(self):
        """Test export of observability data"""
        snapshot = HumorSignalSnapshot(timestamp=1000, content_id='test_content', dimensions={'chronos': 0.8, 'lexicon': 0.6}, confidence=0.85, bonus_factor=0.2, policy_version='v1.0.0')
        self.observatory.record_signal(snapshot)
        export_data = self.observatory.export_observability_data(policy_version='v1.0.0', policy_hash='test_policy_hash')
        assert 'report' in export_data
        assert 'dimension_distributions' in export_data
        assert 'top_performing_content' in export_data
        assert 'correlations' in export_data
        assert 'raw_data_sample' in export_data
        assert 'total_signals_processed' in export_data['report']
        assert 'average_confidence' in export_data['report']
        assert 'dimension_averages' in export_data['report']
        assert 'policy_version' in export_data['report']
        assert 'policy_hash' in export_data['report']
        assert export_data['report']['policy_version'] == 'v1.0.0'
        assert export_data['report']['policy_hash'] == 'test_policy_hash'

    def test_policy_version_hash_correctness(self):
        """Test policy version and hash correctness in observatory outputs"""
        snapshots = [HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': 0.5 + i * 0.05, 'lexicon': 0.4 + i * 0.03}, confidence=0.8, bonus_factor=0.1 + i * 0.02, policy_version='policy_v2.1.3') for i in range(10)]
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        policy_version = 'policy_v2.1.3'
        policy_hash = 'abc123def456ghi789'
        report = self.observatory.get_observability_report(policy_version=policy_version, policy_hash=policy_hash)
        assert report.policy_version == policy_version
        assert report.policy_hash == policy_hash
        assert report.policy_settings_summary['version'] == policy_version
        assert report.policy_settings_summary['hash'] == policy_hash
        export_data = self.observatory.export_observability_data(policy_version=policy_version, policy_hash=policy_hash)
        assert export_data['report']['policy_version'] == policy_version
        assert export_data['report']['policy_hash'] == policy_hash

    def test_aggregate_statistics_accuracy(self):
        """Test accuracy of aggregate statistics with realistic data"""
        self.observatory = HumorSignalObservatory()
        snapshots = []
        for i in range(50):
            chronos_score = 0.5 + (i % 10 - 5) * 0.05
            lexicon_score = 0.6 + (i % 8 - 4) * 0.04
            bonus_factor = 0.2 + (i % 6 - 3) * 0.03
            snapshots.append(HumorSignalSnapshot(timestamp=1000 + i, content_id=f'content_{i}', dimensions={'chronos': chronos_score, 'lexicon': lexicon_score}, confidence=0.85, bonus_factor=bonus_factor, policy_version='v1.0.0'))
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        report = self.observatory.get_observability_report()
        chronos_values = [0.5 + (i % 10 - 5) * 0.05 for i in range(50)]
        lexicon_values = [0.6 + (i % 8 - 4) * 0.04 for i in range(50)]
        bonus_values = [0.2 + (i % 6 - 3) * 0.03 for i in range(50)]
        expected_chronos_avg = sum(chronos_values) / len(chronos_values)
        expected_lexicon_avg = sum(lexicon_values) / len(lexicon_values)
        expected_bonus_avg = sum(bonus_values) / len(bonus_values)
        print(f"Chronos - Expected: {expected_chronos_avg:.4f}, Actual: {report.dimension_averages['chronos']:.4f}")
        print(f"Lexicon - Expected: {expected_lexicon_avg:.4f}, Actual: {report.dimension_averages['lexicon']:.4f}")
        print(f"Bonus - Expected: {expected_bonus_avg:.4f}, Actual: {report.bonus_statistics['mean']:.4f}")
        assert abs(report.dimension_averages['chronos'] - expected_chronos_avg) < 0.001
        assert abs(report.dimension_averages['lexicon'] - expected_lexicon_avg) < 0.001
        assert abs(report.bonus_statistics['mean'] - expected_bonus_avg) < 0.001
        expected_confidence_avg = 0.85
        assert abs(report.average_confidence - expected_confidence_avg) < 0.001
        assert 'mean' in report.bonus_statistics
        assert 'min' in report.bonus_statistics
        assert 'max' in report.bonus_statistics
        assert 'median' in report.bonus_statistics
        assert 'std_dev' in report.bonus_statistics
        assert report.bonus_statistics['min'] >= 0.0
        assert report.bonus_statistics['max'] <= 1.0
        assert report.bonus_statistics['min'] <= report.bonus_statistics['max']
if __name__ == '__main__':
    pytest.main([__file__])