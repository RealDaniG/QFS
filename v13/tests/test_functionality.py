from CertifiedMath import BigNum128, CertifiedMath

# Test basic arithmetic
print("Testing CertifiedMath functionality...")

# Create numbers
a = BigNum128.from_int(2)
b = BigNum128.from_int(3)
print(f"Created a = {a.to_decimal_string()}")
print(f"Created b = {b.to_decimal_string()}")

# Test addition
with CertifiedMath.LogContext() as log:
    result = CertifiedMath.add(a, b, log)
    print(f"2 + 3 = {result.to_decimal_string()}")
    print(f"Log entries: {len(log)}")

# Test transcendental functions
with CertifiedMath.LogContext() as log:
    x = CertifiedMath.from_string("1.5")
    print(f"Created x = {x.to_decimal_string()}")
    
    # Test exp function
    exp_result = CertifiedMath.safe_exp(x, log)
    print(f"e^1.5 = {exp_result.to_decimal_string()}")
    
    # Test ln function
    ln_result = CertifiedMath.safe_ln(a, log)  # ln(2)
    print(f"ln(2) = {ln_result.to_decimal_string()}")
    
    print(f"Transcendental function log entries: {len(log)}")

print("CertifiedMath functionality test completed successfully!")

# Test HSMF import
try:
    from HSMF import HSMF, ValidationResult
    print("HSMF import successful")
    
    # Check if the function signature is correct
    import inspect
    sig = inspect.signature(HSMF.validate_action_bundle)
    params = list(sig.parameters.keys())
    print(f"HSMF.validate_action_bundle parameters: {params}")
    
    # Check if drv_packet_sequence is in the parameters
    if 'drv_packet_sequence' in params:
        print("✅ HSMF correctly accepts drv_packet_sequence parameter")
    else:
        print("❌ HSMF missing drv_packet_sequence parameter")
        
except Exception as e:
    print(f"HSMF import failed: {e}")

print("All tests completed!")