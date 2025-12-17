"""
Comprehensive Test for QFS V13 SDK Operations
"""
import json
from QFSV13SDK import QFSV13SDK, DRV_Packet

def test_all_operations():
    """Test all CertifiedMath operations in the SDK"""
    print('=== Comprehensive SDK Operations Test ===\n')
    sdk = QFSV13SDK()
    sequence_counter = 0
    base_timestamp = 1678901234
    print('1. Testing Addition...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_add_{sequence_counter}')
        result = sdk.add('1000000000000000000', '2000000000000000000', drv_packet)
        print(f'   1 + 2 = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print('\n2. Testing Subtraction...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_sub_{sequence_counter}')
        result = sdk.sub('3000000000000000000', '1000000000000000000', drv_packet)
        print(f'   3 - 1 = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print('\n3. Testing Multiplication...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_mul_{sequence_counter}')
        result = sdk.mul('2000000000000000000', '3000000000000000000', drv_packet)
        print(f'   2 * 3 = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print('\n4. Testing Division...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_div_{sequence_counter}')
        result = sdk.div('6000000000000000000', '2000000000000000000', drv_packet)
        print(f'   6 / 2 = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print('\n5. Testing Square Root...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_sqrt_{sequence_counter}')
        result = sdk.sqrt('4000000000000000000', 20, drv_packet)
        print(f'   sqrt(4) = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print('\n6. Testing Phi Series...')
    try:
        drv_packet = DRV_Packet(ttsTimestamp=base_timestamp + sequence_counter, sequenceNumber=sequence_counter, seed=f'test_seed_phi_{sequence_counter}')
        result = sdk.phi_series('1000000000000000000', 10, drv_packet)
        print(f'   phi_series(1) = {int(result.result) / 10 ** 18}')
        sequence_counter += 1
    except Exception as e:
        print(f'   Error: {e}')
    print(f'\n7. Audit Log Summary:')
    audit_log = sdk.get_audit_log()
    print(f'   Total operations executed: {len(audit_log)}')
    print(f'\n8. PQC Signature Verification:')
    all_signatures_valid = True
    for i, entry in enumerate(audit_log):
        print(f'   Operation {i + 1}: Signature verification not directly testable from log')
    print('\n=== Comprehensive SDK Operations Test Completed ===')
if __name__ == '__main__':
    test_all_operations()