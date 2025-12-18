import hashlib
try:
    from PQC import generate_keypair, clear_pqc_audit_log, get_pqc_audit_log, get_pqc_audit_hash
except ImportError:
    import PQC
    generate_keypair = getattr(PQC, 'generate_keypair', None)
    clear_pqc_audit_log = getattr(PQC, 'clear_pqc_audit_log', None)
    get_pqc_audit_log = getattr(PQC, 'get_pqc_audit_log', None)
    get_pqc_audit_hash = getattr(PQC, 'get_pqc_audit_hash', None)
try:
    from DRV_Packet import DRV_Packet, ValidationResult, ValidationErrorCode, clear_drv_packet_audit_log, get_drv_packet_audit_log, get_drv_packet_audit_hash
except ImportError:
    import DRV_Packet
    DRV_Packet = getattr(DRV_Packet, 'DRV_Packet', DRV_Packet)
    ValidationResult = getattr(DRV_Packet, 'ValidationResult', None)
    ValidationErrorCode = getattr(DRV_Packet, 'ValidationErrorCode', None)
    clear_drv_packet_audit_log = getattr(DRV_Packet, 'clear_drv_packet_audit_log', None)
    get_drv_packet_audit_log = getattr(DRV_Packet, 'get_drv_packet_audit_log', None)
    get_drv_packet_audit_hash = getattr(DRV_Packet, 'get_drv_packet_audit_hash', None)
