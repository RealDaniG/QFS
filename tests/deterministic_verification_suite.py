"""
Deterministic Verification Test Suite for QFS V13
Implements byte-for-byte matching tests to ensure Zero-Simulation compliance
"""

import json
import hashlib
import sys
import os
from typing import List, Dict, Any

# Try to import directly first, then add path if needed
try:
    from CertifiedMath import BigNum128, CertifiedMath
    from PQC import PQC
    from HSMF import HSMF, ValidationResult
    from DRV_Packet import DRV_Packet
    from TokenStateBundle import TokenStateBundle, create_token_state_bundle
    from CIR302_Handler import CIR302_Handler, QuarantineResult
except ImportError:
    # Add the libs directory to the path
    libs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libs'))
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)
    
    # Import all QFS V13 components
    from CertifiedMath import BigNum128, CertifiedMath
    from PQC import PQC
    from HSMF import HSMF, ValidationResult
    from DRV_Packet import DRV_Packet
    from TokenStateBundle import TokenStateBundle, create_token_state_bundle
    from CIR302_Handler import CIR302_Handler, QuarantineResult

# Define missing dataclasses for compatibility
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    dez_ok: bool
    survival_ok: bool
    errors: List[str]
    raw_metrics: Dict[str, BigNum128]

@dataclass
class QuarantineResult:
    is_quarantined: bool
    reason: str
    system_state: Dict[str, Any]
    finality_seal: str
    timestamp: int
    pqc_cid: str

def deterministic_hash(data: Any) -> str:
    """Generate deterministic SHA-256 hash of data."""
    if isinstance(data, str):
        serialized = data
    else:
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def test_certifiedmath_determinism() -> Dict[str, str]:
    """Test CertifiedMath deterministic operations."""
    print("Testing CertifiedMath deterministic operations...")
    
    results = {}
    
    # Test basic arithmetic operations
    with CertifiedMath.LogContext() as log1:
        a = BigNum128.from_int(2)
        b = BigNum128.from_int(3)
        result_add = CertifiedMath.add(a, b, log1)
        results["add"] = result_add.to_decimal_string()
    
    with CertifiedMath.LogContext() as log2:
        a = BigNum128.from_int(2)
        b = BigNum128.from_int(3)
        result_add = CertifiedMath.add(a, b, log2)
        results["add_replay"] = result_add.to_decimal_string()
    
    # Test transcendental functions
    with CertifiedMath.LogContext() as log3:
        x = CertifiedMath.from_string("1.5")
        result_exp = CertifiedMath.safe_exp(x, log3, iterations=20)
        results["exp"] = result_exp.to_decimal_string()
    
    with CertifiedMath.LogContext() as log4:
        x = CertifiedMath.from_string("1.5")
        result_exp = CertifiedMath.safe_exp(x, log4, iterations=20)
        results["exp_replay"] = result_exp.to_decimal_string()
    
    # Test logarithm function
    with CertifiedMath.LogContext() as log5:
        x = BigNum128.from_int(2)
        result_ln = CertifiedMath.safe_ln(x, log5, iterations=20)
        results["ln"] = result_ln.to_decimal_string()
    
    with CertifiedMath.LogContext() as log6:
        x = BigNum128.from_int(2)
        result_ln = CertifiedMath.safe_ln(x, log6, iterations=20)
        results["ln_replay"] = result_ln.to_decimal_string()
    
    # Test power function
    with CertifiedMath.LogContext() as log7:
        base = BigNum128.from_int(2)
        exp_val = CertifiedMath.from_string("1.5")
        result_pow = CertifiedMath.safe_pow(base, exp_val, log7, iterations=20)
        results["pow"] = result_pow.to_decimal_string()
    
    with CertifiedMath.LogContext() as log8:
        base = BigNum128.from_int(2)
        exp_val = CertifiedMath.from_string("1.5")
        result_pow = CertifiedMath.safe_pow(base, exp_val, log8, iterations=20)
        results["pow_replay"] = result_pow.to_decimal_string()
    
    # Verify deterministic behavior
    assert results["add"] == results["add_replay"], "Addition is not deterministic"
    assert results["exp"] == results["exp_replay"], "Exponential is not deterministic"
    assert results["ln"] == results["ln_replay"], "Natural log is not deterministic"
    assert results["pow"] == results["pow_replay"], "Power function is not deterministic"
    
    print("✅ CertifiedMath deterministic operations verified")
    return results

def test_pqc_determinism() -> Dict[str, str]:
    """Test PQC deterministic operations."""
    print("Testing PQC deterministic operations...")
    
    results = {}
    
    # Test deterministic key generation with seed
    seed = b"deterministic_test_seed_12345"
    
    with PQC.LogContext() as log1:
        keypair1 = PQC.generate_keypair(
            log_list=log1,
            seed=seed,
            deterministic_timestamp=1234567890
        )
        results["keypair1_pub"] = keypair1.public_key.hex()
        results["keypair1_priv_len"] = str(len(keypair1.private_key))
    
    with PQC.LogContext() as log2:
        keypair2 = PQC.generate_keypair(
            log_list=log2,
            seed=seed,
            deterministic_timestamp=1234567890
        )
        results["keypair2_pub"] = keypair2.public_key.hex()
        results["keypair2_priv_len"] = str(len(keypair2.private_key))
    
    # Test deterministic signing
    data = {"test": "data", "value": "123.45"}
    
    with PQC.LogContext() as log3:
        signature1 = PQC.sign_data(
            keypair1.private_key,
            data,
            log_list=log3,
            deterministic_timestamp=1234567891
        )
        results["signature1"] = signature1.hex()
    
    with PQC.LogContext() as log4:
        signature2 = PQC.sign_data(
            keypair1.private_key,
            data,
            log_list=log4,
            deterministic_timestamp=1234567891
        )
        results["signature2"] = signature2.hex()
    
    # Verify deterministic behavior
    assert results["keypair1_pub"] == results["keypair2_pub"], "Key generation is not deterministic"
    assert results["signature1"] == results["signature2"], "Signature generation is not deterministic"
    
    print("✅ PQC deterministic operations verified")
    return results

def test_drv_packet_determinism() -> Dict[str, str]:
    """Test DRV_Packet deterministic operations."""
    print("Testing DRV_Packet deterministic operations...")
    
    results = {}
    
    # Test deterministic packet creation
    packet1 = DRV_Packet(
        ttsTimestamp=1700000000,
        sequence=1,
        seed="test_seed_123",
        metadata={"source": "test"},
        previous_hash="0" * 64
    )
    results["packet1_hash"] = packet1.get_hash()
    
    packet2 = DRV_Packet(
        ttsTimestamp=1700000000,
        sequence=1,
        seed="test_seed_123",
        metadata={"source": "test"},
        previous_hash="0" * 64
    )
    results["packet2_hash"] = packet2.get_hash()
    
    # Test deterministic serialization
    serialized1 = packet1.serialize()
    serialized2 = packet2.serialize()
    results["serialized_match"] = str(serialized1 == serialized2)
    
    # Verify deterministic behavior
    assert results["packet1_hash"] == results["packet2_hash"], "Packet creation is not deterministic"
    assert serialized1 == serialized2, "Packet serialization is not deterministic"
    
    print("✅ DRV_Packet deterministic operations verified")
    return results

def test_token_state_bundle_determinism() -> Dict[str, str]:
    """Test TokenStateBundle deterministic operations."""
    print("Testing TokenStateBundle deterministic operations...")
    
    results = {}
    
    # Test deterministic bundle creation
    chr_state = {"coherence_metric": "0.95"}
    flx_state = {"scaling_metric": "0.15"}
    psi_sync_state = {"frequency_metric": "0.08"}
    atr_state = {"directional_metric": "0.85"}
    res_state = {"inertial_metric": "0.05"}
    
    lambda1 = BigNum128.from_int(2)
    lambda2 = BigNum128.from_int(3)
    c_crit = BigNum128.from_int(1)
    
    bundle1 = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=lambda1,
        lambda2=lambda2,
        c_crit=c_crit,
        pqc_cid="test_001",
        timestamp=1700000000
    )
    results["bundle1_hash"] = bundle1.get_deterministic_hash()
    
    bundle2 = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=lambda1,
        lambda2=lambda2,
        c_crit=c_crit,
        pqc_cid="test_001",
        timestamp=1700000000
    )
    results["bundle2_hash"] = bundle2.get_deterministic_hash()
    
    # Test deterministic serialization
    serialized1 = bundle1.serialize_for_hash()
    serialized2 = bundle2.serialize_for_hash()
    results["bundle_serialized_match"] = str(serialized1 == serialized2)
    
    # Verify deterministic behavior
    assert results["bundle1_hash"] == results["bundle2_hash"], "Bundle creation is not deterministic"
    assert serialized1 == serialized2, "Bundle serialization is not deterministic"
    
    print("✅ TokenStateBundle deterministic operations verified")
    return results

def test_hsmf_determinism() -> Dict[str, str]:
    """Test HSMF deterministic operations."""
    print("Testing HSMF deterministic operations...")
    
    results = {}
    
    # Create test token bundle
    chr_state = {"coherence_metric": "0.95"}
    flx_state = {"scaling_metric": "0.15", "magnitudes": ["1.0", "1.1", "1.2"]}
    psi_sync_state = {"frequency_metric": "0.08", "current_sequence": "10"}
    atr_state = {"directional_metric": "0.85", "atr_magnitude": "0.1"}
    res_state = {"inertial_metric": "0.05"}
    
    lambda1 = BigNum128.from_int(2)
    lambda2 = BigNum128.from_int(3)
    c_crit = BigNum128.from_int(1)
    
    bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=lambda1,
        lambda2=lambda2,
        c_crit=c_crit,
        pqc_cid="test_001",
        timestamp=1700000000
    )
    
    # Convert string values to BigNum128
    for key in bundle.chr_state:
        if isinstance(bundle.chr_state[key], str):
            bundle.chr_state[key] = CertifiedMath.from_string(bundle.chr_state[key])
    
    for key in bundle.flx_state:
        if isinstance(bundle.flx_state[key], str):
            bundle.flx_state[key] = CertifiedMath.from_string(bundle.flx_state[key])
        elif isinstance(bundle.flx_state[key], list):
            bundle.flx_state[key] = [CertifiedMath.from_string(item) if isinstance(item, str) else item for item in bundle.flx_state[key]]
    
    for key in bundle.psi_sync_state:
        if isinstance(bundle.psi_sync_state[key], str):
            bundle.psi_sync_state[key] = CertifiedMath.from_string(bundle.psi_sync_state[key])
    
    for key in bundle.atr_state:
        if isinstance(bundle.atr_state[key], str):
            bundle.atr_state[key] = CertifiedMath.from_string(bundle.atr_state[key])
    
    for key in bundle.res_state:
        if isinstance(bundle.res_state[key], str):
            bundle.res_state[key] = CertifiedMath.from_string(bundle.res_state[key])
    
    # Test HSMF validation
    cm = CertifiedMath  # Use the class directly since we don't need instance state
    hsmf = HSMF(cm)
    f_atr = CertifiedMath.from_string("0.05")
    
    with CertifiedMath.LogContext() as log1:
        result1 = hsmf.validate_action_bundle(
            token_bundle=bundle,
            f_atr=f_atr,
            drv_packet_sequence=10,
            log_list=log1
        )
        results["hsmf_result1_valid"] = str(result1.is_valid)
        results["hsmf_result1_dez"] = str(result1.dez_ok)
        results["hsmf_result1_survival"] = str(result1.survival_ok)
    
    with CertifiedMath.LogContext() as log2:
        result2 = hsmf.validate_action_bundle(
            token_bundle=bundle,
            f_atr=f_atr,
            drv_packet_sequence=10,
            log_list=log2
        )
        results["hsmf_result2_valid"] = str(result2.is_valid)
        results["hsmf_result2_dez"] = str(result2.dez_ok)
        results["hsmf_result2_survival"] = str(result2.survival_ok)
    
    # Verify deterministic behavior
    assert results["hsmf_result1_valid"] == results["hsmf_result2_valid"], "HSMF validation is not deterministic"
    assert results["hsmf_result1_dez"] == results["hsmf_result2_dez"], "HSMF DEZ check is not deterministic"
    assert results["hsmf_result1_survival"] == results["hsmf_result2_survival"], "HSMF survival check is not deterministic"
    
    print("✅ HSMF deterministic operations verified")
    return results

def run_deterministic_verification_suite() -> Dict[str, Dict[str, str]]:
    """Run the complete deterministic verification suite."""
    print("Running QFS V13 Deterministic Verification Suite")
    print("=" * 60)
    
    results = {}
    
    # Run all deterministic tests
    results["certifiedmath"] = test_certifiedmath_determinism()
    results["pqc"] = test_pqc_determinism()
    results["drv_packet"] = test_drv_packet_determinism()
    results["token_state_bundle"] = test_token_state_bundle_determinism()
    results["hsmf"] = test_hsmf_determinism()
    
    print("\n" + "=" * 60)
    print("✅ All deterministic verification tests passed!")
    print("✅ QFS V13 components are fully deterministic and replayable")
    
    # Generate overall verification hash
    verification_hash = deterministic_hash(results)
    print(f"Verification suite hash: {verification_hash[:32]}...")
    
    return results

if __name__ == "__main__":
    # Run the deterministic verification suite
    suite_results = run_deterministic_verification_suite()
    
    # Export results
    with open("deterministic_verification_results.json", "w") as f:
        json.dump(suite_results, f, indent=2)
    
    print("\nResults exported to deterministic_verification_results.json")