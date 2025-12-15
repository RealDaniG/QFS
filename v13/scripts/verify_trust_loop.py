
import asyncio
import json
import os
import sys
from datetime import datetime

# Adjust path to find v13 modules
# sys.path.append(os.path.join(os.getcwd()))
# Ensure we can import from v13 root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

from v13.ledger.genesis_ledger import GenesisLedger, GenesisEntry
from v13.ATLAS.src.security.wallet_id import wallet_to_user_id
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.CoherenceEngine import CoherenceEngine
from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle

async def verify_trust_loop():
    print(">> Starting Phase 2.5 Trust Loop Validation...")
    
    # 1. Setup
    ledger_file = "trust_loop_ledger.jsonl"
    if os.path.exists(ledger_file):
        os.remove(ledger_file)
    
    ledger = GenesisLedger(filepath=ledger_file)
    print(f"   [Setup] Ledger initialized at {ledger_file}")

    # 2. Actors
    alice_wallet = "0xAlice1234567890abcdef1234567890abcdef12"
    bob_wallet = "0xBob9876543210FEDCBA09876543210FEDCBA98"
    
    alice_id = wallet_to_user_id(alice_wallet)
    bob_id = wallet_to_user_id(bob_wallet)
    print(f"   [Identity] Alice ID: {alice_id}")
    print(f"   [Identity] Bob ID: {bob_id}")

    # 3. Execution Flow
    
    # Step A: Alice Logs In
    print("   [Step A] Alice Logs In...")
    entry_login_a = GenesisEntry(
        wallet=alice_wallet,
        event_type="LOGIN",
        value=0,
        metadata={"user_id": alice_id, "action": "connect"}
    )
    await ledger.append(entry_login_a)
    
    # Step B: Alice Creates Referral Code (Implicit)
    ref_code = alice_id 
    
    # Step C: Bob Joins with Referral
    print(f"   [Step C] Bob Joins with Ref Code: {ref_code}...")
    entry_login_b = GenesisEntry(
        wallet=bob_wallet,
        event_type="LOGIN",
        value=0,
        metadata={"user_id": bob_id, "referred_by": ref_code}
    )
    await ledger.append(entry_login_b)
    
    # Step D: System Logs Referral Event
    print("   [Step D] Logging REFERRAL_USE...")
    entry_ref = GenesisEntry(
        wallet=bob_wallet, # The actor
        event_type="REFERRAL_USE",
        value=0,
        metadata={
            "referrer_wallet": alice_wallet, 
            "referral_code": ref_code,
            "program_id": "v1_beta"
        }
    )
    await ledger.append(entry_ref)
    
    # Step E: Chat Interaction (Alice -> Bob)
    print("   [Step E] Alice Sends Message to Bob...")
    msg_hash = "sha256_of_ciphertext" 
    entry_msg = GenesisEntry(
        wallet=alice_wallet,
        event_type="MESSAGE",
        value=0,
        metadata={
            "recipient_wallet": bob_wallet,
            "msg_hash": msg_hash,
            "size_bytes": 128
        }
    )
    await ledger.append(entry_msg)
    
    # Step F: Reward Trigger (Simulated Coherence Update)
    # Using 'REFERRAL_REWARDED' to match CoherenceEngine expectation
    print("   [Step F] Triggering Reward for Referral...")
    entry_reward = GenesisEntry(
        wallet=alice_wallet, # Referrer gets reward
        event_type="REFERRAL_REWARDED",
        value=10.0, # +100 FLX (scalled later) - Wait, TokenStateBundle expects BigNum128
        metadata={
            "reason": "referral_bonus",
            "source_event": "prev_hash",
            "referrer_wallet": alice_wallet, # Needed by CoherenceEngine
            "token_type": "FLX",
            "amount_scaled": 10_000_000_000 # 100 FLX
        }
    )
    await ledger.append(entry_reward)
    
    # 4. Verification
    print(">> Verifying Ledger Integrity...")
    
    events = []
    with open(ledger_file, 'r') as f:
        for line in f:
            events.append(json.loads(line))
            
    # Checks
    assert len(events) == 5, f"Expected 5 events, found {len(events)}"
    assert events[4]['event_type'] == 'REFERRAL_REWARDED'
    
    print("   [Check] Event Sequence: OK")
    
    # 5. Coherence Loop Verification (L-002)
    print(">> Verifying Coherence State (L-002)...")
    
    # Initialize Engine
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
        engine = CoherenceEngine(cm)
        
        # Initial Bundle
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
            timestamp=int(datetime.utcnow().timestamp())
        )
        
        # Adapt Genesis Events to Engine Events
        engine_events = []
        for e in events:
            # We only care about REFERRAL_REWARDED for now as logic is sparse
            if e['event_type'] == 'REFERRAL_REWARDED':
                
                # Create a simple object to mimic the event class
                class AdapterEvent:
                    pass
                evt = AdapterEvent()
                evt.event_type = 'REFERRAL_REWARDED'
                evt.referrer_wallet = e['metadata'].get('referrer_wallet', e['wallet'])
                evt.amount_scaled = e['metadata'].get('amount_scaled', 0)
                evt.token_type = e['metadata'].get('token_type', 'FLX')
                engine_events.append(evt)
        
        # Run Transition
        new_bundle = engine.apply_hsmf_transition(
            current_bundle=bundle,
            log_list=log_list,
            processed_events=engine_events
        )
        
        # Assert Alice Balance
        # Alice is the referrer
        # Reward was 100 FLX (10_000_000_000)
        
        alice_bal = new_bundle.flx_state.get(alice_wallet)
        print(f"   [State] Alice FLX: {alice_bal}")
        
        expected = BigNum128.from_int(10_000_000_000)
        
        assert alice_bal is not None, "Alice should have a balance entry"
        # Assuming BigNum128 equality works or comparing string/fields
        # cm.eq(alice_bal, expected, ...)
        
        # Simple check using internal value if exposed, or string rep
        val_str = str(alice_bal) # Should be readable representation
        exp_str = str(expected)
        
        # Since BigNum128 logic might vary, let's strictly check value
        assert alice_bal.value == expected.value, f"Balance Mismatch: Got {alice_bal.value}, Expected {expected.value}"
        
        print(f"   [Check] Alice Balance Correct: {alice_bal.to_decimal_string()} FLX (scaled)")

    print("[SUCCESS] V1 Minimal Trust Loop Verified (L-001 & L-002)!")

if __name__ == "__main__":
    asyncio.run(verify_trust_loop())
