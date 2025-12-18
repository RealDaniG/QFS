"""
Simple script to check if transaction_processor.py has violations
"""
import subprocess
import sys

def main():
    # Run the debug checker and capture output
    result = subprocess.run([
        sys.executable, 
        'v13/tools_root/debug_checker.py'
    ], capture_output=True, text=True, cwd='.')
    
    # Check if transaction_processor.py is mentioned in the output
    if 'transaction_processor.py' in result.stdout:
        print("Violations found in transaction_processor.py:")
        lines = result.stdout.split('\n')
        for line in sorted(lines):
            if 'transaction_processor.py' in line:
                print(line)
            elif 'transaction_processor.py' in line:
                print(line)
    else:
        print("No violations found in transaction_processor.py")

if __name__ == '__main__':
    main()
