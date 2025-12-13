"""Debug BLOCK_TIME_SECONDS value"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from libs.economics.economic_constants import BLOCK_TIME_SECONDS

print(f"BLOCK_TIME_SECONDS = {BLOCK_TIME_SECONDS}")
print(f"BLOCK_TIME_SECONDS.value = {BLOCK_TIME_SECONDS.value}")
print(f"type(BLOCK_TIME_SECONDS.value) = {type(BLOCK_TIME_SECONDS.value)}")

# Test multiplication
voting_duration_blocks = 100
result = voting_duration_blocks * BLOCK_TIME_SECONDS.value
print(f"100 * BLOCK_TIME_SECONDS.value = {result}")
print(f"type(result) = {type(result)}")
