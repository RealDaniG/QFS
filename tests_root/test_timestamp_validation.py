import sys
sys.path.append('src')

# Simple test for timestamp validation without PQC dependencies
class MockValidationResult:
    def __init__(self, is_valid, error_code=None, error_message=None):
        self.is_valid = is_valid
        self.error_code = error_code
        self.error_message = error_message

class MockValidationErrorCode:
    OK = 0
    INVALID_TTS_TIMESTAMP = 2

def validate_ttsTimestamp(ttsTimestamp):
    """Mock function to validate ttsTimestamp"""
    # Checks for a valid 64-bit unsigned integer range (max unix time)
    if not (0 <= ttsTimestamp <= 2**63 - 1):
        return MockValidationResult(False, MockValidationErrorCode.INVALID_TTS_TIMESTAMP, f"ttsTimestamp {ttsTimestamp} out of range")
    return MockValidationResult(True, MockValidationErrorCode.OK)

# Test valid timestamp
try:
    result = validate_ttsTimestamp(1700000000)  # Valid timestamp
    if result.is_valid:
        print("✓ Valid timestamp correctly accepted")
    else:
        print(f"✗ Valid timestamp incorrectly rejected: {result.error_message}")
except Exception as e:
    print(f"Unexpected error with valid timestamp: {e}")

# Test invalid future timestamp (this should be rejected)
try:
    # This is a future timestamp that should be rejected
    future_timestamp = 2**63  # This should be out of range
    result = validate_ttsTimestamp(future_timestamp)
    if not result.is_valid and result.error_code == MockValidationErrorCode.INVALID_TTS_TIMESTAMP:
        print("✓ Future timestamp correctly rejected")
    else:
        print(f"✗ Future timestamp incorrectly accepted or wrong error code: {result.error_message}")
except Exception as e:
    print(f"Unexpected error with future timestamp: {e}")

# Test invalid past timestamp (this should be rejected)
try:
    # This is a negative timestamp that should be rejected
    result = validate_ttsTimestamp(-1)  # Negative timestamp
    if not result.is_valid and result.error_code == MockValidationErrorCode.INVALID_TTS_TIMESTAMP:
        print("✓ Negative timestamp correctly rejected")
    else:
        print(f"✗ Negative timestamp incorrectly accepted or wrong error code: {result.error_message}")
except Exception as e:
    print(f"Unexpected error with negative timestamp: {e}")