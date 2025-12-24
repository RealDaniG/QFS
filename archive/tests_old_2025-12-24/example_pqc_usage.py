"""
Example usage of the PQC library for QFS V13.

This example demonstrates how to use the PQC library for signing and verifying
data in a quantum-resistant manner, compliant with QFS V13 requirements.
"""
from PQC import PQC, generate_keypair, sign_data, verify_signature

def main():
    print('QFS V13 PQC Library Example')
    print('=' * 30)
    print('1. Generating PQC keypair...')
    keypair = generate_keypair()
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    print(f'   Private Key: {private_key[:32]}...')
    print(f'   Public Key: {public_key}')
    data = {'operation': 'transfer', 'from_account': 'ACC001', 'to_account': 'ACC002', 'amount': 1500000000000000000, 'timestamp': 1700000000, 'nonce': 42}
    print('\n2. Data to sign:')
    for key, value in data.items():
        print(f'   {key}: {value}')
    print('\n3. Signing data with private key...')
    signature = sign_data(data, private_key)
    print(f'   Signature: {signature[:64]}...')
    print('\n4. Verifying signature with private key...')
    is_valid = verify_signature(data, signature, private_key)
    print(f'   Signature Valid: {is_valid}')
    print('\n5. Testing tamper detection...')
    tampered_data = {**data, 'amount': 2000000000000000000}
    is_valid_tampered = verify_signature(tampered_data, signature, private_key)
    print(f'   Tampered Data Signature Valid: {is_valid_tampered}')
    print('\n6. Using PQC class directly...')
    pqc = PQC()
    operation_data = {'operation': 'multiply', 'operands': [1234567890000000000, 987654321000000000], 'timestamp': 1700000001}
    class_signature = pqc.sign(operation_data, private_key)
    print(f'   Class Signature: {class_signature[:64]}...')
    class_verify = pqc.verify(operation_data, class_signature, private_key)
    print(f'   Class Verification: {class_verify}')
    print('\nExample completed successfully!')
if __name__ == '__main__':
    main()