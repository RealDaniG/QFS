
"""
Golden Fail File for Zero-Sim Checker.
This file SHOULD contain violations (imported os, time, float math).
"""
import os
import time
import random

def unsafe_calculation() -> float:
    # Forbidden call
    t = time.time()
    
    # Forbidden import usage
    r = random.random()
    
    # Forbidden float literal
    x = 1.0 + 2.5
    
    # Forbidden comprehension (not sorted)
    d = {"b": 1, "a": 2}
    vals = [d[k] for k in d]
    
    return t + r + x
