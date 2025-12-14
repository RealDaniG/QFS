import sys
import os
import glob

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'libs'))

from src.libs.AST_ZeroSimChecker import AST_ZeroSimChecker

def check_core_violations():
    checker = AST_ZeroSimChecker()
    core_dirs = ['src/core', 'src/handlers', 'src/libs', 'src/sdk', 'src/services']
    all_violations = {}
    
    for directory in core_dirs:
        # Get all Python files in the directory
        pattern = os.path.join(directory, '*.py')
        files = glob.glob(pattern)
        
        for file_path in files:
            # Skip test files and cache directories
            if 'test' not in file_path.lower() and '__pycache__' not in file_path.lower():
                violations = checker.scan_file(file_path)
                if violations:
                    all_violations[file_path] = violations
    
    print(f"Total files with violations in core: {len(all_violations)}")
    total_violations = sum(len(v) for v in all_violations.values())
    print(f"Total violations in core: {total_violations}")
    
    # Print details of violations
    if all_violations:
        print("\nDetailed violations:")
        for file_path, violations in all_violations.items():
            print(f"\n{file_path}:")
            for violation in violations:
                print(f"  Line {violation.line_number}: {violation.violation_type} - {violation.message}")
    else:
        print("\n✓ No violations found in core implementation files!")

if __name__ == "__main__":
    check_core_violations()