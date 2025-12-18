import pytest
from v13.ledger.referral_ledger import ReferralLedger
from v13.core.CoherenceLedger import CoherenceLedger
from v13.libs.CertifiedMath import CertifiedMath
from v13.events.referral_events import ReferralRewarded

def test_referral_ledger_sync_flow():
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    coherence_ledger = CoherenceLedger(cm)
    referral_ledger = ReferralLedger(coherence_ledger)
    referrer = 'wallet_referrer_123'
    referee = 'wallet_referee_456'
    epoch = 101
    code = referral_ledger.create_link(referrer, epoch, 'test_source')
    assert code is not None
    assert len(coherence_ledger.ledger_entries) == 1
    assert coherence_ledger.ledger_entries[0].entry_type == 'REFERRAL_CREATED'
    referral_ledger._resolve_code = lambda c: referrer if c == code else None
    referral_ledger.accept(code, referee, epoch, 'device_hash_abc')
    assert len(coherence_ledger.ledger_entries) == 2
    assert coherence_ledger.ledger_entries[1].entry_type == 'REFERRAL_ACCEPTED'
    referral_ledger._count_referrals = lambda w: 0
    referral_ledger._get_pending_referral = lambda w: {'referrer': referrer, 'code': code}
    referral_ledger.activate(referee, 'PROFILE_COMPLETE', epoch)
    assert len(coherence_ledger.ledger_entries) == 4
    assert coherence_ledger.ledger_entries[2].entry_type == 'REFERRAL_ACTIVATED'
    assert coherence_ledger.ledger_entries[3].entry_type == 'REFERRAL_REWARDED'
    reward_entry = coherence_ledger.ledger_entries[3]
    event_data = reward_entry.data['event_data']
    assert event_data['amount_scaled'] == 10000000000
    assert event_data['referrer_wallet'] == referrer
if __name__ == '__main__':
    test_referral_ledger_sync_flow()
