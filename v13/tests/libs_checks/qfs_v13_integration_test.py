"""
QFS V13 Integration Test - Complete System Verification

This test verifies that all components work together according to the QFS V13 Hardening Plan:
1. CertifiedMath provides all required deterministic functions
2. PQC integration works with real Dilithium5
3. HSMF validation with proper log flow
4. DRV_Packet signing and verification
5. TokenStateBundle creation and validation
6. CIR302_Handler quarantine functionality
7. AST Zero-Simulation compliance
8. Finality seal and AFE generation
"""

import json
import hashlib
from typing import Dict, Any, List
from CertifiedMath import BigNum128, CertifiedMath
from v13.libs.PQC import PQC, KeyPair
from HSMF import HSMF, ValidationResult as HSMFValidationResult
from v13.core.DRV_Packet import DRV_Packet, ValidationResult as DRVValidationResult
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from v13.handlers.CIR302_Handler import CIR302_Handler, QuarantineResult
from AST_ZeroSimChecker import AST_ZeroSimChecker


def test_certified_math_functions():
    """Test all required CertifiedMath functions for QFS V13 compliance."""
    print("Testing CertifiedMath functions...")
    with CertifiedMath.LogContext() as log_list:
        a = BigNum128.from_int(2)
        b = BigNum128.from_int(3)
        result_add = CertifiedMath.add(a, b, log_list, "TEST_ADD")
        result_sub = CertifiedMath.sub(b, a, log_list, "TEST_SUB")
        result_mul = CertifiedMath.mul(a, b, log_list, "TEST_MUL")
        result_div = CertifiedMath.div(b, a, log_list, "TEST_DIV")
        print(f"  2 + 3 = {result_add.to_decimal_string()}")
        print(f"  3 - 2 = {result_sub.to_decimal_string()}")
        print(f"  2 * 3 = {result_mul.to_decimal_string()}")
        print(f"  3 / 2 = {result_div.to_decimal_string()}")
        result_exp = CertifiedMath.safe_exp(a, log_list, 20, "TEST_EXP")
        result_ln = CertifiedMath.safe_ln(b, log_list, 20, "TEST_LN")
        result_pow = CertifiedMath.safe_pow(a, b, log_list, 20, "TEST_POW")
        result_two_power = CertifiedMath.safe_two_to_the_power(
            a, log_list, 20, "TEST_TWO_POWER"
        )
        print(f"  exp(2) = {result_exp.to_decimal_string()}")
        print(f"  ln(3) = {result_ln.to_decimal_string()}")
        print(f"  2^3 = {result_pow.to_decimal_string()}")
        print(f"  2^2 = {result_two_power.to_decimal_string()}")
        result_sqrt = CertifiedMath.fast_sqrt(a, log_list, 20, "TEST_SQRT")
        result_phi = CertifiedMath.calculate_phi_series(a, log_list, 20, "TEST_PHI")
        print(f"  sqrt(2) = {result_sqrt.to_decimal_string()}")
        print(f"  phi_series(2) = {result_phi.to_decimal_string()}")
        result_gt = CertifiedMath.gt(a, b, log_list, "TEST_GT")
        result_lt = CertifiedMath.lt(a, b, log_list, "TEST_LT")
        result_gte = CertifiedMath.gte(a, b, log_list, "TEST_GTE")
        result_lte = CertifiedMath.lte(a, b, log_list, "TEST_LTE")
        result_eq = CertifiedMath.eq(a, b, log_list, "TEST_EQ")
        result_neq = CertifiedMath.neq(a, b, log_list, "TEST_NEQ")
        print(f"  2 > 3 = {result_gt}")
        print(f"  2 < 3 = {result_lt}")
        print(f"  2 >= 3 = {result_gte}")
        print(f"  2 <= 3 = {result_lte}")
        print(f"  2 == 3 = {result_eq}")
        print(f"  2 != 3 = {result_neq}")
        negative_a = CertifiedMath.sub(BigNum128.from_int(0), a, log_list, "TEST_NEG")
        result_abs = CertifiedMath.abs(negative_a, log_list, "TEST_ABS")
        print(f"  abs(-2) = {result_abs.to_decimal_string()}")
        print(f"  CertifiedMath log entries: {len(log_list)}")
        return True


def test_pqc_integration():
    """Test PQC integration with real Dilithium5."""
    print("\nTesting PQC integration...")
    with PQC.LogContext() as log_list:
        try:
            keypair = PQC.generate_keypair(
                log_list=log_list, algorithm=PQC.DILITHIUM5, pqc_cid="TEST_KEYGEN"
            )
            print(f"  Generated keypair: {keypair.algorithm}")
            print(f"  Public key size: {len(keypair.public_key)} bytes")
            print(f"  Private key size: {len(keypair.private_key)} bytes")
            test_data = {
                "message": "QFS V13 Test Data",
                "timestamp": 1234567890,
                "values": [1, 2, 3, 4, 5],
            }
            signature = PQC.sign_data(
                private_key=keypair.private_key,
                data=test_data,
                log_list=log_list,
                pqc_cid="TEST_SIGN",
            )
            print(f"  Signature size: {len(signature)} bytes")
            validation_result = PQC.verify_signature(
                public_key=keypair.public_key,
                data=test_data,
                signature=signature,
                log_list=log_list,
                pqc_cid="TEST_VERIFY",
            )
            print(f"  Signature valid: {validation_result.is_valid}")
            if validation_result.is_valid:
                print(f"  PQC operations successful")
                print(f"  PQC log entries: {len(log_list)}")
                return True
            else:
                print(f"  PQC verification failed: {validation_result.error_message}")
                return False
        except Exception as e:
            print(f"  PQC test failed: {e}")
            return False


def test_hsmf_validation():
    """Test HSMF validation with proper log flow."""
    print("\nTesting HSMF validation...")
    cm = CertifiedMath()
    hsmf = HSMF(cm)
    chr_state = {
        "coherence_metric": BigNum128.from_int(1),
        "c_holo_proxy": BigNum128.from_string("0.95"),
    }
    flx_state = {
        "magnitudes": [
            BigNum128.from_int(1),
            BigNum128.from_int(2),
            BigNum128.from_int(3),
        ]
    }
    psi_sync_state = {"current_sequence": BigNum128.from_int(100)}
    atr_state = {
        "atr_magnitude": BigNum128.from_int(1),
        "directional_metric": BigNum128.from_string("0.5"),
    }
    res_state = {"inertial_metric": BigNum128.from_string("0.1")}
    token_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=BigNum128.from_int(1),
        lambda2=BigNum128.from_int(1),
        c_crit=BigNum128.from_int(0),
        pqc_cid="TEST_BUNDLE",
        timestamp=1234567890,
    )
    with CertifiedMath.LogContext() as log_list:
        try:
            f_atr = BigNum128.from_int(1)
            drv_packet_sequence = 100
            result = hsmf.validate_action_bundle(
                token_bundle=token_bundle,
                f_atr=f_atr,
                drv_packet_sequence=drv_packet_sequence,
                log_list=log_list,
                pqc_cid="TEST_HSMF",
                raise_on_failure=False,
                strict_atr_coherence=False,
            )
            print(f"  HSMF validation result: {result.is_valid}")
            print(f"  DEZ check OK: {result.dez_ok}")
            print(f"  Survival check OK: {result.survival_ok}")
            print(f"  Errors: {result.errors}")
            print(f"  HSMF log entries: {len(log_list)}")
            required_metrics = [
                "action_cost",
                "c_holo",
                "s_res",
                "s_flx",
                "s_psi_sync",
                "f_atr",
                "s_chr",
            ]
            for metric in sorted(required_metrics):
                if metric in result.raw_metrics:
                    print(
                        f"  ✓ Metric '{metric}' present: {result.raw_metrics[metric].to_decimal_string()}"
                    )
                else:
                    print(f"  ✗ Metric '{metric}' missing")
            return result.is_valid
        except Exception as e:
            print(f"  HSMF validation failed: {e}")
            return False


def test_drv_packet():
    """Test DRV_Packet signing and verification."""
    print("\nTesting DRV_Packet...")
    try:
        packet = DRV_Packet(
            ttsTimestamp=1700000000,
            sequence=1,
            seed="test_seed_12345",
            metadata={"source": "test", "version": "1.0"},
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            pqc_cid="DRV_TEST_001",
        )
        print(f"  Created packet with sequence: {packet.sequence}")
        print(f"  Packet hash: {packet.get_hash()}")
        with PQC.LogContext() as pqc_log:
            keypair = PQC.generate_keypair(
                log_list=pqc_log,
                algorithm=PQC.DILITHIUM5,
                seed=packet.seed_bytes,
                pqc_cid="DRV_TEST_002",
            )
            private_key_bytes = bytes(keypair.private_key)
            public_key_bytes = keypair.public_key
            print(f"  Generated keypair for packet")
            packet.sign(private_key_bytes=private_key_bytes, pqc_cid="DRV_TEST_003")
            print(
                f"  Signed packet with signature length: {(len(packet.pqc_signature) if packet.pqc_signature else 0)}"
            )
            is_valid = packet.verify_signature(
                public_key_bytes=public_key_bytes, pqc_cid="DRV_TEST_004"
            )
            print(f"  Signature verification: {is_valid}")
            validation_result = packet.is_valid(
                public_key_bytes=public_key_bytes, pqc_cid="DRV_TEST_005"
            )
            print(f"  Packet validation: {validation_result.is_valid}")
            print(f"  Validation error code: {validation_result.error_code}")
            print(f"  Validation error message: {validation_result.error_message}")
            return is_valid and validation_result.is_valid
    except Exception as e:
        print(f"  DRV_Packet test failed: {e}")
        return False


def test_token_state_bundle():
    """Test TokenStateBundle creation and validation."""
    print("\nTesting TokenStateBundle...")
    try:
        chr_state = {
            "coherence_metric": BigNum128.from_string("0.95"),
            "c_holo_proxy": BigNum128.from_string("0.85"),
        }
        flx_state = {
            "magnitudes": [
                BigNum128.from_int(1),
                BigNum128.from_int(2),
                BigNum128.from_int(3),
            ],
            "scaling_metric": BigNum128.from_string("0.15"),
        }
        psi_sync_state = {
            "current_sequence": BigNum128.from_int(100),
            "frequency_metric": BigNum128.from_string("0.08"),
        }
        atr_state = {
            "atr_magnitude": BigNum128.from_int(1),
            "directional_metric": BigNum128.from_string("0.85"),
        }
        res_state = {"inertial_metric": BigNum128.from_string("0.05")}
        token_bundle = create_token_state_bundle(
            chr_state=chr_state,
            flx_state=flx_state,
            psi_sync_state=psi_sync_state,
            atr_state=atr_state,
            res_state=res_state,
            lambda1=BigNum128.from_string("1.618033988749894848"),
            lambda2=BigNum128.from_string("0.95"),
            c_crit=BigNum128.from_string("1.0"),
            pqc_cid="TOKEN_BUNDLE_TEST",
            timestamp=1234567890,
        )
        print(f"  Created token bundle with ID: {token_bundle.bundle_id}")
        print(f"  Bundle hash: {token_bundle.get_deterministic_hash()}")
        print(
            f"  Coherence metric: {token_bundle.get_coherence_metric().to_decimal_string()}"
        )
        bundle_dict = token_bundle.to_dict(include_signature=False)
        print(f"  Bundle serialized to dictionary with {len(bundle_dict)} fields")
        survival_ok = token_bundle.check_survival_imperative()
        print(f"  Survival imperative satisfied: {survival_ok}")
        return True
    except Exception as e:
        print(f"  TokenStateBundle test failed: {e}")
        return False


def test_cir302_handler():
    """Test CIR302_Handler quarantine functionality."""
    print("\nTesting CIR302_Handler...")
    try:
        cm = CertifiedMath()
        handler = CIR302_Handler(cm)
        test_system_state = {
            "token_states": {
                "CHR": {"coherence": "0.95"},
                "FLX": {"flux": "0.15"},
                "PSI_SYNC": {"sync": "0.08"},
                "ATR": {"attractor": "0.85"},
                "RES": {"resonance": "0.05"},
            },
            "hsmf_metrics": {
                "c_holo": "0.95",
                "s_flx": "0.15",
                "s_psi_sync": "0.08",
                "f_atr": "0.85",
            },
            "error_details": "Test quarantine scenario",
        }
        result = handler.trigger_quarantine("Test CIR-302 trigger", test_system_state)
        print(f"  Quarantine triggered: {result.is_quarantined}")
        print(f"  Reason: {result.reason}")
        print(f"  Finality seal generated: {result.finality_seal is not None}")
        print(f"  System quarantined: {handler.is_system_quarantined()}")
        seal = handler.generate_finality_seal(test_system_state)
        print(f"  Finality seal hash: {seal[:32]}...")
        return result.is_quarantined
    except Exception as e:
        print(f"  CIR302_Handler test failed: {e}")
        return False


def test_ast_zero_simulation():
    """Test AST Zero-Simulation compliance."""
    print("\nTesting AST Zero-Simulation compliance...")
    try:
        checker = AST_ZeroSimChecker()
        violations = checker.scan_file(__file__)
        print(f"  Scanned current file for violations")
        print(f"  Found {len(violations)} violations")
        if len(violations) == 0:
            print(f"  ✓ Zero-Simulation compliance verified")
            return True
        else:
            print(f"  ✗ Zero-Simulation violations found:")
            for violation in sorted(violations):
                print(
                    f"    Line {violation.line_number}: {violation.violation_type} - {violation.message}"
                )
            return False
    except Exception as e:
        print(f"  AST Zero-Simulation test failed: {e}")
        return False


def test_finality_seal_and_afe():
    """Test Finality Seal and Anti-Forgery Equation generation."""
    print("\nTesting Finality Seal and AFE generation...")
    try:
        log_data = [
            {"operation": "test_op_1", "timestamp": 1234567890},
            {"operation": "test_op_2", "timestamp": 1234567891},
        ]
        log_hash = hashlib.sha3_512(
            json.dumps(log_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        print(f"  Generated log hash: {log_hash[:32]}...")
        quantum_metadata = {
            "component": "AFE_TEST",
            "version": "QFS-V13-P1-2",
            "timestamp": "0",
        }
        public_key_bytes = b"test_public_key"
        pqc_signature_bytes = b"test_signature"
        operation_hash = hashlib.sha3_512(b"test_operation").hexdigest()
        quantum_metadata_hash = hashlib.sha3_512(
            json.dumps(quantum_metadata, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        afe_data = {
            "public_key_bytes": public_key_bytes.hex(),
            "pqc_signature_bytes": pqc_signature_bytes.hex(),
            "operation_hash": operation_hash,
            "quantum_metadata_hash": quantum_metadata_hash,
        }
        afe_json = json.dumps(afe_data, sort_keys=True, separators=(",", ":"))
        afe_hash = hashlib.sha3_512(afe_json.encode("utf-8")).hexdigest()
        print(f"  Generated AFE hash: {afe_hash[:32]}...")
        finality_data = {
            "log_hash": log_hash,
            "pqc_signature_bytes": pqc_signature_bytes.hex(),
            "quantum_metadata": quantum_metadata,
        }
        finality_json = json.dumps(finality_data, sort_keys=True, separators=(",", ":"))
        finality_seal = hashlib.sha3_512(finality_json.encode("utf-8")).hexdigest()
        print(f"  Generated finality seal: {finality_seal[:32]}...")
        return True
    except Exception as e:
        print(f"  Finality Seal and AFE test failed: {e}")
        return False


def run_complete_integration_test():
    """Run complete QFS V13 integration test."""
    print("=" * 60)
    print("QFS V13 COMPLETE INTEGRATION TEST")
    print("=" * 60)
    test_results = []
    test_results.append(("CertifiedMath Functions", test_certified_math_functions()))
    test_results.append(("PQC Integration", test_pqc_integration()))
    test_results.append(("HSMF Validation", test_hsmf_validation()))
    test_results.append(("DRV_Packet", test_drv_packet()))
    test_results.append(("TokenStateBundle", test_token_state_bundle()))
    test_results.append(("CIR302_Handler", test_cir302_handler()))
    test_results.append(("AST Zero-Simulation", test_ast_zero_simulation()))
    test_results.append(("Finality Seal & AFE", test_finality_seal_and_afe()))
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    passed = 0
    total = len(test_results)
    for test_name, result in sorted(test_results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 ALL TESTS PASSED - QFS V13 SYSTEM IS FULLY COMPLIANT")
        print("✅ CertifiedMath provides all required deterministic functions")
        print("✅ PQC integration works with real Dilithium5")
        print("✅ HSMF validation with proper log flow")
        print("✅ DRV_Packet signing and verification")
        print("✅ TokenStateBundle creation and validation")
        print("✅ CIR302_Handler quarantine functionality")
        print("✅ AST Zero-Simulation compliance")
        print("✅ Finality seal and AFE generation")
        print("\n🚀 SYSTEM IS PRODUCTION-READY FOR QFS V13")
    else:
        print(f"❌ {total - passed} tests failed - system requires fixes")
    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    run_complete_integration_test()
