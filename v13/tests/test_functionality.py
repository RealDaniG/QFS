import sys
import os
import inspect

# Ensure v13 root is in path for imports
sys.path.append(".")

from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.HSMF import HSMF, ValidationResult

print("Testing CertifiedMath functionality...")
# Instantiate CertifiedMath for instance method usage
cm = CertifiedMath()

a = BigNum128.from_int(2)
b = BigNum128.from_int(3)
print(f"Created a = {a.to_decimal_string()}")
print(f"Created b = {b.to_decimal_string()}")

with CertifiedMath.LogContext() as log:
    # Use instance method with explicit log_list
    result = cm.add(a, b, log_list=log)
    print(f"2 + 3 = {result.to_decimal_string()}")
    print(f"Log entries: {len(log)}")

with CertifiedMath.LogContext() as log:
    x = BigNum128.from_string("1.5")
    print(f"Created x = {x.to_decimal_string()}")
    # Use modern instance methods: exp and ln
    exp_result = cm.exp(x, log_list=log)
    print(f"e^1.5 = {exp_result.to_decimal_string()}")
    ln_result = cm.ln(a, log_list=log)
    print(f"ln(2) = {ln_result.to_decimal_string()}")
    print(f"Transcendental function log entries: {len(log)}")

print("CertifiedMath functionality test completed successfully!")

try:
    print("HSMF import successful")
    sig = inspect.signature(HSMF.validate_action_bundle)
    params = list(sig.parameters.keys())
    print(f"HSMF.validate_action_bundle parameters: {params}")
    if "drv_packet_sequence" in params:
        print("✅ HSMF correctly accepts drv_packet_sequence parameter")
    else:
        print("❌ HSMF missing drv_packet_sequence parameter")
except Exception as e:
    print(f"HSMF check failed: {e}")

print("All tests completed!")
