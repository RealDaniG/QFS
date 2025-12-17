"""
Simple AST checker to debug recursion issues
"""
import ast
import pathlib
from typing import List, Tuple, Set, Optional

def main():
    """Main function to run the simple checker."""
    print('Simple AST Checker')
    print('=' * 20)
    target_files = ['v13/tools_root/ast_checker.py', 'v13/libs/deterministic_helpers.py', 'v13/tools_root/auto_fix_violations.py']
    for target_file in sorted(target_files):
        print(f'Checking: {target_file}')
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                source = f.read()
            print(f'  Successfully read {len(source)} characters')
        except Exception as e:
            print(f'  Error reading file: {e}')
if __name__ == '__main__':
    main()