import json
import os
import sys
import datetime
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)
from v13.ledger.genesis_ledger import GenesisLedger, GenesisEntry
from v13.atlas.src.security.wallet_id import wallet_to_user_id
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.CoherenceEngine import CoherenceEngine
from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle


async def verify_trust_loop():
    print(">> Starting Phase 2.5 Trust Loop Validation...")
    ledger_file = "trust_loop_ledger.jsonl"
    if os.path.exists(ledger_file):
        os.remove(ledger_file)
    ledger = GenesisLedger(filepath=ledger_file)
    print(f"   [Setup] Ledger initialized at {ledger_file}")
    alice_wallet = "0xAlice1234567890abcdef1234567890abcdef12"
    bob_wallet = "0xBob9876543210FEDCBA09876543210FEDCBA98"
    alice_id = wallet_to_user_id(alice_wallet)
    bob_id = wallet_to_user_id(bob_wallet)
    print(f"   [Identity] Alice ID: {alice_id}")
    print(f"   [Identity] Bob ID: {bob_id}")
    print("   [Step A] Alice Logs In...")
    entry_login_a = GenesisEntry(
        wallet=alice_wallet,
        event_type="LOGIN",
        value=0,
        metadata={"user_id": alice_id, "action": "connect"},
    )
    await ledger.append(entry_login_a)
    ref_code = alice_id
    print(f"   [Step C] Bob Joins with Ref Code: {ref_code}...")
    entry_login_b = GenesisEntry(
        wallet=bob_wallet,
        event_type="LOGIN",
        value=0,
        metadata={"user_id": bob_id, "referred_by": ref_code},
    )
    await ledger.append(entry_login_b)
    print("   [Step D] Logging REFERRAL_USE...")
    entry_ref = GenesisEntry(
        wallet=bob_wallet,
        event_type="REFERRAL_USE",
        value=0,
        metadata={
            "referrer_wallet": alice_wallet,
            "referral_code": ref_code,
            "program_id": "v1_beta",
        },
    )
    await ledger.append(entry_ref)
    print("   [Step E] Alice Sends Message to Bob...")
    msg_hash = "sha256_of_ciphertext"
    entry_msg = GenesisEntry(
        wallet=alice_wallet,
        event_type="MESSAGE",
        value=0,
        metadata={
            "recipient_wallet": bob_wallet,
            "msg_hash": msg_hash,
            "size_bytes": 128,
        },
    )
    await ledger.append(entry_msg)
    print("   [Step F] Triggering Reward for Referral...")
    entry_reward = GenesisEntry(
        wallet=alice_wallet,
        event_type="REFERRAL_REWARDED",
        value=10,
        metadata={
            "reason": "referral_bonus",
            "source_event": "prev_hash",
            "referrer_wallet": alice_wallet,
            "token_type": "FLX",
            "amount_scaled": 10000000000,
        },
    )
    await ledger.append(entry_reward)
    print(">> Verifying Ledger Integrity...")
    events = []
    with open(ledger_file, "r") as f:
        for line in sorted(f):
            events.append(json.loads(line))
    assert len(events) == 5, f"Expected 5 events, found {len(events)}"
    assert events[4]["event_type"] == "REFERRAL_REWARDED"
    print("   [Check] Event Sequence: OK")
    print(">> Verifying Coherence State (L-002)...")
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
        engine = CoherenceEngine(cm)
        bundle = create_token_state_bundle(
            chr_state={},
            flx_state={},
            psi_sync_state={},
            atr_state={},
            res_state={},
            nod_state={},
            lambda1=BigNum128.from_int(1),
            lambda2=BigNum128.from_int(1),
            c_crit=BigNum128.from_int(1),
            pqc_cid="init_cid",
            timestamp=int(datetime.utcnow().timestamp()),
        )
        engine_events = []
        for e in sorted(events):
            if e["event_type"] == "REFERRAL_REWARDED":

                class AdapterEvent:
                    pass

                evt = AdapterEvent()
                evt.event_type = "REFERRAL_REWARDED"
                evt.referrer_wallet = e["metadata"].get("referrer_wallet", e["wallet"])
                evt.amount_scaled = e["metadata"].get("amount_scaled", 0)
                evt.token_type = e["metadata"].get("token_type", "FLX")
                engine_events.append(evt)
        new_bundle = engine.apply_hsmf_transition(
            current_bundle=bundle, log_list=log_list, processed_events=engine_events
        )
        alice_bal = new_bundle.flx_state.get(alice_wallet)
        print(f"   [State] Alice FLX: {alice_bal}")
        expected = BigNum128.from_int(10000000000)
        assert alice_bal is not None, "Alice should have a balance entry"
        val_str = str(alice_bal)
        exp_str = str(expected)
        assert alice_bal.value == expected.value, (
            f"Balance Mismatch: Got {alice_bal.value}, Expected {expected.value}"
        )
        print(
            f"   [Check] Alice Balance Correct: {alice_bal.to_decimal_string()} FLX (scaled)"
        )
    print("[SUCCESS] V1 Minimal Trust Loop Verified (L-001 & L-002)!")


if __name__ == "__main__":
    asyncio.run(verify_trust_loop())
