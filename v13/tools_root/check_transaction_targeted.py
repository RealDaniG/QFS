"""
Targeted checker for transaction_processor.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from debug_checker import check_file

def main():
    file_path = 'v13/ATLAS/src/core/transaction_processor.py'
    errors = check_file(file_path)
    
    if errors:
        print(f"Violations found in {file_path}:")
        for line, error in sorted(errors):
            print(f"  Line {line}: {error}")
    else:
        print(f"No violations found in {file_path}")

if __name__ == '__main__':
    main()