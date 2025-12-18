"""
Test-mode CIR302_Handler for AdversarialSimulator.
This handler avoids actual halts during testing by capturing exit codes instead.
"""
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCIR302Handler:
    """
    Test-mode CIR302_Handler that captures exit codes instead of halting the system.
    This is used for testing adversarial scenarios without actually stopping the program.
    """

    def __init__(self):
        self.exit_code = None
        self.violations = []

    def handle_violation(self, error_type: str, error_details: str, log_list: list, pqc_cid=None, quantum_metadata=None, deterministic_timestamp: int=0):
        """
        Handle violation by capturing the exit code instead of halting.
        
        Args:
            error_type: Type of violation
            error_details: Details of the violation
            log_list: Log list for canonical logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        self.exit_code = 302
        self.violations.append({'error_type': error_type, 'error_details': error_details, 'pqc_cid': pqc_cid, 'timestamp': deterministic_timestamp})
        raise SystemExit(302)

    def was_triggered(self):
        """Check if CIR-302 was triggered."""
        return self.exit_code == 302

def test_cir302_handler():
    """Test the TestCIR302Handler implementation."""
    print('Testing TestCIR302Handler...')
    handler = TestCIR302Handler()
    try:
        handler.handle_violation(error_type='test_violation', error_details='Test violation for handler', log_list=[])
    except SystemExit:
        print('SystemExit caught as expected')
    print(f'CIR-302 triggered: {handler.was_triggered()}')
    print(f'Exit code: {handler.exit_code}')
    print(f'Violations captured: {len(handler.violations)}')
    print('✓ TestCIR302Handler test completed!')
if __name__ == '__main__':
    test_cir302_handler()
