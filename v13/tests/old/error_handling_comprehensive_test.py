import sys

from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError, MathValidationError

def test_comprehensive_error_handling():
    """Comprehensive test for error handling in CertifiedMath."""
    print("=== Comprehensive Error Handling Test ===")
    
    # Test 1: Division by zero
    print("\n1. Testing division by zero...")
    cm = CertifiedMath([])
    a = BigNum128.from_string("10.0")
    b = BigNum128.from_string("0.0")
    
    try:
        result = cm.div(a, b, "div_by_zero_test", {"test": "div_by_zero"})
        div_by_zero_caught = False
    except MathValidationError as e:
        div_by_zero_caught = "division by zero" in str(e).lower()
    
    print(f"  Division by zero properly caught: {div_by_zero_caught}")
    
    # Test 2: Overflow in addition
    print("\n2. Testing overflow in addition...")
    cm = CertifiedMath([])
    
    # Create values that will definitely cause overflow
    max_val = BigNum128(BigNum128.MAX_VALUE)
    increment = BigNum128(BigNum128.SCALE)  # 1.0
    
    try:
        result = cm.add(max_val, increment, "overflow_test", {"test": "overflow"})
        overflow_caught = False
    except MathOverflowError as e:
        overflow_caught = True
    
    print(f"  Addition overflow properly caught: {overflow_caught}")
    
    # Test 3: Invalid input validation
    print("\n3. Testing invalid input validation...")
    
    # Test with None values (should be handled gracefully)
    try:
        # This should not be allowed by the type system, but let's check behavior
        result = cm.add(None, a, "none_test", {"test": "none"})
        none_input_caught = False
    except Exception as e:
        none_input_caught = True
    
    print(f"  None input properly handled: {none_input_caught}")
    
    # Test 4: Square root of negative number
    print("\n4. Testing square root of negative number...")
    negative = BigNum128.from_string("-1.0")
    
    try:
        result = cm.sqrt(negative, "negative_sqrt_test", {"test": "negative_sqrt"})
        negative_sqrt_caught = False
    except MathValidationError as e:
        negative_sqrt_caught = "negative" in str(e).lower() or "invalid" in str(e).lower()
    
    print(f"  Negative square root properly caught: {negative_sqrt_caught}")
    
    # Test 5: Log not created for failed operations
    print("\n5. Testing that logs are not created for failed operations...")
    log_list = []
    cm_with_log = CertifiedMath(log_list)
    
    # Perform a valid operation first
    valid_a = BigNum128.from_string("5.0")
    valid_b = BigNum128.from_string("3.0")
    valid_result = cm_with_log.add(valid_a, valid_b, "valid_test", {"test": "valid"})
    
    # Try an invalid operation
    try:
        invalid_result = cm_with_log.div(valid_a, BigNum128.from_string("0.0"), "invalid_test", {"test": "invalid"})
    except MathValidationError:
        pass  # Expected
    
    # Check that only the valid operation was logged
    log_count_after_valid_and_invalid = len(log_list)
    only_valid_logged = log_count_after_valid_and_invalid == 1 and log_list[0]["op_name"] == "add"
    
    print(f"  Only valid operations logged: {only_valid_logged}")
    print(f"  Log count: {log_count_after_valid_and_invalid}")
    
    # Test 6: Exponentiation with invalid base/exponent combinations
    print("\n6. Testing exponentiation edge cases...")
    
    # Test 0^0 (undefined)
    zero = BigNum128.from_string("0.0")
    try:
        result = cm.pow(zero, zero, "zero_power_zero_test", {"test": "0^0"})
        zero_power_zero_caught = False
    except MathValidationError as e:
        zero_power_zero_caught = True
    
    print(f"  0^0 properly caught: {zero_power_zero_caught}")
    
    # Test negative base with non-integer exponent
    negative_base = BigNum128.from_string("-2.0")
    fractional_exp = BigNum128.from_string("0.5")
    try:
        result = cm.pow(negative_base, fractional_exp, "neg_base_frac_exp_test", {"test": "neg^frac"})
        neg_base_frac_exp_caught = False
    except MathValidationError as e:
        neg_base_frac_exp_caught = True
    
    print(f"  Negative base with fractional exponent properly caught: {neg_base_frac_exp_caught}")
    
    # Summary
    print("\n=== Error Handling Test Summary ===")
    all_tests_passed = (
        div_by_zero_caught and 
        overflow_caught and 
        none_input_caught and 
        negative_sqrt_caught and 
        only_valid_logged and 
        zero_power_zero_caught and 
        neg_base_frac_exp_caught
    )
    
    print(f"All error handling tests passed: {all_tests_passed}")
    return all_tests_passed

if __name__ == "__main__":
    test_comprehensive_error_handling()