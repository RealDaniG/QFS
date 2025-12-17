"""
Tests for the CIR-302 incident simulation script
"""
import json
import tempfile
import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.scripts.simulate_storage_cir302_incident import CIR302IncidentSimulator
from v13.libs.deterministic_helpers import det_time_isoformat

class TestCIR302Simulation:
    """Test suite for CIR302 incident simulation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.simulator = CIR302IncidentSimulator()

    def test_initialize_simulator(self):
        """Test that CIR302IncidentSimulator initializes correctly"""
        assert self.simulator.cm is not None
        assert self.simulator.storage_engine is not None
        assert self.simulator.cir302_handler is not None

    def test_simulate_economic_violation(self):
        """Test economic violation simulation"""
        details = self.simulator.simulate_economic_violation()
        assert 'scenario' in details
        assert details['scenario'] == 'economic_violation'
        assert 'violation_detected' in details
        assert 'cir302_triggered' in details
        assert details['violation_detected'] == True
        assert details['cir302_triggered'] == True

    def test_simulate_proof_chain_corruption(self):
        """Test proof chain corruption simulation"""
        details = self.simulator.simulate_proof_chain_corruption()
        assert 'scenario' in details
        assert details['scenario'] == 'proof_chain_corruption'
        assert 'corruption_simulated' in details
        assert 'cir302_triggered' in details
        assert details['cir302_triggered'] == True

    def test_simulate_aegis_cascade_failure(self):
        """Test AEGIS cascade failure simulation"""
        details = self.simulator.simulate_aegis_cascade_failure()
        assert 'scenario' in details
        assert details['scenario'] == 'aegis_cascade_failure'
        assert 'cascade_failure_detected' in details
        assert 'cir302_triggered' in details
        assert details['cascade_failure_detected'] == True
        assert details['cir302_triggered'] == True

    def test_create_evidence_artifact(self):
        """Test evidence artifact creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_evidence_dir = 'docs/evidence/incidents'
            test_details = {'scenario': 'test_scenario', 'description': 'Test incident simulation', 'cir302_triggered': True}
            evidence_path = self.simulator.create_evidence_artifact('test_scenario', test_details)
            assert os.path.exists(evidence_path)
            with open(evidence_path, 'r') as f:
                evidence = json.load(f)
            assert 'component' in evidence
            assert 'incident_type' in evidence
            assert 'scenario' in evidence
            assert evidence['scenario'] == 'test_scenario'
            assert 'timestamp' in evidence
            assert 'simulation_details' in evidence
            assert 'verification' in evidence
            assert evidence['verification']['cir302_response_validated'] == True

def test_cir302_simulation():
    """Test the CIR302 simulation implementation"""
    print('Testing CIR-302 incident simulation...')
    test_instance = TestCIR302Simulation()
    test_instance.setup_method()
    test_instance.test_initialize_simulator()
    print('✓ test_initialize_simulator passed')
    test_instance.test_simulate_economic_violation()
    print('✓ test_simulate_economic_violation passed')
    test_instance.test_simulate_proof_chain_corruption()
    print('✓ test_simulate_proof_chain_corruption passed')
    test_instance.test_simulate_aegis_cascade_failure()
    print('✓ test_simulate_aegis_cascade_failure passed')
    test_instance.test_create_evidence_artifact()
    print('✓ test_create_evidence_artifact passed')
    print('CIR-302 simulation tests completed successfully')
if __name__ == '__main__':
    test_cir302_simulation()