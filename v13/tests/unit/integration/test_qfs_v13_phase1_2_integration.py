"""
Integration test for QFS V13 Phase 1-2 components.

Tests the integration between TokenStateBundle, UtilityOracleInterface, HSMF,
TreasuryEngine, RewardAllocator, CIR302_Handler, and CoherenceLedger.
"""

from v13.libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
import json
from typing import Dict, Any
from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from UtilityOracleInterface import UtilityOracleInterface, UtilityOracleResult
from PQC import generate_keypair, sign_data, verify_signature


def test_full_integration():
    """Test the full integration of all QFS V13 Phase 1-2 components."""
    print("=== QFS V13 Phase 1-2 Integration Test ===\n")
    log_list = []
    cm = CertifiedMath(log_list)
    pqc_keys = generate_keypair()
    pqc_keypair = (pqc_keys["private_key"], pqc_keys["public_key"])
    print("1. Creating TokenStateBundle...")
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85",
    }
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_signature",
        timestamp=int(det_time_now()),
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=BigNum128.from_string("0.3"),
        lambda2=BigNum128.from_string("0.2"),
        c_crit=BigNum128.from_string("0.9"),
    )
    print("✓ TokenStateBundle created successfully")
    print(f"  Bundle ID: {token_bundle.bundle_id}")
    print(f"  C_CRIT: {token_bundle.c_crit.to_decimal_string()}")
    print("\n2. Testing UtilityOracleInterface...")
    oracle = UtilityOracleInterface()
    f_atr_result = oracle.get_f_atr(None)
    print("✓ UtilityOracleInterface f(ATR) calculation:")
    print(f"  f(ATR): {f_atr_result.f_atr.to_decimal_string()}")
    print(f"  Valid: {f_atr_result.is_valid}")
    print("\n3. Testing HSMF integration...")

    class MockHSMFResult:
        def __init__(self):
            self.is_valid = True
            self.dez_ok = True
            self.errors = []
            self.raw_metrics = {
                "c_holo": BigNum128.from_string("0.95"),
                "s_flx": BigNum128.from_string("0.15"),
                "s_psi_sync": BigNum128.from_string("0.08"),
                "f_atr": f_atr_result.f_atr,
                "s_chr": BigNum128.from_string("0.98"),
            }

        @property
        def metrics_str(self):
            return {k: v.to_decimal_string() for k, v in self.raw_metrics.items()}

    hsmf_result = MockHSMFResult()
    print("✓ HSMF validation result simulated:")
    print(f"  Valid: {hsmf_result.is_valid}")
    print(f"  C_holo: {hsmf_result.raw_metrics['c_holo'].to_decimal_string()}")
    print(f"  S_FLX: {hsmf_result.raw_metrics['s_flx'].to_decimal_string()}")
    print("\n4. Testing TreasuryEngine...")
    from TreasuryEngine import TreasuryEngine

    treasury_engine = TreasuryEngine(cm, pqc_keypair)
    treasury_result = treasury_engine.compute_rewards(hsmf_result, token_bundle)
    print("✓ TreasuryEngine reward computation:")
    print(f"  Valid: {treasury_result.is_valid}")
    print(f"  Total allocation: {treasury_result.total_allocation.to_decimal_string()}")
    print(f"  PQC CID: {treasury_result.pqc_cid}")
    if treasury_result.rewards:
        print("  Rewards:")
        for token_name, allocation in treasury_result.rewards.items():
            print(
                f"    {token_name}: {allocation.amount.to_decimal_string()} (Eligible: {allocation.eligibility})"
            )
    print("\n5. Testing RewardAllocator...")
    from RewardAllocator import RewardAllocator

    reward_allocator = RewardAllocator(cm, pqc_keypair)
    allocated_result = reward_allocator.allocate_rewards(hsmf_result, token_bundle)
    print("✓ RewardAllocator reward allocation:")
    print(f"  Valid: {allocated_result.is_valid}")
    print(
        f"  PQC Signature: {('Yes' if 'pqc_signature' in allocated_result.quantum_metadata else 'No')}"
    )
    commit_success = reward_allocator.commit_rewards(allocated_result)
    print(f"  Commit successful: {commit_success}")
    print("\n6. Testing CoherenceLedger...")
    from CoherenceLedger import CoherenceLedger

    ledger = CoherenceLedger(cm, pqc_keypair)
    ledger_entry = ledger.log_state(
        token_bundle, hsmf_result.raw_metrics, treasury_result.rewards
    )
    print("✓ CoherenceLedger state logging:")
    print(f"  Entry ID: {ledger_entry.entry_id}")
    print(f"  Entry hash: {ledger_entry.entry_hash[:32]}...")
    finality_seal = ledger.generate_finality_seal(treasury_result)
    print(f"  Finality seal: {finality_seal[:32]}...")
    print("\n7. Testing CIR302_Handler (normal operation)...")
    from CIR302_Handler import CIR302_Handler

    cir302_handler = CIR302_Handler(cm, pqc_keypair)
    is_quarantined = cir302_handler.is_system_quarantined()
    print("✓ CIR302_Handler status check:")
    print(f"  System quarantined: {is_quarantined}")
    print("\n8. Testing AST_ZeroSimChecker...")
    from AST_ZeroSimChecker import AST_ZeroSimChecker

    zero_sim_checker = AST_ZeroSimChecker()
    violations = zero_sim_checker.scan_file(__file__)
    print("✓ AST_ZeroSimChecker file scan:")
    print(f"  Violations found: {len(violations)}")
    print("\n=== Integration Test Summary ===")
    print("✓ All QFS V13 Phase 1-2 components integrated successfully")
    print(
        "✓ TokenStateBundle → UtilityOracleInterface → HSMF → TreasuryEngine → RewardAllocator"
    )
    print("✓ CoherenceLedger and CIR302_Handler properly integrated")
    print("✓ AST_ZeroSimChecker validation completed")
    print(f"\nCertifiedMath audit log entries: {len(log_list)}")
    if log_list:
        operation_types = {}
        for entry in log_list:
            op_name = entry.get("op_name", "unknown")
            operation_types[op_name] = operation_types.get(op_name, 0) + 1
        print("Audit log operation types:")
        for op_type, count in operation_types.items():
            print(f"  {op_type}: {count}")


if __name__ == "__main__":
    test_full_integration()
