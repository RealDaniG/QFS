"""
Test file with violations
"""
import datetime
import random
import time

def test_function():
    # This should be detected as a violation
    now = datetime.now()
    
    # This should also be detected as a violation
    rand_val = random.random()
    
    # This should also be detected as a violation
    current_time = time.time()
    
    # This should also be detected as a violation
    result = float("3.14")
    
    return result