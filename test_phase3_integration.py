#!/usr/bin/env python3
"""
Comprehensive integration test for all Phase 3 components
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'libs'))

from libs.CertifiedMath import CertifiedMath, BigNum128
from libs.economics.GenesisHarmonicState import GENESIS_STATE, FOUNDING_NODE_REGISTRY
from libs.economics.PsiFieldEngine import DiscretePsiField, create_secure_psi_field
from libs.economics.HarmonicEconomics import HarmonicEconomics
from libs.economics.TreasuryDistributionEngine import TreasuryDistributionEngine
from libs.economics.HoloRewardEngine import HoloRewardEngine
from libs.economics.PsiSyncProtocol import PsiSyncProtocol, create_psisync_protocol
from libs.economics.SystemRecoveryProtocol import SystemRecoveryProtocol, create_system_recovery_protocol
from libs.economics.EconomicAdversarySuite import EconomicAdversarySuite, create_economic_adversary_suite
from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle

# Mock PQC class for testing
class MockPQC:
    def __init__(self):
        pass
    
    def sign_data(self, private_key, data, log_list):
        # Return a mock signature
        return type('obj', (object,), {'signature': b'mock_signature'})()
    
    def verify_signature(self, public_key, data, signature, log_list):
        # Always return valid for testing
        return type('obj', (object,), {'is_valid': True})()

def create_mock_cir_handlers():
    """Create mock CIR handlers for testing"""
    class MockCIRHandler:
        def __init__(self):
            self.events = []
        
        def halt(self, reason, details, evidence=None):
            self.events.append({
                "type": "halt",
                "reason": reason,
                "details": details,
                "evidence": evidence
            })
        
        def notify(self, reason, details, severity, evidence=None):
            self.events.append({
                "type": "notify",
                "reason": reason,
                "details": details,
                "severity": severity,
                "evidence": evidence
            })
    
    return {
        "cir302": MockCIRHandler(),
        "cir412": MockCIRHandler(),
        "cir511": MockCIRHandler()
    }

def test_component_integration():
    """Test integration of all Phase 3 components"""
    print("Testing Phase 3 component integration...")
    
    # Initialize CertifiedMath
    certified_math = CertifiedMath()
    
    # Create mock CIR handlers
    cir_handlers = create_mock_cir_handlers()
    
    # Create genesis state
    genesis_state = GENESIS_STATE
    
    # Create psi field engine
    psi_field = create_secure_psi_field(
        genesis_topology=genesis_state["topology"],
        certified_math=certified_math,
        security_level="BALANCED"
    )
    
    # Create TokenStateBundle from genesis state
    chr_state = {
        "shards": genesis_state["token_allocations"]["shards"]
    }
    flx_state = {
        "FLX_flow_matrix": {}
    }
    psi_sync_state = {}
    atr_state = {}
    res_state = {}
    
    token_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=BigNum128.from_int(1618033988749894848),  # φ * 1e18
        lambda2=BigNum128.from_int(618033988749894848),   # (φ-1) * 1e18
        c_crit=BigNum128.from_int(1000000000000000000),   # 1.0 * 1e18
        pqc_cid="test_phase3_integration",
        timestamp=1763510400,
        quantum_metadata={"test": "phase3_integration"}
    )
    
    # Create harmonic economics (note: no CIR handlers in constructor)
    economics = HarmonicEconomics(
        psi_field_engine=psi_field,
        certified_math=certified_math
    )
    
    # Create psi sync protocol
    psisync = create_psisync_protocol(
        certified_math=certified_math,
        cir412_handler=cir_handlers["cir412"],
        security_level="BALANCED"
    )
    
    # Create treasury distribution engine
    mock_pqc = MockPQC()
    treasury = TreasuryDistributionEngine(
        certified_math=certified_math,
        pqc_signer=mock_pqc,
        cir302_handler=cir_handlers["cir302"],
        psi_field_engine=psi_field,
        psisync_protocol=psisync
    )
    
    # Create holo reward engine
    holo_reward = HoloRewardEngine(
        certified_math=certified_math,
        cir302_handler=cir_handlers["cir302"],
        psi_field_engine=psi_field
    )
    
    # Create system recovery protocol
    recovery = create_system_recovery_protocol(
        certified_math=certified_math,
        pqc_verifier=mock_pqc,
        founding_nodes=FOUNDING_NODE_REGISTRY,
        recovery_threshold=3,
        security_level="BALANCED"
    )
    
    # Test psi field validation
    print("Testing psi field validation...")
    try:
        validation_result = psi_field.validate_psi_field_integrity(
            token_bundle,
            delta_curl_threshold=10
        )
        print(f"✓ Psi field validation passed: {validation_result['security_checks_passed']}")
    except Exception as e:
        print(f"❌ Psi field validation failed: {e}")
        return False
    
    # Test harmonic economics
    print("Testing harmonic economics...")
    try:
        economic_result = economics.compute_harmonic_state(token_bundle)
        print(f"✓ Harmonic economics computation passed")
    except Exception as e:
        print(f"❌ Harmonic economics computation failed: {e}")
        return False
    
    # Test psi sync protocol
    print("Testing psi sync protocol...")
    try:
        # Create mock shard psi sync values
        shard_psisync_values = {
            shard_id: 1000 for shard_id in genesis_state["token_allocations"]["shards"].keys()
        }
        
        psisync_result = psisync.compute_global_psisync(
            shard_psisync_values=shard_psisync_values,
            epsilon_sync=2,
            genesis_shard_count=len(genesis_state["token_allocations"]["shards"]),
            genesis_shard_ids=list(genesis_state["token_allocations"]["shards"].keys()),
            epoch_id="test_epoch_1"
        )
        print(f"✓ Psi sync protocol computation passed: global_psisync={psisync_result['global_psisync']}")
    except Exception as e:
        print(f"❌ Psi sync protocol computation failed: {e}")
        return False
    
    # Test treasury distribution
    print("Testing treasury distribution...")
    try:
        treasury_result = treasury.compute_system_treasury_distribution(
            harmonic_state=token_bundle,
            treasury_balance=1000000000,
            epoch_id="test_epoch_1",
            genesis_shard_ids=list(genesis_state["token_allocations"]["shards"].keys()),
            global_psisync=1000
        )
        print(f"✓ Treasury distribution computation passed")
    except Exception as e:
        print(f"❌ Treasury distribution computation failed: {e}")
        return False
    
    # Test holo reward engine
    print("Testing holo reward engine...")
    try:
        reward_result = holo_reward.compute_holofield_reward_package(
            harmonic_state=token_bundle,
            treasury_state=type('obj', (object,), {'total_distributed': 1000000000})(),
            epoch_id="test_epoch_1"
        )
        print(f"✓ Holo reward engine computation passed: reward_multiplier={reward_result['reward_multiplier']}")
    except Exception as e:
        print(f"❌ Holo reward engine computation failed: {e}")
        return False
    
    # Test system recovery protocol
    print("Testing system recovery protocol...")
    try:
        recovery_status = recovery.get_recovery_status()
        print(f"✓ System recovery protocol status check passed: current_state={recovery_status['current_state']}")
    except Exception as e:
        print(f"❌ System recovery protocol status check failed: {e}")
        return False
    
    print("All component integration tests passed!")
    return True

def test_economic_adversary_suite():
    """Test the economic adversary suite"""
    print("\nTesting Economic Adversary Suite...")
    
    # Initialize CertifiedMath
    certified_math = CertifiedMath()
    
    # Create mock CIR handlers
    cir_handlers = create_mock_cir_handlers()
    
    # Create genesis state
    genesis_state = GENESIS_STATE
    
    # Create psi field engine
    psi_field = create_secure_psi_field(
        genesis_topology=genesis_state["topology"],
        certified_math=certified_math,
        security_level="BALANCED"
    )
    
    # Create TokenStateBundle from genesis state
    chr_state = {
        "shards": genesis_state["token_allocations"]["shards"]
    }
    flx_state = {
        "FLX_flow_matrix": {}
    }
    psi_sync_state = {}
    atr_state = {}
    res_state = {}
    
    token_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=BigNum128.from_int(1618033988749894848),  # φ * 1e18
        lambda2=BigNum128.from_int(618033988749894848),   # (φ-1) * 1e18
        c_crit=BigNum128.from_int(1000000000000000000),   # 1.0 * 1e18
        pqc_cid="test_adversary_suite",
        timestamp=1763510400,
        quantum_metadata={"test": "adversary_suite"}
    )
    
    # Create harmonic economics (note: no CIR handlers in constructor)
    economics = HarmonicEconomics(
        psi_field_engine=psi_field,
        certified_math=certified_math
    )
    
    # Create psi sync protocol
    psisync = create_psisync_protocol(
        certified_math=certified_math,
        cir412_handler=cir_handlers["cir412"],
        security_level="BALANCED"
    )
    
    # Create treasury distribution engine
    mock_pqc = MockPQC()
    treasury = TreasuryDistributionEngine(
        certified_math=certified_math,
        pqc_signer=mock_pqc,
        cir302_handler=cir_handlers["cir302"],
        psi_field_engine=psi_field,
        psisync_protocol=psisync
    )
    
    # Create holo reward engine
    holo_reward = HoloRewardEngine(
        certified_math=certified_math,
        cir302_handler=cir_handlers["cir302"],
        psi_field_engine=psi_field
    )
    
    # Create system recovery protocol
    recovery = create_system_recovery_protocol(
        certified_math=certified_math,
        pqc_verifier=mock_pqc,
        founding_nodes=FOUNDING_NODE_REGISTRY,
        recovery_threshold=3,
        security_level="BALANCED"
    )
    
    # Create mock coherence ledger
    class MockCoherenceLedger:
        def __init__(self):
            self.events = []
        
        def record_event(self, event):
            self.events.append(event)
    
    coherence_ledger = MockCoherenceLedger()
    
    # Create economic adversary suite
    adversary_suite = create_economic_adversary_suite(
        certified_math=certified_math,
        psi_field_engine=psi_field,
        harmonic_economics=economics,
        treasury_engine=treasury,
        psisync_protocol=psisync,
        coherence_ledger=coherence_ledger,
        system_recovery_protocol=recovery,
        genesis_state=token_bundle
    )
    
    print("✓ Economic Adversary Suite created successfully")
    return True

if __name__ == "__main__":
    print("Running Phase 3 integration tests...")
    
    try:
        # Test component integration
        if not test_component_integration():
            print("\n❌ Component integration tests failed!")
            sys.exit(1)
        
        # Test economic adversary suite
        if not test_economic_adversary_suite():
            print("\n❌ Economic Adversary Suite tests failed!")
            sys.exit(1)
        
        print("\n✅ All Phase 3 integration tests passed!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Integration tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)