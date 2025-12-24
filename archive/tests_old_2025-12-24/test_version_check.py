from v13.libs.DRV_Packet import DRV_Packet
if __name__ == '__main__':
    print('=== Testing Valid Version ===')
    try:
        valid_data = {'version': '1.0', 'ttsTimestamp': 1700000000, 'sequence': 1, 'seed': 'test_seed', 'previous_hash': '0000000000000000000000000000000000000000000000000000000000000000'}
        packet = DRV_Packet.from_dict(valid_data)
        print(f'Valid version packet created successfully: {packet}')
    except Exception as e:
        print(f'Error with valid version: {e}')
    print('\n=== Testing Invalid Version ===')
    try:
        invalid_data = {'version': '0.9', 'ttsTimestamp': 1700000000, 'sequence': 1, 'seed': 'test_seed', 'previous_hash': '0000000000000000000000000000000000000000000000000000000000000000'}
        packet = DRV_Packet.from_dict(invalid_data)
        print(f'Invalid version packet created (this should not happen): {packet}')
    except ValueError as e:
        print(f'Correctly caught version error: {e}')
    except Exception as e:
        print(f'Unexpected error with invalid version: {e}')
    print('\n=== Testing Missing Version ===')
    try:
        missing_data = {'ttsTimestamp': 1700000000, 'sequence': 1, 'seed': 'test_seed', 'previous_hash': '0000000000000000000000000000000000000000000000000000000000000000'}
        packet = DRV_Packet.from_dict(missing_data)
        print(f'Missing version packet created successfully: {packet}')
    except Exception as e:
        print(f'Error with missing version: {e}')