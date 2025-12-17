"""
Demo Transaction Script for QFS V13 SDK
This script demonstrates the 6-step mandatory transaction workflow for QFS V13
"""
import json
import hashlib
from QFSV13SDK import QFSV13SDK, DRV_Packet, OperationBundle

def demo_transaction_workflow():
    """
    Demonstrate the 6-step mandatory transaction workflow for QFS V13:
    1. Deterministic Request Verification (DRV) Initialization
    2. CertifiedMath Operation Execution
    3. PQC Signature Generation
    4. Atomic Bundle Creation
    5. CRS Hash Chain Update
    6. External Verification Preparation
    """
    print('=== QFS V13 Transaction Workflow Demo ===\n')
    sdk = QFSV13SDK()
    print('1. SDK initialized successfully')
    print('\n2. Step 1: Deterministic Request Verification (DRV) Initialization')
    drv_packet = DRV_Packet(ttsTimestamp=1678901234, sequenceNumber=0, seed='deterministic_seed_12345')
    print(f'   DRV Packet created with timestamp: {drv_packet.ttsTimestamp}')
    print(f'   Sequence number: {drv_packet.sequenceNumber}')
    print(f'   Seed: {drv_packet.seed}')
    print('\n3. Step 2: CertifiedMath Operation Execution')
    try:
        result_bundle = sdk.add('1000000000000000000', '2000000000000000000', drv_packet)
        print(f'   Addition operation completed: 1 + 2 = {int(result_bundle.result) / 10 ** 18}')
        print(f'   Operation ID: {result_bundle.operation_id}')
    except Exception as e:
        print(f'   Error during operation: {e}')
        return
    print('\n4. Step 3: PQC Signature Generation')
    print(f'   PQC signature generated: {result_bundle.pqc_signature[:32]}...')
    print(f'   Signature is deterministic: {sdk.verify_pqc_signature(result_bundle)}')
    print('\n5. Step 4: Atomic Bundle Creation')
    print(f'   Bundle created with operation: {result_bundle.operation}')
    print(f'   Operands: {result_bundle.operands}')
    print(f'   Result: {int(result_bundle.result) / 10 ** 18}')
    print('\n6. Step 5: CRS Hash Chain Update')
    print(f'   Log hash: {result_bundle.log_hash}')
    audit_log = sdk.get_audit_log()
    print(f'   Audit log entries: {len(audit_log)}')
    print('\n7. Step 6: External Verification Preparation')
    export_success = sdk.export_audit_log('transaction_audit_log.json')
    if export_success:
        print('   Audit log exported successfully for external verification')
    else:
        print('   Failed to export audit log')
    print('\n8. Sequence Enforcement Demo (Second Transaction)')
    drv_packet2 = DRV_Packet(ttsTimestamp=1678901235, sequenceNumber=1, seed='deterministic_seed_67890')
    try:
        result_bundle2 = sdk.mul('3000000000000000000', '4000000000000000000', drv_packet2)
        print(f'   Multiplication operation completed: 3 * 4 = {int(result_bundle2.result) / 10 ** 18}')
        print(f'   Operation ID: {result_bundle2.operation_id}')
        print(f'   PQC signature: {result_bundle2.pqc_signature[:32]}...')
        audit_log = sdk.get_audit_log()
        print(f'   Total audit log entries: {len(audit_log)}')
        export_success = sdk.export_audit_log('transaction_audit_log_updated.json')
        if export_success:
            print('   Updated audit log exported successfully')
    except Exception as e:
        print(f'   Error during second operation: {e}')
    print('\n=== Transaction Workflow Demo Completed ===')

def test_error_handling():
    """Test atomic rollback on error"""
    print('\n=== Error Handling Test ===')
    sdk = QFSV13SDK()
    drv_packet = DRV_Packet(ttsTimestamp=1678901236, sequenceNumber=0, seed='error_test_seed')
    print('Testing division by zero (should trigger atomic rollback)...')
    try:
        result_bundle = sdk.div('1000000000000000000', '0', drv_packet)
        print('   ERROR: Division by zero should have failed!')
    except ZeroDivisionError as e:
        print(f'   Expected error caught: {e}')
        audit_log = sdk.get_audit_log()
        print(f'   Audit log entries after rollback: {len(audit_log)} (should be 0)')
    print('=== Error Handling Test Completed ===')

def test_sequence_enforcement():
    """Test sequence number enforcement"""
    print('\n=== Sequence Enforcement Test ===')
    sdk = QFSV13SDK()
    drv_packet1 = DRV_Packet(ttsTimestamp=1678901237, sequenceNumber=0, seed='sequence_test_seed_1')
    try:
        result_bundle1 = sdk.add('1000000000000000000', '1000000000000000000', drv_packet1)
        print(f'   First transaction successful (sequence 0)')
    except Exception as e:
        print(f'   Error in first transaction: {e}')
        return
    drv_packet_invalid = DRV_Packet(ttsTimestamp=1678901238, sequenceNumber=2, seed='sequence_test_seed_2')
    try:
        result_bundle_invalid = sdk.add('2000000000000000000', '1000000000000000000', drv_packet_invalid)
        print('   ERROR: Invalid sequence number should have been rejected!')
    except ValueError as e:
        print(f'   Expected error for invalid sequence: {e}')
    drv_packet2 = DRV_Packet(ttsTimestamp=1678901238, sequenceNumber=1, seed='sequence_test_seed_2')
    try:
        result_bundle2 = sdk.add('2000000000000000000', '1000000000000000000', drv_packet2)
        print(f'   Second transaction successful (sequence 1)')
        audit_log = sdk.get_audit_log()
        print(f'   Total audit log entries: {len(audit_log)}')
    except Exception as e:
        print(f'   Error in second transaction: {e}')
    print('=== Sequence Enforcement Test Completed ===')
if __name__ == '__main__':
    demo_transaction_workflow()
    test_error_handling()
    test_sequence_enforcement()