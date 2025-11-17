"""
Example usage of the PQC library for QFS V13.

This example demonstrates how to use the PQC library for signing and verifying
data in a quantum-resistant manner, compliant with QFS V13 requirements.
"""

import sys
import os

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from PQC import PQC, generate_keypair, sign_data, verify_signature


def main():
    print("QFS V13 PQC Library Example")
    print("=" * 30)
    
    # Generate a keypair
    print("1. Generating PQC keypair...")
    keypair = generate_keypair()
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    print(f"   Private Key: {private_key[:32]}...")  # Show first 32 chars
    print(f"   Public Key: {public_key}")
    
    # Data to sign (representing a transaction or operation)
    data = {
        "operation": "transfer",
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 1500000000000000000,  # 1.5 in fixed-point
        "timestamp": 1700000000,
        "nonce": 42
    }
    
    print("\n2. Data to sign:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    # Sign the data
    print("\n3. Signing data with private key...")
    signature = sign_data(data, private_key)
    print(f"   Signature: {signature[:64]}...")  # Show first 64 chars
    
    # Verify the signature
    print("\n4. Verifying signature with private key...")
    is_valid = verify_signature(data, signature, private_key)
    print(f"   Signature Valid: {is_valid}")
    
    # Demonstrate tamper detection
    print("\n5. Testing tamper detection...")
    tampered_data = {**data, "amount": 2000000000000000000}  # Changed amount to 2.0
    is_valid_tampered = verify_signature(tampered_data, signature, private_key)
    print(f"   Tampered Data Signature Valid: {is_valid_tampered}")
    
    # Using the PQC class directly
    print("\n6. Using PQC class directly...")
    pqc = PQC()
    
    # Different data for this example
    operation_data = {
        "operation": "multiply",
        "operands": [1234567890000000000, 987654321000000000],  # 1.23456789 * 0.987654321
        "timestamp": 1700000001
    }
    
    # Sign with the class
    class_signature = pqc.sign(operation_data, private_key)
    print(f"   Class Signature: {class_signature[:64]}...")
    
    # Verify with the class
    class_verify = pqc.verify(operation_data, class_signature, private_key)
    print(f"   Class Verification: {class_verify}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()