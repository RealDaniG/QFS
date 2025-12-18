"""
verify_reward_proof.py - E-003: Client-side Verification Tool

Verifies the Zero-Sim Proof returned by the GET /explain/reward/{tx_id} endpoint.
Ensures that the explanation provided is cryptographically bound to the ledger state.
"""
import json
import hashlib
import argparse

def verify_proof(proof_data: dict) -> bool:
    """
    Verifies the cryptographic integrity of the proof.
    """
    try:
        entry_data = proof_data.get('entry_data_snapshot')
        previous_hash = proof_data.get('input_state_hash')
        timestamp = proof_data.get('timestamp')
        expected_hash = proof_data.get('output_state_hash')
        if entry_data is None or previous_hash is None or expected_hash is None:
            print('[ERROR] Missing required proof fields (entry_data_snapshot, input_state_hash, output_state_hash).')
            return False
        data_to_hash = {'entry_data': entry_data, 'previous_hash': previous_hash, 'timestamp': timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        calculated_hash = hashlib.sha256(data_json.encode('utf-8')).hexdigest()
        print(f'Calculated Hash: {calculated_hash}')
        print(f'Expected Hash:   {expected_hash}')
        if calculated_hash == expected_hash:
            print('[SUCCESS] Proof Verified! The data is authentic and derived from the ledger.')
            return True
        else:
            print('[FAILURE] Hash mismatch! The data may have been tampered with.')
            return False
    except Exception as e:
        print(f'[ERROR] Verification failed with exception: {e}')
        return False

def main():
    parser = argparse.ArgumentParser(description='Verify a QFS Reward Explanation Proof')
    parser.add_argument('proof_file', help='Path to JSON file containing the proof/response')
    args = parser.parse_args()
    try:
        with open(args.proof_file, 'r') as f:
            data = json.load(f)
        proof = None
        if 'explanation' in data and 'zero_sim_proof' in data['explanation']:
            proof = data['explanation']['zero_sim_proof']
        elif 'input_state_hash' in data:
            proof = data
        elif 'zero_sim_proof' in data:
            proof = data['zero_sim_proof']
        elif 'proof' in data:
            proof = data['proof']
        if not proof:
            print("[ERROR] Could not locate proof object in JSON. Expected 'explanation.zero_sim_proof' or similar.")
            raise ZeroSimAbort(1)
        print(f"Verifying proof for Timestamp: {proof.get('timestamp')}")
        success = verify_proof(proof)
        if success:
            raise ZeroSimAbort(0)
        else:
            raise ZeroSimAbort(1)
    except FileNotFoundError:
        print(f'[ERROR] File not found: {args.proof_file}')
        raise ZeroSimAbort(1)
    except json.JSONDecodeError:
        print(f'[ERROR] Invalid JSON in file: {args.proof_file}')
        raise ZeroSimAbort(1)
if __name__ == '__main__':
    main()
