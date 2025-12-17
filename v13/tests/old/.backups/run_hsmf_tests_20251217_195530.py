from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
if __name__ == '__main__':
    try:
        from v13.tests.test_hsmf_certifiedmath_integration import test_hsmf_with_certified_math, test_public_api
        print('=== QFS V13 HSMF & CertifiedMath Integration Test ===')
        api_success = test_public_api()
        hsmf_success = test_hsmf_with_certified_math()
        if api_success and hsmf_success:
            print('\n=== ALL TESTS PASSED ===')
            raise ZeroSimAbort(0)
        else:
            print('\n=== SOME TESTS FAILED ===')
            raise ZeroSimAbort(1)
    except Exception as e:
        print(f'Failed to run tests: {e}')
        import traceback
        traceback.print_exc()
        raise ZeroSimAbort(1)