"""
manager.py - Keystore Abstraction for QFS
"""
import json
from typing import Optional

class KeystoreManager:
    """
    Manages secure storage of wallet keys.
    For DEV/TESTNET, using a local file with restrictive permissions (conceptually).
    """

    def __init__(self, key_file: str='.qfs_keystore_dev.json'):
        self.key_file = key_file
        self.store = {}
        self._load()

    def _load(self):
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'r', encoding='utf-8') as f:
                    self.store = json.load(f)
            except Exception:
                self.store = {}
        else:
            self.store = {}

    def _save(self):
        with open(self.key_file, 'w', encoding='utf-8') as f:
            json.dump(self.store, f, indent=2)

    def save_key(self, role: str, scope: str, private_key: str, public_address: str):
        """
        Save a key to the keystore.
        """
        key = f'{role}::{scope}'
        if key in self.store:
            if self.store[key]['public_address'] != public_address:
                raise ValueError('Key conflict for same role/scope')
        self.store[key] = {'private_key': private_key, 'public_address': public_address}
        self._save()

    def get_wallet(self, role: str, scope: str) -> Optional[dict]:
        key = f'{role}::{scope}'
        return self.store.get(key)

    def get_private_key(self, role: str, scope: str) -> Optional[str]:
        w = self.get_wallet(role, scope)
        return w.get('private_key') if w else None

    def exists(self, role: str, scope: str) -> bool:
        return f'{role}::{scope}' in self.store