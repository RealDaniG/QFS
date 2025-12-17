from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from v13.core.DRV_Packet import DRV_Packet, ValidationErrorCode

def run_drv_timestamp_tests():
    results = []
    try:
        log_list = []
        packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed_12345', log_list=log_list)
        result = packet.validate_ttsTimestamp()
        results.append(result.is_valid)
        assert result.is_valid, f'Valid timestamp rejected: {result.error_message}'
    except Exception as e:
        results.append(False)
        assert False, f'Unexpected error with valid timestamp: {str(e)}'
    try:
        log_list = []
        future_ts = 2 ** 63
        packet = DRV_Packet(ttsTimestamp=future_ts, sequence=1, seed='test_seed_12345', log_list=log_list)
        result = packet.validate_ttsTimestamp()
        results.append(not result.is_valid)
        assert not result.is_valid, 'Future timestamp incorrectly accepted'
        assert result.error_code == ValidationErrorCode.INVALID_TTS_TIMESTAMP, f'Wrong error code: {result.error_code}'
    except Exception as e:
        results.append(False)
        assert False, f'Unexpected error with future timestamp: {str(e)}'
    try:
        log_list = []
        packet = DRV_Packet(ttsTimestamp=-1, sequence=1, seed='test_seed_12345', log_list=log_list)
        results.append(False)
        assert False, 'Negative timestamp should have been rejected during initialization'
    except ValueError:
        results.append(True)
    except Exception as e:
        results.append(False)
        assert False, f'Unexpected error with negative timestamp: {str(e)}'
    return results
if __name__ == '__main__':
    try:
        test_results = run_drv_timestamp_tests()
        if all(test_results):
            raise ZeroSimAbort(0)
        else:
            raise ZeroSimAbort(1)
    except AssertionError as e:
        raise ZeroSimAbort(1)