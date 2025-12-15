"""
init_creator.py - CLI command to initialize System Creator Wallet
"""
import asyncio
import json
import hashlib
import sys
import argparse
from typing import Dict, Any

# Adjust path to ensure we can import v13 modules if running purely as script
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from v13.libs.crypto.derivation import derive_creator_keypair
from v13.libs.keystore.manager import KeystoreManager
from v13.ledger.writer import LedgerWriter
from v13.ledger.genesis_ledger import GenesisLedger
from v13.policy.authorization import AuthorizationEngine

async def main():
    parser = argparse.ArgumentParser(description="Initialize System Creator Wallet")
    parser.add_argument("--scope", required=True, choices=["dev", "testnet", "DEV", "TESTNET"], help="Target environment scope")
    args = parser.parse_args()
    
    scope = args.scope.upper()
    
    # 1. Assert Scope
    if scope == "MAINNET":
        print("Error: MAINNET is not supported for init-creator.")
        sys.exit(1)

    # 2. Derive Wallet
    try:
        priv_key, pub_addr = derive_creator_keypair(scope)
    except Exception as e:
        print(f"Error during derivation: {e}")
        sys.exit(1)

    # 3. Store Key
    ks = KeystoreManager()
    
    # Check if already exists in keystore
    if ks.exists("SYSTEM_CREATOR", scope):
        # We might want to verify it matches or error.
        # Spec says "Refuse to run if ... Wallet already registered"
        # We can check keystore for "I already have this".
        # But maybe we just want to idempotently ensure it's there.
        # However, for safety, if keys exist, we shouldn't overwrite blindly or re-emit registration potentially.
        # Let's check if the stored public address matches.
        stored = ks.get_wallet("SYSTEM_CREATOR", scope)
        if stored and stored['public_address'] != pub_addr:
             print("Error: Wallet already registered with different keys.")
             sys.exit(1)
        # If it matches, we proceed? Or stop?
        # "Refuse to run if ... Wallet already registered"
        # I'll fail if it exists.
        print(f"Error: Wallet already registered in local keystore for {scope}.")
        sys.exit(1)

    try:
        ks.save_key("SYSTEM_CREATOR", scope, priv_key, pub_addr)
    except Exception as e:
        print(f"Error saving to keystore: {e}")
        sys.exit(1)

    # 4. Emit WALLET_REGISTERED
    writer = LedgerWriter()
    capabilities = [
        "LEDGER_READ_ALL",
        "LEDGER_WRITE_SYSTEM_EVENTS",
        "COHERENCE_OVERRIDE_TEST",
        "TREASURY_SIMULATION_ACCESS",
        "GOVERNANCE_PROPOSAL_CREATE",
        "GOVERNANCE_PROPOSAL_EXECUTE_TEST"
    ]
    
    # Check if ledger already has this?
    ledger = GenesisLedger()
    entries = ledger.read_all()
    already_registered = False
    for e in entries:
        if e.event_type == "WALLET_REGISTERED" and e.metadata.get("wallet_id") == pub_addr:
            already_registered = True
            break
            
    if not already_registered:
        try:
            await writer.emit_wallet_registered(pub_addr, "SYSTEM_CREATOR", scope, capabilities)
        except Exception as e:
            print(f"Error writing to ledger: {e}")
            sys.exit(1)
    
    # 5. Replay Ledger & Verify
    entries = ledger.read_all() # Re-read after write
    
    hashes = [e.hash for e in entries]
    # Simple integrity hash over the chain of hashes
    replay_hash = hashlib.sha256("".join(hashes).encode()).hexdigest()

    auth = AuthorizationEngine(entries)
    role = auth.resolve_role(pub_addr)
    
    # Check capabilities
    verified = True
    if role != "SYSTEM_CREATOR":
        verified = False
        
    if not auth.authorize(pub_addr, "LEDGER_READ_ALL", scope):
        verified = False

    verification_status = "PASS" if verified else "FAIL"
    
    # 6. Output JSON
    output = {
        "wallet_address": pub_addr,
        "role": role,
        "scope": scope,
        "replay_hash": replay_hash,
        "verification_status": verification_status
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
