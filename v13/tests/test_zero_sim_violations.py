"""
Test file with Zero-Simulation violations to verify AST_ZeroSimChecker detects them.
This file should FAIL the Zero-Sim check.
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import math

class TestClass:
    pass
test_obj = TestClass()
test_obj.value = 42
pi = 3.14159
small_number = 1e-18
random_value = det_random()
current_time = det_time_now()
hash_value = hash('test')
squares = (x ** 2 for x in range(10))
import importlib
dynamic_module = importlib.import_module('os')

def test_function():
    test_dict = {'a': 1, 'b': 2, 'c': 3}
    for key in test_dict.keys():
        print(key)
    result = 5 + 3
    power_result = 2 ** 8

def another_function():
    pass
