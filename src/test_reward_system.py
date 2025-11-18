"""
Test script to verify RewardAllocator and TreasuryEngine fixes
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that imports work correctly"""
    try:
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.reward_types import RewardBundle
        from libs.governance.TreasuryEngine import TreasuryEngine
        from libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
        from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_deterministic_iteration():
    """Test that dictionary iteration is deterministic"""
    try:
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from libs.governance.RewardAllocator import RewardAllocator
        
        cm = CertifiedMath()
        allocator = RewardAllocator(cm)
        
        # Create test weights in a non-deterministic order
        weights = {
            "zebra": BigNum128.from_int(1),
            "alpha": BigNum128.from_int(2),
            "beta": BigNum128.from_int(3)
        }
        
        log_list = []
        # This should work deterministically now
        normalized = allocator._normalize_weights(weights, log_list)
        
        # Check that keys are processed in sorted order
        keys = list(normalized.keys())
        if keys == sorted(keys):
            print("✓ Deterministic iteration order verified")
            return True
        else:
            print(f"✗ Iteration order not deterministic: {keys}")
            return False
    except Exception as e:
        print(f"✗ Deterministic iteration test failed: {e}")
        return False

def test_c_holo_check():
    """Test that C_holo < C_MIN check works"""
    try:
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from libs.governance.TreasuryEngine import TreasuryEngine
        from core.TokenStateBundle import create_token_state_bundle
        
        cm = CertifiedMath()
        treasury = TreasuryEngine(cm)
        
        # Create test metrics where C_holo < C_MIN
        hsmf_metrics = {
            "S_CHR": BigNum128.from_int(5),
            "C_holo": BigNum128.from_int(1),  # Low coherence
            "Action_Cost_QFS": BigNum128.from_int(2)
        }
        
        # Create token bundle with higher C_MIN
        token_bundle = create_token_state_bundle(
            chr_state={"balance": "100.0", "coherence_metric": "5.0"},
            flx_state={"balance": "50.0", "scaling_metric": "2.0"},
            psi_sync_state={"balance": "25.0", "frequency_metric": "1.0"},
            atr_state={"balance": "30.0", "directional_metric": "1.5"},
            res_state={"balance": "40.0", "inertial_metric": "2.5"},
            lambda1=BigNum128.from_int(1),
            lambda2=BigNum128.from_int(1),
            c_crit=BigNum128.from_int(3),  # Higher than C_holo
            pqc_cid="test_treasury_001",
            timestamp=1234567890
        )
        
        log_list = []
        
        # This should raise an error
        try:
            rewards = treasury.calculate_rewards(
                hsmf_metrics=hsmf_metrics,
                token_bundle=token_bundle,
                log_list=log_list,
                pqc_cid="test_treasury_001",
                deterministic_timestamp=1234567890
            )
            print("✗ C_holo check failed - should have raised an error")
            return False
        except RuntimeError as e:
            if "C_holo < C_MIN" in str(e):
                print("✓ C_holo < C_MIN check working correctly")
                return True
            else:
                print(f"✗ Wrong error message: {e}")
                return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"✗ C_holo check test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Reward System Fixes...")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_deterministic_iteration,
        test_c_holo_check
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Reward system is QFS V13.5 compliant.")
        return True
    else:
        print("❌ Some tests failed. Please review the fixes.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)