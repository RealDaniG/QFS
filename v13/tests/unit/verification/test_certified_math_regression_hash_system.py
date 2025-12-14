"""
Reference hash system for CertifiedMath operations.
This script generates and stores SHA256 hashes for deterministic outputs to ensure consistency.
"""

import sys
import os
import json
import hashlib

# Add the libs directory to the path

from CertifiedMath import CertifiedMath, BigNum128

def generate_reference_hashes():
    """Generate reference hashes for common CertifiedMath operations."""
    print("Generating reference hashes for CertifiedMath operations...")
    
    # Reference hash database
    reference_hashes = {}
    
    # Test case 1: Basic arithmetic operations
    log = []
    math = CertifiedMath(log)
    
    # Addition: 1.5 + 2.5 = 4.0
    a = BigNum128.from_string("1.5")
    b = BigNum128.from_string("2.5")
    result = math.add(a, b, pqc_cid="REF_HASH_001")
    hash_value = math.get_log_hash()
    reference_hashes["add_1.5_2.5"] = {
        "inputs": {"a": "1.5", "b": "2.5"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "add"
    }
    
    # Subtraction: 5.0 - 3.0 = 2.0
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("5.0")
    b = BigNum128.from_string("3.0")
    result = math.sub(a, b, pqc_cid="REF_HASH_002")
    hash_value = math.get_log_hash()
    reference_hashes["sub_5.0_3.0"] = {
        "inputs": {"a": "5.0", "b": "3.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "sub"
    }
    
    # Multiplication: 2.0 * 3.0 = 6.0
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("2.0")
    b = BigNum128.from_string("3.0")
    result = math.mul(a, b, pqc_cid="REF_HASH_003")
    hash_value = math.get_log_hash()
    reference_hashes["mul_2.0_3.0"] = {
        "inputs": {"a": "2.0", "b": "3.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "mul"
    }
    
    # Division: 8.0 / 2.0 = 4.0
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("8.0")
    b = BigNum128.from_string("2.0")
    result = math.div(a, b, pqc_cid="REF_HASH_004")
    hash_value = math.get_log_hash()
    reference_hashes["div_8.0_2.0"] = {
        "inputs": {"a": "8.0", "b": "2.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "div"
    }
    
    # Square root: sqrt(16.0) = 4.0
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("16.0")
    result = math.sqrt(a, pqc_cid="REF_HASH_005")
    hash_value = math.get_log_hash()
    reference_hashes["sqrt_16.0"] = {
        "inputs": {"a": "16.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "sqrt"
    }
    
    # Exponential: exp(1.0) ≈ e
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("1.0")
    result = math.exp(a, pqc_cid="REF_HASH_006")
    hash_value = math.get_log_hash()
    reference_hashes["exp_1.0"] = {
        "inputs": {"a": "1.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "exp"
    }
    
    # Natural logarithm: ln(e) = 1.0
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("2.718281828459045235")  # Approximation of e
    result = math.ln(a, pqc_cid="REF_HASH_007")
    hash_value = math.get_log_hash()
    reference_hashes["ln_e"] = {
        "inputs": {"a": "2.718281828459045235"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "ln"
    }
    
    # Phi series: phi_series(0.5)
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("0.5")
    result = math.phi_series(a, pqc_cid="REF_HASH_008")
    hash_value = math.get_log_hash()
    reference_hashes["phi_series_0.5"] = {
        "inputs": {"a": "0.5"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "phi_series"
    }
    
    # Two to the power: 2^2 = 4
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("2.0")
    result = math.two_to_the_power(a, pqc_cid="REF_HASH_009")
    hash_value = math.get_log_hash()
    reference_hashes["two_to_the_power_2.0"] = {
        "inputs": {"a": "2.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "two_to_the_power"
    }
    
    # Power: 2^3 = 8
    log = []
    math = CertifiedMath(log)
    base = BigNum128.from_string("2.0")
    exponent = BigNum128.from_string("3.0")
    result = math.pow(base, exponent, pqc_cid="REF_HASH_010")
    hash_value = math.get_log_hash()
    reference_hashes["pow_2.0_3.0"] = {
        "inputs": {"base": "2.0", "exponent": "3.0"},
        "result": result.to_decimal_string(),
        "hash": hash_value,
        "operation": "pow"
    }
    
    # Complex operation chain
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string("1.234567")
    b = BigNum128.from_string("2.345678")
    result1 = math.add(a, b, pqc_cid="REF_HASH_011")
    result2 = math.mul(result1, a, pqc_cid="REF_HASH_011")
    result3 = math.exp(result2, pqc_cid="REF_HASH_011")
    hash_value = math.get_log_hash()
    reference_hashes["complex_chain"] = {
        "inputs": {"a": "1.234567", "b": "2.345678"},
        "operations": ["add", "mul", "exp"],
        "final_result": result3.to_decimal_string(),
        "hash": hash_value,
        "operation": "complex_chain"
    }
    
    return reference_hashes

def save_reference_hashes(reference_hashes):
    """Save reference hashes to a JSON file."""
    hash_file = os.path.join(os.path.dirname(__file__), 'certified_math_reference_hashes.json')
    with open(hash_file, 'w') as f:
        json.dump(reference_hashes, f, indent=2)
    print(f"Reference hashes saved to: {hash_file}")
    return hash_file

def validate_reference_hashes(reference_hashes):
    """Validate that reference hashes are consistent."""
    print("Validating reference hash consistency...")
    
    # Re-execute operations to verify hashes
    for key, data in reference_hashes.items():
        log = []
        math = CertifiedMath(log)
        
        if data["operation"] == "add":
            a = BigNum128.from_string(data["inputs"]["a"])
            b = BigNum128.from_string(data["inputs"]["b"])
            result = math.add(a, b, pqc_cid="REF_HASH_001")
        elif data["operation"] == "sub":
            a = BigNum128.from_string(data["inputs"]["a"])
            b = BigNum128.from_string(data["inputs"]["b"])
            result = math.sub(a, b, pqc_cid="REF_HASH_002")
        elif data["operation"] == "mul":
            a = BigNum128.from_string(data["inputs"]["a"])
            b = BigNum128.from_string(data["inputs"]["b"])
            result = math.mul(a, b, pqc_cid="REF_HASH_003")
        elif data["operation"] == "div":
            a = BigNum128.from_string(data["inputs"]["a"])
            b = BigNum128.from_string(data["inputs"]["b"])
            result = math.div(a, b, pqc_cid="REF_HASH_004")
        elif data["operation"] == "sqrt":
            a = BigNum128.from_string(data["inputs"]["a"])
            result = math.sqrt(a, pqc_cid="REF_HASH_005")
        elif data["operation"] == "exp":
            a = BigNum128.from_string(data["inputs"]["a"])
            result = math.exp(a, pqc_cid="REF_HASH_006")
        elif data["operation"] == "ln":
            a = BigNum128.from_string(data["inputs"]["a"])
            result = math.ln(a, pqc_cid="REF_HASH_007")
        elif data["operation"] == "phi_series":
            a = BigNum128.from_string(data["inputs"]["a"])
            result = math.phi_series(a, pqc_cid="REF_HASH_008")
        elif data["operation"] == "two_to_the_power":
            a = BigNum128.from_string(data["inputs"]["a"])
            result = math.two_to_the_power(a, pqc_cid="REF_HASH_009")
        elif data["operation"] == "pow":
            base = BigNum128.from_string(data["inputs"]["base"])
            exponent = BigNum128.from_string(data["inputs"]["exponent"])
            result = math.pow(base, exponent, pqc_cid="REF_HASH_010")
        elif data["operation"] == "complex_chain":
            a = BigNum128.from_string(data["inputs"]["a"])
            b = BigNum128.from_string(data["inputs"]["b"])
            result1 = math.add(a, b, pqc_cid="REF_HASH_011")
            result2 = math.mul(result1, a, pqc_cid="REF_HASH_011")
            result = math.exp(result2, pqc_cid="REF_HASH_011")
        
        # Verify hash consistency
        computed_hash = math.get_log_hash()
        if computed_hash != data["hash"]:
            raise ValueError(f"Hash mismatch for {key}: expected {data['hash']}, got {computed_hash}")
    
    print("  [PASS] All reference hashes validated successfully")

def run_reference_hash_system():
    """Run the reference hash system generation and validation."""
    print("Running CertifiedMath Reference Hash System...")
    print("=" * 50)
    
    # Generate reference hashes
    reference_hashes = generate_reference_hashes()
    
    # Save reference hashes
    hash_file = save_reference_hashes(reference_hashes)
    
    # Validate reference hashes
    validate_reference_hashes(reference_hashes)
    
    print("=" * 50)
    print(f"[SUCCESS] Reference hash system completed!")
    print(f"Generated {len(reference_hashes)} reference hashes")
    print(f"Hash database saved to: {hash_file}")
    
    return reference_hashes

if __name__ == "__main__":
    run_reference_hash_system()