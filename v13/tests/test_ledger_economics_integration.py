"""
Tests for ledger economics service integration
"""
import pytest
from v13.guards.AEGISGuard import AEGISGuard
from v13.services.ledger_economics_service import LedgerEconomicsService
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import TokenStateBundle

class TestLedgerEconomicsIntegration:
    """Test suite for ledger economics service integration"""

    def test_aegis_with_ledger_economics_service(self):
        """Test that AEGIS uses real economics data when service is available"""
        cm = CertifiedMath()
        aegis_guard = AEGISGuard(cm)
        chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
        parameters = {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128.from_int(1618033988749894848)}
        token_bundle = TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, nod_state={'nod_metric': '0.5'}, signature='test_signature', timestamp=1234567890, bundle_id='test_bundle_id', pqc_cid='test_pqc_cid', quantum_metadata={'test': 'data'}, lambda1=BigNum128.from_int(300000000000000000), lambda2=BigNum128.from_int(200000000000000000), c_crit=BigNum128.from_int(900000000000000000), parameters=parameters)
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'like', 'content': 'This is a test comment'}
        observation1 = aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=token_bundle, deterministic_timestamp=1234567890)
        economics_result1 = observation1.economics_guard_result
        assert economics_result1 is not None
        assert economics_result1['passed'] is True
        fake_ledger_economics = LedgerEconomicsService()
        aegis_guard.set_ledger_economics_service(fake_ledger_economics)
        observation2 = aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=token_bundle, deterministic_timestamp=1234567891)
        economics_result2 = observation2.economics_guard_result
        assert economics_result2 is not None
        assert economics_result2['passed'] is True
        assert hasattr(aegis_guard, 'ledger_economics_service')
        assert aegis_guard.ledger_economics_service is not None

    def test_aegis_ledger_economics_service_fallback(self):
        """Test that AEGIS falls back to demo values when service fails"""
        cm = CertifiedMath()
        aegis_guard = AEGISGuard(cm)
        chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
        parameters = {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128.from_int(1618033988749894848)}
        token_bundle = TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, nod_state={'nod_metric': '0.5'}, signature='test_signature', timestamp=1234567890, bundle_id='test_bundle_id', pqc_cid='test_pqc_cid', quantum_metadata={'test': 'data'}, lambda1=BigNum128.from_int(300000000000000000), lambda2=BigNum128.from_int(200000000000000000), c_crit=BigNum128.from_int(900000000000000000), parameters=parameters)

        class FailingLedgerEconomicsService:

            def get_chr_daily_totals(self):
                raise Exception('Service unavailable')

            def get_chr_total_supply(self):
                raise Exception('Service unavailable')
        failing_service = FailingLedgerEconomicsService()
        aegis_guard.set_ledger_economics_service(failing_service)
        interaction_inputs = {'user_id': 'test_user', 'target_id': 'test_target', 'interaction_type': 'like', 'content': 'This is a test comment'}
        observation = aegis_guard.observe_event(event_type='social_interaction', inputs=interaction_inputs, token_bundle=token_bundle, deterministic_timestamp=1234567890)
        economics_result = observation.economics_guard_result
        assert economics_result is not None
        assert economics_result['passed'] is True
if __name__ == '__main__':
    pytest.main([__file__])