"""
Test file with Zero-Simulation violations.
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import math

def test_function():
    x = 3.14
    y = det_random()
    z = det_time_now()
    w = math.sqrt(2.0)
    return x + y + z + w

def another_test():
    return (1, 2)