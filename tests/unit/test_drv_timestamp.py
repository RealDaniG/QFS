from core.DRV_Packet import DRV_Packet, ValidationErrorCode

def run_drv_timestamp_tests():
    results = []

    # Test valid timestamp
    try:
        log_list = []
        packet = DRV_Packet(
            ttsTimestamp=1700000000,  # Valid timestamp
            sequence=1,
            seed="test_seed_12345",
            log_list=log_list
        )
        result = packet.validate_ttsTimestamp()
        results.append(result.is_valid)
        assert result.is_valid, f"Valid timestamp rejected: {result.error_message}"
    except Exception as e:
        results.append(False)
        # In a real test runner we might want to re-raise or log differently, 
        # but for this strict pattern we assert False with the message
        assert False, f"Unexpected error with valid timestamp: {str(e)}"

    # Test future timestamp
    try:
        log_list = []
        future_ts = 2**63  # Local variable only
        packet = DRV_Packet(
            ttsTimestamp=future_ts,
            sequence=1,
            seed="test_seed_12345",
            log_list=log_list
        )
        result = packet.validate_ttsTimestamp()
        results.append(not result.is_valid)
        assert not result.is_valid, "Future timestamp incorrectly accepted"
        assert result.error_code == ValidationErrorCode.INVALID_TTS_TIMESTAMP, f"Wrong error code: {result.error_code}"
    except Exception as e:
        results.append(False)
        assert False, f"Unexpected error with future timestamp: {str(e)}"

    # Test invalid past timestamp
    try:
        log_list = []
        packet = DRV_Packet(
            ttsTimestamp=-1,  # Negative timestamp
            sequence=1,
            seed="test_seed_12345",
            log_list=log_list
        )
        # Should raise ValueError during init
        results.append(False) # Should not reach here
        assert False, "Negative timestamp should have been rejected during initialization"
    except ValueError:
        results.append(True) # Correctly rejected
    except Exception as e:
        results.append(False)
        assert False, f"Unexpected error with negative timestamp: {str(e)}"

    return results

if __name__ == "__main__":
    # Simple execution wrapper for manual testing if needed, 
    # but the core logic is now in the deterministic function.
    try:
        test_results = run_drv_timestamp_tests()
        if all(test_results):
            # We can exit with 0 for success, but avoid printing "Success" if strict silence is needed.
            # For now, a simple exit code is the most deterministic signal.
            import sys
            sys.exit(0)
        else:
            import sys
            sys.exit(1)
    except AssertionError as e:
        # If assertions fail, we exit with error
        import sys
        sys.exit(1)