"""
Tests for AEGIS advisory gate functionality
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import pytest
from v13.guards.AEGISGuard import AEGISGuard
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import TokenStateBundle

class TestAEGISAdvisoryGate:
    """Test suite for AEGIS advisory gate functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.cm = CertifiedMath()
        self.aegis_guard = AEGISGuard(self.cm)
        chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
        parameters = {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128.from_int(1618033988749894848)}
        storage_metrics = {'storage_bytes_stored': {}, 'storage_uptime_bucket': {}, 'storage_proofs_verified': {}}
        self.token_bundle = TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, nod_state={'nod_metric': '0.5'}, storage_metrics=storage_metrics, signature='test_signature', timestamp=1234567890, bundle_id='test_bundle_id', pqc_cid='test_pqc_cid', quantum_metadata={'test': 'data'}, lambda1=BigNum128.from_int(300000000000000000), lambda2=BigNum128.from_int(200000000000000000), c_crit=BigNum128.from_int(900000000000000000), parameters=parameters)

    def test_safe_interaction_no_blocking_suggested(self):
        """Test that safe interactions do not suggest blocking"""
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'comment', 'content': 'This is a safe, family-friendly post about quantum computing.'}
        observation = self.aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567890)
        assert observation.block_suggested is False
        assert observation.severity == 'info'
        assert observation.safety_guard_result['passed'] is True
        assert observation.economics_guard_result['passed'] is True

    def test_unsafe_content_suggests_blocking(self):
        """Test that unsafe content suggests blocking with appropriate severity"""
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'comment', 'content': 'This is explicit adult content that should be flagged.'}
        observation = self.aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567891)
        assert observation.block_suggested is True
        assert observation.severity == 'critical'
        assert observation.safety_guard_result['passed'] is False
        assert qnum(observation.safety_guard_result['risk_score']) > 0.7

    def test_spam_content_suggests_blocking(self):
        """Test that spam content suggests blocking with appropriate severity"""
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'comment', 'content': 'Buy now! Click here for free money! Urgent limited time offer! Act now!'}
        observation = self.aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567892)
        assert observation.block_suggested is True
        assert observation.severity == 'warning'
        assert observation.safety_guard_result['passed'] is False
        risk_score = qnum(observation.safety_guard_result['risk_score'])
        assert 0.5 < risk_score <= 0.7

    def test_economic_violation_suggests_blocking(self):
        """Test that economic violations suggest blocking with appropriate severity"""

        class ViolatingLedgerEconomicsService:

            def get_chr_daily_totals(self):
                return {'current_daily_total': BigNum128.from_int(1000000000)}

            def get_chr_total_supply(self):
                return {'current_total_supply': BigNum128.from_int(1000000000000)}
        violating_service = ViolatingLedgerEconomicsService()
        self.aegis_guard.set_ledger_economics_service(violating_service)
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'like', 'content': 'This is a normal, safe comment.'}
        observation = self.aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567893)
        assert observation.block_suggested is True
        assert observation.severity == 'warning'
        assert observation.economics_guard_result['passed'] is False

    def test_feed_ranking_safe_content_no_blocking(self):
        """Test that safe feed ranking content does not suggest blocking"""
        feed_inputs = {'user_id': 'test_user', 'post_id': 'test_post', 'features': ['feature1', 'feature2'], 'coherence_score': '0.95', 'content': 'This is a safe, educational post about quantum physics.'}
        observation = self.aegis_guard.observe_event(event_type='feed_ranking', inputs=feed_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567894)
        assert observation.block_suggested is False
        assert observation.severity == 'info'
        assert observation.safety_guard_result['passed'] is True

    def test_feed_ranking_unsafe_content_suggests_blocking(self):
        """Test that unsafe feed ranking content suggests blocking"""
        feed_inputs = {'user_id': 'test_user', 'post_id': 'test_post', 'features': ['feature1', 'feature2'], 'coherence_score': '0.95', 'content': 'This post contains explicit adult material.'}
        observation = self.aegis_guard.observe_event(event_type='feed_ranking', inputs=feed_inputs, token_bundle=self.token_bundle, deterministic_timestamp=1234567895)
        assert observation.block_suggested is True
        assert observation.severity == 'critical'
        assert observation.safety_guard_result['passed'] is False
if __name__ == '__main__':
    pytest.main([__file__])