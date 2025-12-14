import sys
import os

# Add the libs directory to the path

# Run the test
if __name__ == "__main__":
    try:
        from v13.tests.test_hsmf_certifiedmath_integration import test_hsmf_with_certified_math, test_public_api
        print("=== QFS V13 HSMF & CertifiedMath Integration Test ===")
        
        # Test CertifiedMath public API
        api_success = test_public_api()
        
        # Test HSMF with CertifiedMath
        hsmf_success = test_hsmf_with_certified_math()
        
        if api_success and hsmf_success:
            print("\n=== ALL TESTS PASSED ===")
            sys.exit(0)
        else:
            print("\n=== SOME TESTS FAILED ===")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to run tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)