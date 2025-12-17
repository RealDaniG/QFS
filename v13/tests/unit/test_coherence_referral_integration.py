import pytest
from v13.core.CoherenceEngine import CoherenceEngine
from v13.core.TokenStateBundle import create_token_state_bundle
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.events.referral_events import ReferralRewarded

class TestCoherenceReferralIntegration:

    def test_referral_reward_application(self):
        """Test that CoherenceEngine correctly applies ReferralRewarded events to token state."""
        cm = CertifiedMath()
        engine = CoherenceEngine(cm)
        referrer_wallet = '0xReferrerWallet'
        initial_balance = '100.0'
        initial_bundle = create_token_state_bundle(chr_state={}, flx_state={referrer_wallet: BigNum128.from_string(initial_balance)}, psi_sync_state={}, atr_state={}, res_state={}, nod_state={}, lambda1=BigNum128.from_int(1), lambda2=BigNum128.from_int(1), c_crit=BigNum128.from_int(1), pqc_cid='test_cid', timestamp=1000)
        reward_amount_scaled = 10000000000
        event = ReferralRewarded(referrer_wallet=referrer_wallet, referee_wallet='0xReferee', token_type='FLX', amount_scaled=reward_amount_scaled, epoch=101, reason='Test Reward', guard_cir_code='PASS')
        log_list = []
        new_bundle = engine.apply_hsmf_transition(current_bundle=initial_bundle, log_list=log_list, pqc_cid='test_cid_2', deterministic_timestamp=1100, processed_events=[event])
        old_balance = initial_bundle.flx_state[referrer_wallet]
        new_balance = new_bundle.flx_state[referrer_wallet]
        expected_balance = cm.add(old_balance, BigNum128.from_int(reward_amount_scaled), [])
        assert new_balance.value == expected_balance.value
        assert new_balance.value > old_balance.value
        found_log = False
        for log in sorted(log_list):
            if log.get('op_name') == 'apply_referral_reward':
                if log.get('inputs', {}).get('wallet') == referrer_wallet:
                    found_log = True
                    break
        assert found_log, 'Referral reward application was not logged'