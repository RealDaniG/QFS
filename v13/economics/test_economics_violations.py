"""
Test file with Zero-Simulation violations in economics module.
This file should FAIL the Zero-Sim check.
"""

import random
import time
import math

# Global attribute mutation
class TestClass:
    pass

test_obj = TestClass()

# This should be flagged as global attribute mutation
test_obj.value = 42

# Float literal - should be flagged
pi = 3.14159

# Scientific notation float - should be flagged
small_number = 1e-18

# Forbidden function calls
random_value = random.random()
current_time = time.time()

# Hash function - should be flagged
hash_value = hash("test")

# Generator expression - should be flagged in deterministic modules
squares = (x**2 for x in range(10))

# Dynamic import - should be flagged
import importlib
dynamic_module = importlib.import_module("os")

def test_function():
    # Unsorted dict iteration - should be flagged
    test_dict = {"a": 1, "b": 2, "c": 3}
    for key in test_dict.keys():
        print(key)
    
    # Direct arithmetic - should be flagged in deterministic modules
    result = 5 + 3
    
    # Power operator - should be flagged
    power_result = 2 ** 8

# Function without required deterministic parameters
def another_function():
    pass