import json
sys.path.append('src')
test_data = {'zebra': 'last', 'alpha': 'first', 'beta': 'second', 'gamma': 'third'}
serialized = json.dumps(test_data, sort_keys=True, separators=(',', ':'))
parsed = json.loads(serialized)
keys = list(parsed.keys())
if keys == sorted(keys):
    print('✓ Canonical serialization - keys are in sorted order')
else:
    print(f'✗ Canonical serialization failed - keys not sorted: {keys}')
expected = '{"alpha":"first","beta":"second","gamma":"third","zebra":"last"}'
if serialized == expected:
    print('✓ Canonical serialization - correct output format')
else:
    print(f'✗ Canonical serialization - incorrect format')
    print(f'  Expected: {expected}')
    print(f'  Got:      {serialized}')
