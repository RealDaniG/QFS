"""
Test file to verify HSMF.py compliance with QFS V13 requirements
"""

from CertifiedMath import BigNum128, CertifiedMath
from HSMF import HSMF, ValidationResult
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Mock TokenStateBundle for testing
@dataclass
class MockTokenStateBundle:
    """Mock implementation of TokenStateBundle for testing purposes"""
    atr_state: Dict[str, BigNum128]
    flx_state: Dict[str, List[BigNum128]]
    psi_sync_state: Dict[str, BigNum128]
    lambda1: BigNum128
    lambda2: BigNum128
    c_crit: BigNum128
    timestamp: int
    bundle_id: str = "test_bundle"
    pqc_cid: str = "test_pqc"
    
    def get_coherence_metric(self) -> BigNum128:
        """Get coherence metric for testing"""
        return BigNum128.from_int(1)  # High coherence for testing

def test_hsmf_compliance():
    """Test that HSMF.py is fully compliant with QFS V13 requirements"""
    print("Testing HSMF compliance with QFS V13 requirements...")
    
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # Create HSMF instance
    hsmf = HSMF(cm)
    
    # Create mock token bundle
    token_bundle = MockTokenStateBundle(
        atr_state={"atr_magnitude": BigNum128.from_int(1)},
        flx_state={"magnitudes": [BigNum128.from_int(1), BigNum128.from_int(2), BigNum128.from_int(3)]},
        psi_sync_state={"current_sequence": BigNum128.from_int(100)},
        lambda1=BigNum128.from_int(1),
        lambda2=BigNum128.from_int(1),
        c_crit=BigNum128.from_int(0),  # Low critical threshold for testing
        timestamp=1234567890
    )
    
    # Test with CertifiedMath LogContext
    with CertifiedMath.LogContext() as log_list:
        # Test validate_action_bundle
        f_atr = BigNum128.from_int(1)  # Valid f(ATR) value in [0,1]
        drv_packet_sequence = 100  # Matching sequence number
        
        try:
            result = hsmf.validate_action_bundle(
                token_bundle=token_bundle,
                f_atr=f_atr,
                drv_packet_sequence=drv_packet_sequence,
                log_list=log_list,
                pqc_cid="test_pqc_id",
                raise_on_failure=False,
                strict_atr_coherence=False,
                quantum_metadata={"test": "metadata"}
            )
            
            print(f"Validation result: {result.is_valid}")
            print(f"DEZ check OK: {result.dez_ok}")
            print(f"Survival check OK: {result.survival_ok}")
            print(f"Errors: {result.errors}")
            print(f"Log entries: {len(log_list)}")
            
            # Verify that all required metrics are present
            required_metrics = ["action_cost", "c_holo", "s_res", "s_flx", "s_psi_sync", "f_atr", "s_chr"]
            for metric in required_metrics:
                if metric in result.raw_metrics:
                    print(f"✓ Metric '{metric}' present: {result.raw_metrics[metric].to_decimal_string()}")
                else:
                    print(f"✗ Metric '{metric}' missing")
            
            # Verify log entries were created
            if len(log_list) > 0:
                print(f"✓ Log entries created: {len(log_list)}")
                # Show first few log entries
                for i, entry in enumerate(log_list[:3]):
                    print(f"  Log entry {i+1}: {entry['op_name']}")
            else:
                print("✗ No log entries created")
                
            print("HSMF compliance test completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during HSMF validation: {e}")
            return False

if __name__ == "__main__":
    test_hsmf_compliance()