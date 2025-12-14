"""
Test file with Zero-Simulation violations.
"""
import random
import time
import math
from datetime import datetime

def test_function():
    # This should trigger violations
    x = 3.14  # Float literal
    y = random.random()  # Random function
    z = time.time()  # Time function
    w = math.sqrt(2.0)  # Math function
    return x + y + z + w

def another_test():
    # This should be clean
    # Example of proper import (commented out for testing)
    # from src.libs.CertifiedMath import BigNum128
    # a = BigNum128.from_int(1)
    # b = BigNum128.from_int(2)
    # return a, b
    return 1, 2