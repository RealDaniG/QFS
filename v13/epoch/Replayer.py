"""
epoch.Replayer.py - Full Epoch Replay Engine for QFS V13
Purpose: Reconstruct entire economic state of a single epoch from PQC audit logs
Zero-Simulation compliant, deterministic, auditable, supports BigNum128 balances
"""
import json
import hashlib
from typing import Any, Dict, List, Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.libs.PQC import PQC, ValidationResult
from v13.libs.BigNum128 import BigNum128

class EpochReplayer:
    """
    Replays a full epoch's PQC audit log and reconstructs token balances,
    treasury state, and intermediate HSMF metrics.
    
    Zero-Simulation compliant: reconstructs state from logs alone.
    """

    def __init__(self, pqc_log: List[Dict[str, Any]]):
        self.log = pqc_log
        self.validated = False
        self.token_state: Dict[str, BigNum128] = {}
        self.treasury: Dict[str, BigNum128] = {}
        self.hsmf_hashes: List[str] = []
        self.final_hash: Optional[str] = None

    def validate_log(self) -> ValidationResult:
        """
        Validates the PQC log chain and individual entries.
        """
        result = PQC.validate_log_chain(self.log)
        self.validated = result.is_valid
        return result

    def replay(self) -> ValidationResult:
        """
        Reconstructs economic state deterministically from audit log.
        Steps:
        1. Validate log integrity
        2. Apply token operations deterministically
        3. Update treasury balances
        4. Capture intermediate HSMF hashes
        5. Compute final epoch hash
        """
        if not self.validated:
            validation = self.validate_log()
            if not validation.is_valid:
                return validation
        for entry in sorted(self.log):
            operation = entry.get('operation')
            details = entry.get('details', {})
            if operation == 'token_mint':
                user = details['account']
                amount = BigNum128.from_string(details['amount'])
                self.token_state[user] = self.token_state.get(user, BigNum128.zero())
                self.token_state[user] = self.token_state[user] + amount
            elif operation == 'token_transfer':
                sender = details['from']
                receiver = details['to']
                amount = BigNum128.from_string(details['amount'])
                self.token_state[sender] = self.token_state.get(sender, BigNum128.zero())
                self.token_state[receiver] = self.token_state.get(receiver, BigNum128.zero())
                self.token_state[sender] = self.token_state[sender] - amount
                self.token_state[receiver] = self.token_state[receiver] + amount
            elif operation == 'treasury_update':
                account = details['account']
                amount = BigNum128.from_string(details['amount'])
                self.treasury[account] = self.treasury.get(account, BigNum128.zero())
                self.treasury[account] = self.treasury[account] + amount
            elif operation.startswith('hsmf_'):
                self.hsmf_hashes.append(entry.get('entry_hash'))
            elif operation in ['generate_keypair', 'sign_data', 'verify_signature']:
                continue
            else:
                pass
        self.final_hash = hashlib.sha3_512(PQC._canonical_serialize(self.log)).hexdigest()
        return ValidationResult(is_valid=True, error_message=None, quantum_metadata={'replayed_entries': len(self.log), 'final_epoch_hash': self.final_hash, 'token_accounts': len(self.token_state), 'treasury_accounts': len(self.treasury), 'hsmf_checkpoints': len(self.hsmf_hashes)})

    def export_state(self, path: str):
        """
        Exports token balances, treasury, HSMF hashes, and final epoch hash to JSON.
        """
        export_data = {'token_state': {k: str(v) for k, v in self.token_state.items()}, 'treasury': {k: str(v) for k, v in self.treasury.items()}, 'hsmf_hashes': self.hsmf_hashes, 'final_epoch_hash': self.final_hash}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, sort_keys=True)

    @staticmethod
    def replay_from_file(log_path: str, export_path: Optional[str]=None) -> ValidationResult:
        """
        Load a PQC log JSON file, replay it, and optionally export the reconstructed state.
        """
        with open(log_path, 'r', encoding='utf-8') as f:
            pqc_log = json.load(f)
        replayer = EpochReplayer(pqc_log)
        result = replayer.replay()
        if export_path and result.is_valid:
            replayer.export_state(export_path)
        return result
if __name__ == '__main__':
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
        export_file = sys.argv[2] if len(sys.argv) > 2 else 'replayed_epoch_state.json'
        validation = EpochReplayer.replay_from_file(log_file, export_file)
        if validation.is_valid:
            print('✅ Epoch replay successful')
            print(f"   Replayed entries: {validation.quantum_metadata['replayed_entries']}")
            print(f"   Token accounts: {validation.quantum_metadata['token_accounts']}")
            print(f"   Treasury accounts: {validation.quantum_metadata['treasury_accounts']}")
            print(f"   HSMF checkpoints: {validation.quantum_metadata['hsmf_checkpoints']}")
            print(f"   Final epoch hash: {validation.quantum_metadata['final_epoch_hash']}")
            print(f'   State exported to: {export_file}')
        else:
            print('❌ Epoch replay failed')
            print(f'   Error: {validation.error_message}')
            raise ZeroSimAbort(1)
    else:
        print('Usage: python epoch.Replayer.py <log_file.json> [export_file.json]')
        print('Example: python epoch.Replayer.py epoch_12345_log.json replayed_state.json')
