"""
PQCAdapterFactory - Factory for Creating PQC Adapters
Selects between CorePQCAdapter and MockPQCAdapter based on availability
"""
from typing import Tuple
from ..interfaces.pqc_interface import PQCInterface
from .dilithium5_adapter import Dilithium5Adapter
from .mock_pqc_adapter import MockPQCAdapter

class PQCAdapterFactory:
    """
    Factory for creating PQC adapters based on environment availability.
    """

    @staticmethod
    def create_adapter() -> Tuple[PQCInterface, str]:
        """
        Create the appropriate PQC adapter based on library availability.
        
        Returns:
            Tuple of (adapter_instance, backend_name)
            
        Backend Priority:
        1. CorePQCAdapter (production - dilithium-py)
        2. MockPQCAdapter (testing - SHA-256 simulation)
        """
        try:
            adapter = Dilithium5Adapter()
            test_seed = b'test_seed_1234567890123456789012'
            adapter.keygen(test_seed)
            return (adapter, 'dilithium-py')
        except Exception as e:
            adapter = MockPQCAdapter()
            return (adapter, 'MockPQC')

    @staticmethod
    def get_backend_info() -> dict:
        """
        Get information about the currently active PQC backend.
        
        Returns:
            dict with backend name and production readiness info
        """
        try:
            from ...pqc.PQC_Core import Dilithium5Impl
            adapter = Dilithium5Adapter()
            test_seed = b'test_seed_1234567890123456789012'
            adapter.keygen(test_seed)
            return {'backend': 'dilithium-py', 'algorithm': 'Dilithium-5 (NIST PQC Standard)', 'security_level': 'NIST Level 5 (highest)', 'production_ready': True, 'quantum_resistant': True, 'deterministic': True}
        except Exception:
            return {'backend': 'MockPQC', 'algorithm': 'SHA-256 (simulation only)', 'security_level': 'NONE - NOT CRYPTOGRAPHICALLY SECURE', 'production_ready': False, 'quantum_resistant': False, 'deterministic': True, 'warning': 'INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION'}
