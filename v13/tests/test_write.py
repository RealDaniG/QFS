import json
data = {'test': 'data'}
print('Current working directory:', os.getcwd())
print('Evidence directory exists:', os.path.exists('evidence'))
print('Evidence v13_6 directory exists:', os.path.exists('evidence/v13_6'))
try:
    with open('evidence/v13_6/test.json', 'w') as f:
        json.dump(data, f)
    print('File written successfully')
except Exception as e:
    print('Error writing file:', e)
