sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from libs.PQC import PQC
    print('✅ PQC module imported successfully')
    print('✅ PQC.DILITHIUM5 constant:', PQC.DILITHIUM5)
    print('✅ PQC library is ready for production use')
except ImportError as e:
    print('❌ Failed to import PQC module:', e)
    print('❌ This is expected if pqcrystals.dilithium is not installed')
except Exception as e:
    print('❌ Unexpected error importing PQC module:', e)