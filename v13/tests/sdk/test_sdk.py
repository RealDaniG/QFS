import json
from QFSV13SDK import QFSV13SDK, DRV_Packet

def test_sdk():
    """Test the QFS V13 SDK functionality"""
    sdk = QFSV13SDK()
    drv_packet = DRV_Packet(ttsTimestamp=1678901234, sequenceNumber=1, seed='test_seed_12345')
    print('Testing QFS V13 SDK...')
    print('\n1. Testing addition...')
    try:
        result = sdk.add('1000000000000000000', '2000000000000000000', drv_packet)
        print(f'   1 + 2 = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n2. Testing subtraction...')
    try:
        result = sdk.sub('3000000000000000000', '1000000000000000000', drv_packet)
        print(f'   3 - 1 = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n3. Testing multiplication...')
    try:
        result = sdk.mul('2000000000000000000', '3000000000000000000', drv_packet)
        print(f'   2 * 3 = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n4. Testing division...')
    try:
        result = sdk.div('6000000000000000000', '2000000000000000000', drv_packet)
        print(f'   6 / 2 = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n5. Testing square root...')
    try:
        result = sdk.sqrt('4000000000000000000', 20, drv_packet)
        print(f'   sqrt(4) = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n6. Testing phi series...')
    try:
        result = sdk.phi_series('1000000000000000000', 10, drv_packet)
        print(f'   phi_series(1) = {int(result.result) / 10 ** 18}')
        print(f'   Operation ID: {result.operation_id}')
        print(f'   PQC Signature: {result.pqc_signature[:32]}...')
    except Exception as e:
        print(f'   Error: {e}')
    print('\n7. Audit log entries:')
    audit_log = sdk.get_audit_log()
    print(f'   Total operations: {len(audit_log)}')
    print('\n8. Exporting audit log...')
    try:
        sdk.export_audit_log('test_audit_log.json')
        print('   Audit log exported successfully')
    except Exception as e:
        print(f'   Error exporting audit log: {e}')
    print('\nSDK test completed!')
if __name__ == '__main__':
    test_sdk()