"""
Comprehensive test to verify all modules are working together correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def test_all_modules():
    """Test all modules to ensure they work together."""
    print("Running comprehensive test of all QFS V13 modules...")
    
    try:
        # Test CertifiedMath
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        print("✓ CertifiedMath imported successfully")
        
        # Test PQC
        from src.libs.PQC import PQC
        print("✓ PQC imported successfully")
        
        # Test Core modules
        from src.core.TokenStateBundle import TokenStateBundle
        print("✓ TokenStateBundle imported successfully")
        
        # Test Governance modules
        from src.libs.governance.TreasuryEngine import TreasuryEngine
        print("✓ TreasuryEngine imported successfully")
        
        from src.libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
        print("✓ RewardAllocator imported successfully")
        
        # Test Integration modules
        from src.libs.integration.StateTransitionEngine import StateTransitionEngine
        print("✓ StateTransitionEngine imported successfully")
        
        from src.libs.integration.HolonetSync import HolonetSync
        print("✓ HolonetSync imported successfully")
        
        # Test Core modules
        from src.libs.core.UtilityOracle import UtilityOracle
        print("✓ UtilityOracle imported successfully")
        
        # Test Quantum modules
        from src.libs.quantum.QPU_Interface import QPU_Interface
        print("✓ QPU_Interface imported successfully")
        
        # Test Handlers
        from src.handlers.CIR302_Handler import CIR302_Handler
        print("✓ CIR302_Handler imported successfully")
        
        # Create instances and test basic functionality
        cm = CertifiedMath()
        print("✓ CertifiedMath instance created successfully")
        
        # Test basic math operations
        a = BigNum128.from_int(100)
        b = BigNum128.from_int(50)
        
        with cm.LogContext() as log_list:
            result = cm.add(a, b, log_list)
            print(f"✓ Basic math operation: 100 + 50 = {result.to_decimal_string()}")
            
            # Test TreasuryEngine
            treasury = TreasuryEngine(cm)
            print("✓ TreasuryEngine instance created successfully")
            
            # Test RewardAllocator
            allocator = RewardAllocator(cm)
            print("✓ RewardAllocator instance created successfully")
            
            # Test StateTransitionEngine
            state_engine = StateTransitionEngine(cm)
            print("✓ StateTransitionEngine instance created successfully")
            
            # Test HolonetSync
            holonet = HolonetSync(cm)
            print("✓ HolonetSync instance created successfully")
            
            # Test UtilityOracle
            oracle = UtilityOracle(cm)
            print("✓ UtilityOracle instance created successfully")
            
            # Test QPU_Interface
            qpu = QPU_Interface(cm)
            print("✓ QPU_Interface instance created successfully")
            
            # Test basic functionality of each module
            # Test UtilityOracle
            atr_state = BigNum128.from_int(50)
            guidance = oracle.get_atr_directional_vector(
                current_atr_state=atr_state,
                log_list=log_list,
                pqc_cid="test_001",
                deterministic_timestamp=1234567890
            )
            print(f"✓ UtilityOracle guidance calculation: {guidance.to_decimal_string()}")
            
            # Test QPU_Interface
            entropy = qpu.get_quantum_entropy(
                length=16,
                log_list=log_list,
                pqc_cid="test_001",
                deterministic_timestamp=1234567890
            )
            print(f"✓ QPU_Interface entropy generation: {len(entropy.raw_entropy)} bytes")
            
            # Test HolonetSync
            sync_result = holonet.propagate_finality(
                bundle_hash="test_bundle_123",
                log_hash="test_log_456",
                coherence_metrics={"c_holo": "0.95", "s_chr": "0.98"},
                log_list=log_list,
                pqc_cid="test_001",
                deterministic_timestamp=1234567890
            )
            print(f"✓ HolonetSync propagation: {sync_result}")
            
        print("\n✅ All modules imported and basic functionality tested successfully!")
        print(f"✅ Total log entries generated: {len(log_list)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing modules: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_modules()
    sys.exit(0 if success else 1)