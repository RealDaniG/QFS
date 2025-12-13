#!/usr/bin/env python3
"""
Systematically analyze Zero-Sim violations in key files.
Generates a structured report for remediation.
"""

import subprocess
import json
from pathlib import Path

TIER_1_FILES = [
    "src/libs/governance/TreasuryEngine.py",
    "src/libs/governance/RewardAllocator.py", 
    "src/libs/integration/StateTransitionEngine.py",
    "src/libs/economics/EconomicsGuard.py",
    "src/libs/governance/NODAllocator.py",
    "src/libs/governance/NODInvariantChecker.py",
    "src/libs/governance/AEGIS_Node_Verification.py",
    "src/core/CoherenceEngine.py",
    "src/handlers/CIR302_Handler.py",
]

TIER_2_FILES = [
    "src/libs/economics/economic_constants.py",
    "src/libs/economics/EconomicAdversarySuite.py",
    "src/libs/economics/GenesisHarmonicState.py",
    "src/libs/economics/HarmonicEconomics.py",
    "src/libs/economics/HoloRewardEngine.py",
    "src/libs/economics/PsiFieldEngine.py",
    "src/libs/economics/PsiSyncProtocol.py",
    "src/libs/economics/SystemRecoveryProtocol.py",
    "src/libs/economics/TreasuryDistributionEngine.py",
    "src/libs/governance/InfrastructureGovernance.py",
    "src/core/CoherenceLedger.py",
    "src/core/DRV_Packet.py",
    "src/core/gating_service.py",
    "src/core/HSMF.py",
    "src/core/KeyLedger.py",
]

def analyze_file(file_path):
    """Run AST checker on single file and parse output."""
    try:
        result = subprocess.run(
            ["python", "src/libs/AST_ZeroSimChecker.py", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        
        # Extract violation count
        violation_count = 0
        violation_types = set()
        
        for line in output.split('\n'):
            if 'violations found' in line:
                parts = line.split()
                if parts and parts[0].isdigit():
                    violation_count = int(parts[0])
            if '[' in line and ']' in line:
                # Extract violation type like [FLOAT_LITERAL]
                start = line.find('[')
                end = line.find(']')
                if start != -1 and end != -1:
                    violation_types.add(line[start+1:end])
        
        return {
            "file": file_path,
            "violations_count": violation_count,
            "violation_types": sorted(list(violation_types)),
            "status": "CLEAN" if violation_count == 0 else "VIOLATED"
        }
    except Exception as e:
        return {
            "file": file_path,
            "violations_count": -1,
            "violation_types": [],
            "status": f"ERROR: {str(e)}"
        }

def main():
    print("=" * 80)
    print("QFS V13.x Zero-Sim Violation Analysis")
    print("=" * 80)
    
    print("\n[TIER 1] Critical Deterministic Core Modules\n")
    tier1_results = []
    for file_path in TIER_1_FILES:
        result = analyze_file(file_path)
        tier1_results.append(result)
        status = "✅ CLEAN" if result["status"] == "CLEAN" else "❌ VIOLATED"
        print(f"{status:12} | {file_path:50} | {result['violations_count']:4} violations")
        if result["violation_types"]:
            print(f"             | → {', '.join(result['violation_types'][:3])}")
    
    print("\n[TIER 2] Economics/Governance/Core Modules\n")
    tier2_results = []
    for file_path in TIER_2_FILES:
        result = analyze_file(file_path)
        tier2_results.append(result)
        status = "✅ CLEAN" if result["status"] == "CLEAN" else "❌ VIOLATED"
        print(f"{status:12} | {file_path:50} | {result['violations_count']:4} violations")
        if result["violation_types"]:
            print(f"             | → {', '.join(result['violation_types'][:3])}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    tier1_clean = sum(1 for r in tier1_results if r["status"] == "CLEAN")
    tier2_clean = sum(1 for r in tier2_results if r["status"] == "CLEAN")
    
    print(f"\nTier 1 (Critical):  {tier1_clean}/{len(tier1_results)} files clean")
    print(f"Tier 2 (Important): {tier2_clean}/{len(tier2_results)} files clean")
    
    # Files needing attention
    print("\n[REQUIRES ATTENTION]")
    for result in tier1_results + tier2_results:
        if result["status"] != "CLEAN" and result["violations_count"] > 0:
            print(f"  {result['file']:60} → {result['violations_count']} violations")

if __name__ == "__main__":
    main()
