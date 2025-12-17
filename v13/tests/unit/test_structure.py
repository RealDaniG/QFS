"""
Test file to verify the QFS V13 repository structure.
"""

def test_imports():
    """Test that we can import the core modules."""
    try:
        from CertifiedMath import CertifiedMath, BigNum128
        print('✅ CertifiedMath import successful')
    except ImportError as e:
        print(f'❌ CertifiedMath import failed: {e}')
        raise
    try:
        from PQC import PQC
        print('✅ PQC import successful')
    except ImportError as e:
        print(f'❌ PQC import failed: {e}')
        raise
    try:
        from AST_ZeroSimChecker import AST_ZeroSimChecker
        print('✅ AST_ZeroSimChecker import successful')
    except ImportError as e:
        print(f'❌ AST_ZeroSimChecker import failed: {e}')
        raise

def test_structure():
    """Test that the directory structure is correct."""
    required_dirs = ['src/libs', 'src/core', 'src/sdk', 'src/handlers', 'src/services', 'src/utils', 'tools', 'audit/runs', 'tests/unit', 'tests/integration', 'tests/deterministic', 'tests/property', 'tests/mocks', 'scripts', 'docs/qfs_v13_plans', 'docs/compliance', '.github/workflows']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f'✅ Directory {directory} exists')
        else:
            print(f'❌ Directory {directory} missing')
            raise FileNotFoundError(f'Required directory {directory} not found')
if __name__ == '__main__':
    print('Running QFS V13 Structure Tests...')
    test_structure()
    test_imports()
    print('🎉 All structure tests passed!')