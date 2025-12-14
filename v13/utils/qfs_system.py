"""
QFS System - Unified Deterministic Hashing for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready.

This module provides system-wide deterministic hashing functionality
that combines audit trails from all QFS V13 components.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional

# Import audit hash functions from all modules
try:
    from PQC import get_pqc_audit_hash
except ImportError:
    def get_pqc_audit_hash() -> str:
        return "0" * 64  # Return a default hash if PQC module is not available

try:
    from DRV_Packet import get_drv_packet_audit_hash
except ImportError:
    def get_drv_packet_audit_hash() -> str:
        return "0" * 64  # Return a default hash if DRV_Packet module is not available

try:
    # CertifiedMath uses a different approach - it's instance-based
    # We'll handle this differently
    pass
except ImportError:
    pass


def get_system_audit_hash(
    certified_math_logs: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate a deterministic SHA-256 hash of the entire QFS system audit state.
    
    This function combines audit hashes from all QFS V13 components:
    - PQC operations
    - DRV_Packet events
    - CertifiedMath operations (if provided)
    
    Args:
        certified_math_logs: Optional list of CertifiedMath log entries
        
    Returns:
        Hex string of the SHA-256 hash representing the system state
    """
    # Get audit hashes from all modules
    pqc_hash = get_pqc_audit_hash()
    drv_packet_hash = get_drv_packet_audit_hash()
    
    # For CertifiedMath, we need to hash the provided logs
    if certified_math_logs is not None:
        # Sort the logs by log_index for deterministic hashing
        sorted_logs = sorted(certified_math_logs, key=lambda x: x.get('log_index', 0))
        certified_math_hash = hashlib.sha256(
            json.dumps(sorted_logs, sort_keys=True).encode('utf-8')
        ).hexdigest()
    else:
        certified_math_hash = "0" * 64  # Default hash if no logs provided
    
    # Combine all hashes into a single deterministic structure
    system_state = {
        "pqc_audit_hash": pqc_hash,
        "drv_packet_audit_hash": drv_packet_hash,
        "certified_math_audit_hash": certified_math_hash,
        "timestamp": "system_hash"  # Placeholder to ensure consistent structure
    }
    
    # Generate deterministic hash of the combined system state
    serialized_system_state = json.dumps(system_state, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized_system_state.encode('utf-8')).hexdigest()


def clear_all_audit_logs():
    """
    Clear audit logs from all QFS V13 components.
    
    This function clears the audit logs from:
    - PQC operations
    - DRV_Packet events
    """
    try:
        from PQC import clear_pqc_audit_log
        clear_pqc_audit_log()
    except ImportError:
        pass
    
    try:
        from DRV_Packet import clear_drv_packet_audit_log
        clear_drv_packet_audit_log()
    except ImportError:
        pass


# Example usage
if __name__ == "__main__":
    # Generate system audit hash
    system_hash = get_system_audit_hash()
    print(f"QFS System Audit Hash: {system_hash}")
    
    # Clear all audit logs
    clear_all_audit_logs()
    print("All audit logs cleared")