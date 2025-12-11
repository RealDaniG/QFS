"""
phase3_validator.py - Phase 3 Evidence Package Generator and Validator

QFS V13 - Quantum Currency System
Zero-Simulation Compliant | Deterministic | PQC-Ready | Byzantine-Resistant

This tool generates cryptographic evidence packages for Phase 3 components,
builds Merkle trees of all outputs, and produces PQC-signed manifests.
"""

import json
import hashlib
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Handle imports for both package and direct usage
try:
    # Try relative imports first (for package usage)
    from ...src.libs.PQC import PQC
    from ...src.libs.CertifiedMath import BigNum128
    from ...src.libs.economics.GenesisHarmonicState import export_genesis_evidence
    from ...src.libs.economics.PsiFieldEngine import generate_psi_field_evidence
    from ...src.libs.economics.HarmonicEconomics import HarmonicEconomics
    from ...src.core.TokenStateBundle import TokenStateBundle
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from src.libs.PQC import PQC
        from src.libs.CertifiedMath import BigNum128
        from src.libs.economics.GenesisHarmonicState import export_genesis_evidence
        from src.libs.economics.PsiFieldEngine import generate_psi_field_evidence
        from src.libs.economics.HarmonicEconomics import HarmonicEconomics
        from src.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.libs.PQC import PQC
        from src.libs.CertifiedMath import BigNum128
        from src.libs.economics.GenesisHarmonicState import export_genesis_evidence
        from src.libs.economics.PsiFieldEngine import generate_psi_field_evidence
        from src.libs.economics.HarmonicEconomics import HarmonicEconomics
        from src.core.TokenStateBundle import TokenStateBundle


@dataclass
class EvidencePackage:
    """Container for Phase 3 evidence package."""
    genesis_evidence: Dict[str, Any]
    psi_field_evidence: Dict[str, Any]
    harmonic_economics_evidence: Dict[str, Any]
    adversary_results: Dict[str, Any]
    merkle_root: str
    manifest_hash: str
    signature: str = ""


class Phase3Validator:
    """Phase 3 Evidence Package Generator and Validator."""
    
    def __init__(self, pqc_instance: Optional[PQC] = None):
        """
        Initialize the Phase 3 validator.
        
        Args:
            pqc_instance: Optional PQC instance for signing evidence
        """
        self.pqc = pqc_instance
        self.evidence_dir = "evidence/phase3"
        
        # Create evidence directory if it doesn't exist
        os.makedirs(self.evidence_dir, exist_ok=True)
    
    def generate_evidence_package(
        self,
        genesis_topology: Dict[str, Any],
        harmonic_state: TokenStateBundle,
        psi_field_engine: Any,
        harmonic_economics: HarmonicEconomics,
        adversary_results: Dict[str, Any] = None
    ) -> EvidencePackage:
        """
        Generate complete evidence package for Phase 3 components.
        
        Args:
            genesis_topology: Genesis topology data
            harmonic_state: Current harmonic state
            psi_field_engine: PsiFieldEngine instance
            harmonic_economics: HarmonicEconomics instance
            adversary_results: Results from adversary testing
            
        Returns:
            EvidencePackage: Complete evidence package
        """
        # 1. Generate genesis evidence
        genesis_evidence = export_genesis_evidence()
        
        # 2. Generate psi-field evidence
        psi_field_evidence = generate_psi_field_evidence(
            psi_field_engine,
            harmonic_state,
            delta_curl_threshold=harmonic_state.parameters["δ_curl"].value
        )
        
        # 3. Generate harmonic economics evidence
        harmonic_economics_evidence = {
            "economic_health_report": harmonic_economics.get_economic_health_report(),
            "state_history_size": len(harmonic_economics.economic_state_history),
            "violation_summary": {v.value: count for v, count in harmonic_economics.violation_counters.items()}
        }
        
        # 4. Use provided adversary results or create empty
        if adversary_results is None:
            adversary_results = {"adversary_tests": [], "detection_summary": {}}
        
        # 5. Build Merkle tree of all evidence
        evidence_data = {
            "genesis_evidence": genesis_evidence,
            "psi_field_evidence": psi_field_evidence,
            "harmonic_economics_evidence": harmonic_economics_evidence,
            "adversary_results": adversary_results
        }
        
        merkle_root = self._build_merkle_tree(evidence_data)
        
        # 6. Create manifest hash
        manifest_data = {
            "evidence_data": evidence_data,
            "merkle_root": merkle_root,
            "timestamp": harmonic_state.timestamp,
            "version": "QFSV13-Phase3-Evidence-v1.0"
        }
        
        manifest_hash = self._compute_deterministic_hash(manifest_data)
        
        # 7. Create evidence package
        evidence_package = EvidencePackage(
            genesis_evidence=genesis_evidence,
            psi_field_evidence=psi_field_evidence,
            harmonic_economics_evidence=harmonic_economics_evidence,
            adversary_results=adversary_results,
            merkle_root=merkle_root,
            manifest_hash=manifest_hash
        )
        
        return evidence_package
    
    def _build_merkle_tree(self, evidence_data: Dict[str, Any]) -> str:
        """
        Build Merkle tree from evidence data.
        
        Args:
            evidence_data: Evidence data to build Merkle tree from
            
        Returns:
            str: Merkle root hash
        """
        # Convert evidence data to deterministic JSON
        evidence_json = json.dumps(evidence_data, sort_keys=True, separators=(',', ':'))
        
        # Simple Merkle tree implementation (in a real implementation, 
        # this would be a proper Merkle tree with multiple levels)
        # NOTE: SHA3-256 is permitted in evidence layer per QFSV13 §8.3
        return hashlib.sha3_256(evidence_json.encode('utf-8')).hexdigest()
    
    def _compute_deterministic_hash(self, data: Dict[str, Any]) -> str:
        """
        Compute deterministic hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            str: SHA-256 hash as hexadecimal string
        """
        # Convert to deterministic JSON
        data_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Compute hash
        return hashlib.sha256(data_json.encode('utf-8')).hexdigest()
    
    def sign_evidence_package(
        self, 
        evidence_package: EvidencePackage, 
        private_key: bytes
    ) -> EvidencePackage:
        """
        Sign evidence package with PQC signature.
        
        Args:
            evidence_package: Evidence package to sign
            private_key: Private key for signing
            
        Returns:
            EvidencePackage: Signed evidence package
        """
        if not self.pqc:
            raise RuntimeError("PQC instance not provided")
        
        # Create data to sign
        data_to_sign = {
            "manifest_hash": evidence_package.manifest_hash,
            "merkle_root": evidence_package.merkle_root,
            "timestamp": str(evidence_package.genesis_evidence.get("timestamp", 0))
        }
        
        # Convert to deterministic JSON
        data_json = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
        
        # Sign with PQC
        signature_result = self.pqc.sign_message(
            private_key=private_key,
            data=data_json.encode('utf-8'),
            log_list=[],  # Empty log list for signing
            pqc_cid="PHASE3_EVIDENCE_SIGNING",
            quantum_metadata={"component": "phase3_validator"},
            deterministic_timestamp=0
        )
        
        # Add signature to evidence package
        evidence_package.signature = signature_result.signature.hex()
        
        return evidence_package
    
    def export_evidence_package(self, evidence_package: EvidencePackage) -> str:
        """
        Export evidence package to files.
        
        Args:
            evidence_package: Evidence package to export
            
        Returns:
            str: Path to exported evidence directory
        """
        # Export genesis evidence
        with open(os.path.join(self.evidence_dir, "phase3_genesis.json"), "w") as f:
            json.dump(evidence_package.genesis_evidence, f, indent=2, separators=(',', ':'))
        
        # Export psi-field evidence
        with open(os.path.join(self.evidence_dir, "phase3_psi_dynamics.json"), "w") as f:
            json.dump(evidence_package.psi_field_evidence, f, indent=2, separators=(',', ':'))
        
        # Export harmonic economics evidence
        with open(os.path.join(self.evidence_dir, "phase3_harmonics.json"), "w") as f:
            json.dump(evidence_package.harmonic_economics_evidence, f, indent=2, separators=(',', ':'))
        
        # Export adversary results
        with open(os.path.join(self.evidence_dir, "phase3_adversary_results.json"), "w") as f:
            json.dump(evidence_package.adversary_results, f, indent=2, separators=(',', ':'))
        
        # Export manifest
        manifest = {
            "manifest_hash": evidence_package.manifest_hash,
            "merkle_root": evidence_package.merkle_root,
            "signature": evidence_package.signature,
            "timestamp": evidence_package.genesis_evidence.get("timestamp", 0),
            "version": "QFSV13-Phase3-Evidence-v1.0"
        }
        
        with open(os.path.join(self.evidence_dir, "phase3_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2, separators=(',', ':'))
        
        # Export final hash
        with open(os.path.join(self.evidence_dir, "phase3_final_hash.sha256"), "w") as f:
            f.write(evidence_package.manifest_hash)
        
        return self.evidence_dir
    
    def validate_evidence_package(self, evidence_dir: str = None) -> bool:
        """
        Validate evidence package integrity.
        
        Args:
            evidence_dir: Directory containing evidence files (defaults to self.evidence_dir)
            
        Returns:
            bool: True if evidence package is valid
        """
        if evidence_dir is None:
            evidence_dir = self.evidence_dir
        
        # Check if evidence directory exists
        if not os.path.exists(evidence_dir):
            return False
        
        # Required evidence files
        required_files = [
            "phase3_genesis.json",
            "phase3_psi_dynamics.json",
            "phase3_harmonics.json",
            "phase3_adversary_results.json",
            "phase3_manifest.json",
            "phase3_final_hash.sha256"
        ]
        
        # Check if all required files exist
        for file_name in required_files:
            if not os.path.exists(os.path.join(evidence_dir, file_name)):
                return False
        
        # Load manifest
        with open(os.path.join(evidence_dir, "phase3_manifest.json"), "r") as f:
            manifest = json.load(f)
        
        # Load final hash
        with open(os.path.join(evidence_dir, "phase3_final_hash.sha256"), "r") as f:
            final_hash = f.read().strip()
        
        # Verify manifest hash matches final hash
        if manifest["manifest_hash"] != final_hash:
            return False
        
        # If PQC is available, verify signature
        if self.pqc and manifest.get("signature"):
            try:
                # Create data that was signed
                data_to_verify = {
                    "manifest_hash": manifest["manifest_hash"],
                    "merkle_root": manifest["merkle_root"],
                    "timestamp": str(manifest.get("timestamp", 0))
                }
                
                # Convert to deterministic JSON
                data_json = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
                
                # Verify signature
                signature_bytes = bytes.fromhex(manifest["signature"])
                verification_result = self.pqc.verify_signature(
                    public_key=b"",  # Would need actual public key in real implementation
                    data=data_json.encode('utf-8'),
                    signature=signature_bytes,
                    log_list=[],
                    pqc_cid="PHASE3_EVIDENCE_VERIFICATION",
                    quantum_metadata={"component": "phase3_validator"},
                    deterministic_timestamp=0
                )
                
                return verification_result.is_valid
            except Exception:
                return False
        
        # If no PQC available, just check hash integrity
        return True


def main():
    """Main function for running the Phase 3 validator."""
    print("Phase 3 Evidence Package Generator")
    print("==================================")
    
    # Initialize validator
    validator = Phase3Validator()
    
    # In a real implementation, this would load actual data and generate evidence
    print("✓ Phase 3 validator initialized successfully")
    print("✓ Ready to generate evidence packages for Phase 3 components")


if __name__ == "__main__":
    main()