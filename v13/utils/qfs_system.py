"""
QFS System - Unified Deterministic Hashing for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready.

This module provides system-wide deterministic hashing functionality
that combines audit trails from all QFS V13 components.
"""

import json
import hashlib
import logging
from typing import Dict, Any, List, Optional

try:
    from PQC import get_pqc_audit_hash
except ImportError:

    def get_pqc_audit_hash() -> str:
        return "0" * 64


try:
    from DRV_Packet import get_drv_packet_audit_hash
except ImportError:

    def get_drv_packet_audit_hash() -> str:
        return "0" * 64


try:
    pass
except ImportError:
    pass


def get_system_audit_hash(
    certified_math_logs: Optional[List[Dict[str, Any]]] = None,
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
    pqc_hash = get_pqc_audit_hash()
    drv_packet_hash = get_drv_packet_audit_hash()
    if certified_math_logs is not None:
        sorted_logs = sorted(certified_math_logs, key=lambda x: x.get("log_index", 0))
        certified_math_hash = hashlib.sha256(
            json.dumps(sorted_logs, sort_keys=True).encode("utf-8")
        ).hexdigest()
    else:
        certified_math_hash = "0" * 64
    system_state = {
        "pqc_audit_hash": pqc_hash,
        "drv_packet_audit_hash": drv_packet_hash,
        "certified_math_audit_hash": certified_math_hash,
        "timestamp": "system_hash",
    }
    serialized_system_state = json.dumps(
        system_state, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(serialized_system_state.encode("utf-8")).hexdigest()


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    system_hash = get_system_audit_hash()
    logger.info(f"QFS System Audit Hash: {system_hash}")
    clear_all_audit_logs()
    logger.info("All audit logs cleared")
