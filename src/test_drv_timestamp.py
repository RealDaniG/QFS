from core.DRV_Packet import DRV_Packet, ValidationErrorCode

# Create a log list for the operations
log_list = []

# Test valid timestamp
try:
    packet = DRV_Packet(
        ttsTimestamp=1700000000,  # Valid timestamp
        sequence=1,
        seed="test_seed_12345",
        log_list=log_list
    )
    result = packet.validate_ttsTimestamp()
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
    packet = DRV_Packet(
        ttsTimestamp=future_timestamp,
        sequence=1,
        seed="test_seed_12345",
        log_list=log_list
    )
    result = packet.validate_ttsTimestamp()
    if not result.is_valid and result.error_code == ValidationErrorCode.INVALID_TTS_TIMESTAMP:
        print("✓ Future timestamp correctly rejected")
    else:
        print(f"✗ Future timestamp incorrectly accepted or wrong error code: {result.error_message}")
except Exception as e:
    print(f"Unexpected error with future timestamp: {e}")

# Test invalid past timestamp (this should be rejected)
try:
    # This is a negative timestamp that should be rejected
    packet = DRV_Packet(
        ttsTimestamp=-1,  # Negative timestamp
        sequence=1,
        seed="test_seed_12345",
        log_list=log_list
    )
    # This should raise a ValueError during initialization
    print("✗ Negative timestamp should have been rejected during initialization")
except ValueError:
    print("✓ Negative timestamp correctly rejected during initialization")
except Exception as e:
    print(f"Unexpected error with negative timestamp: {e}")