import subprocess

result = subprocess.run(['python', 'v13/libs/AST_ZeroSimChecker.py', 'v13/', '--fail'], 
                       capture_output=True, text=True)
print(result.stdout[:2000]) # First 2000 chars
print("\n..." + "="*50 + "...\n")
print(result.stdout[-2000:]) # Last 2000 chars
