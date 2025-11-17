import sys
import os
import hashlib

# Add the libs directory to the path - updated to reflect new directory structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

# Import the PQC functions
try:
    from PQC import generate_keypair, clear_pqc_audit_log, get_pqc_audit_log, get_pqc_audit_hash
except ImportError:
    # Try alternative import path
    import PQC
    generate_keypair = getattr(PQC, 'generate_keypair', None)
    clear_pqc_audit_log = getattr(PQC, 'clear_pqc_audit_log', None)
    get_pqc_audit_log = getattr(PQC, 'get_pqc_audit_log', None)
    get_pqc_audit_hash = getattr(PQC, 'get_pqc_audit_hash', None)

# Import DRV_Packet
try:
    from DRV_Packet import DRV_Packet, ValidationResult, ValidationErrorCode, clear_drv_packet_audit_log, get_drv_packet_audit_log, get_drv_packet_audit_hash
except ImportError:
    # Try alternative import path
    import DRV_Packet
    DRV_Packet = getattr(DRV_Packet, 'DRV_Packet', DRV_Packet)
    ValidationResult = getattr(DRV_Packet, 'ValidationResult', None)
    ValidationErrorCode = getattr(DRV_Packet, 'ValidationErrorCode', None)
    clear_drv_packet_audit_log = getattr(DRV_Packet, 'clear_drv_packet_audit_log', None)
    get_drv_packet_audit_log = getattr(DRV_Packet, 'get_drv_packet_audit_log', None)
    get_drv_packet_audit_hash = getattr(DRV_Packet, 'get_drv_packet_audit_hash', None)