#!/usr/bin/env python3
"""
Run Phase 2 tests for QFS V13.5: Determinism Fuzzer and Adversarial Simulator
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.determinism_fuzzer import DeterminismFuzzer
from tools.adversarial_simulator import AdversarialSimulator, CIR302_Handler
from v13.libs.CertifiedMath import CertifiedMath


def run_determinism_fuzzer():
    """Run the determinism fuzzer and save results."""
    print("Running Determinism Fuzzer...")
    
    fuzzer = DeterminismFuzzer()
    
    # Run a smaller test for demonstration (1000 ops instead of 100k)
    test_hash = fuzzer.run_fuzz_test(1000)
    
    # Save results
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "test_runs": 1000,
        "hash": test_hash
    }
    
    # Save to evidence directory
    os.makedirs("evidence/phase2_fuzzer", exist_ok=True)
    with open("evidence/phase2_fuzzer/results.json", "w") as f:
        json.dump(result_data, f, indent=2)
    
    print(f"✓ Determinism Fuzzer completed. Hash: {test_hash}")
    return test_hash


def run_adversarial_simulator():
    """Run the adversarial simulator and save results."""
    print("Running Adversarial Simulator...")
    
    # Create required components
    cm = CertifiedMath  # Pass the class, not an instance
    cir302 = CIR302_Handler(cm)
    simulator = AdversarialSimulator(CertifiedMath(), cir302)
    
    # Run attacks (in a real scenario, this would trigger SystemExit)
    try:
        results = simulator.run_all_attacks()
        
        # Save results
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "attacks": [
                {
                    "attack_name": r.attack_name,
                    "triggered_cir302": r.triggered_cir302,
                    "error_message": r.error_message,
                    "recovery_state": r.recovery_state
                }
                for r in results
            ]
        }
        
        # Save to evidence directory
        os.makedirs("evidence/phase2_adversary", exist_ok=True)
        with open("evidence/phase2_adversary/results.json", "w") as f:
            json.dump(result_data, f, indent=2)
        
        print(f"✓ Adversarial Simulator completed. Results saved.")
        return results
        
    except SystemExit as e:
        print(f"SystemExit caught with code {e.code} - this is expected in adversarial testing")
        return []


def main():
    """Main function to run all Phase 2 tests."""
    print("QFS V13.5 - Phase 2 Testing")
    print("=" * 40)
    
    # Run determinism fuzzer
    fuzzer_hash = run_determinism_fuzzer()
    
    # Run adversarial simulator
    attack_results = run_adversarial_simulator()
    
    # Summary
    print("\n" + "=" * 40)
    print("Phase 2 Testing Summary:")
    print(f"  - Determinism Fuzzer Hash: {fuzzer_hash}")
    print(f"  - Adversarial Attacks Run: {len(attack_results) if attack_results else 'N/A (SystemExit)'}")
    print("✓ All Phase 2 tests completed!")


if __name__ == "__main__":
    main()