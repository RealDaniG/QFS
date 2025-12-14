"""
Simple test file with Zero-Simulation violations in economics module.
"""

# Float literal - should be flagged
pi = 3.14159

# Scientific notation float - should be flagged
small_number = 1e-18

def test_function():
    # Direct arithmetic - should be flagged in deterministic modules
    result = 5 + 3
    
    # Power operator - should be flagged
    power_result = 2 ** 8