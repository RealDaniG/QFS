import sys
import os

# Add the src directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from libs.CertifiedMath import CertifiedMath, BigNum128

def debug_ln():
    """Debug the ln function"""
    with CertifiedMath.LogContext() as log:
        # Test ln(2) 
        two = BigNum128.from_int(2)
        print(f"Input: {two.to_decimal_string()}")
        print(f"Input value: {two.value}")
        
        result = CertifiedMath.safe_ln(two, log)
        print(f"ln(2) = {result.to_decimal_string()}")
        print(f"ln(2) value: {result.value}")
        
        # Print log entries
        print("\nLog entries:")
        for i, entry in enumerate(log):
            print(f"  {i}: {entry}")

if __name__ == "__main__":
    debug_ln()