"""
deterministic_hash.py - Deterministic Hashing Functions for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable
"""
import json
import hashlib
from typing import Any, Dict, List, Union
from CertifiedMath import BigNum128

def deterministic_hash(data: Any) -> str:
    """
    Generate a deterministic SHA-256 hash of any data structure.
    
    Args:
        data: Data to hash (can be any JSON-serializable structure)
        
    Returns:
        str: SHA-256 hash as hexadecimal string
    """
    serialized = json.dumps(data, sort_keys=True, separators=(',', ':'), default=_serialize_object)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def _serialize_object(obj: Any) -> Any:
    """
    Custom serializer for objects that aren't JSON serializable by default.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Any: JSON-serializable representation of the object
    """
    if hasattr(obj, 'to_decimal_string'):
        return obj.to_decimal_string()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (set, frozenset)):
        try:
            return sorted(list(obj))
        except TypeError:
            return list(obj)
    else:
        return str(obj)

def deterministic_uuid(input_data: str) -> str:
    """
    Generate a deterministic UUID-like string from input data.
    
    Args:
        input_data: String to generate UUID from
        
    Returns:
        str: Deterministic UUID-like hexadecimal string
    """
    hash_bytes = hashlib.sha256(input_data.encode('utf-8')).digest()
    uuid_bytes = hash_bytes[:16]
    return uuid_bytes.hex()

def hash_token_state_bundle(bundle: Any) -> str:
    """
    Generate deterministic hash of a TokenStateBundle.
    
    Args:
        bundle: TokenStateBundle object
        
    Returns:
        str: SHA-256 hash as hexadecimal string
    """
    bundle_data = bundle.to_dict(include_signature=False)
    return deterministic_hash(bundle_data)

def hash_ledger_entry(entry: Any) -> str:
    """
    Generate deterministic hash of a ledger entry.
    
    Args:
        entry: Ledger entry object
        
    Returns:
        str: SHA-256 hash as hexadecimal string
    """
    entry_data = {'entry_id': entry.entry_id, 'timestamp': entry.timestamp, 'entry_type': entry.entry_type, 'data': entry.data, 'previous_hash': entry.previous_hash, 'pqc_cid': entry.pqc_cid, 'quantum_metadata': entry.quantum_metadata}
    return deterministic_hash(entry_data)