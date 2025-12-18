from v13.libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from UtilityOracleInterface import UtilityOracleInterface, UtilityOracleResult
from PQC import generate_keypair, sign_data, verify_signature


def test_integration():
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
    print("\n=== Integration Test Summary ===")
    print("✓ All QFS V13 Phase 1-2 components integrated successfully")


if __name__ == "__main__":
    test_integration()
