import json

def generate_drill_ledger(output_path: str='drill_ledger.jsonl'):
    """
    Generate a deterministic reference ledger trace for zero-simulation replay drills.
    """
    entries = [{'entry_id': 'genesis', 'timestamp': 1000, 'entry_type': 'token_state', 'data': {'token_bundle': {'id': 'b1'}}, 'previous_hash': '0', 'entry_hash': 'h1', 'pqc_cid': 'c1', 'quantum_metadata': {}}, {'entry_id': 'evt_reward_1', 'timestamp': 1001, 'entry_type': 'reward_allocation', 'data': {'rewards': {'w1': '100'}}, 'previous_hash': 'h1', 'entry_hash': 'h2', 'pqc_cid': 'c2', 'quantum_metadata': {}}]
    with open(output_path, 'w') as f:
        for e in entries:
            f.write(json.dumps(e) + '\n')
    print(f'Generated drill ledger at {output_path} with {len(entries)} entries.')
if __name__ == '__main__':
    generate_drill_ledger()