"""
Test specifically for the LogContext chain integrity implementation.
"""

import sys
import os
import json
import hashlib

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class MockDilithium5:
    pass

# Patch the Dilithium5 implementation
import libs.PQC
libs.PQC.Dilithium5Impl = MockDilithium5

def create_mock_log_entry(index, operation, entry_hash):
    """Create a mock log entry with the proper structure"""
    entry = {
        "log_index": index,
        "operation": operation,
        "details": {"test": f"data{index}"},
        "pqc_cid": f"test-cid-{index}",
        "quantum_metadata": {"test": "metadata"},
        "timestamp": 1234567890 + index,
        "system_fingerprint": libs.PQC.PQC.SYSTEM_FINGERPRINT,
        "prev_hash": libs.PQC.PQC.ZERO_HASH,  # Placeholder
        "entry_hash": entry_hash
    }
    return entry

def test_log_context_chain_integrity():
    """Test the LogContext chain integrity implementation"""
    try:
        from libs.PQC import PQC
        
        print("✅ Successfully imported PQC module")
        
        # Test LogContext chain integrity
        print("\n--- Testing LogContext Chain Integrity ---")
        with PQC.LogContext() as log:
            # Create properly structured mock entries
            entry1 = create_mock_log_entry(0, "test1", "mock_hash_123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")
            entry2 = create_mock_log_entry(1, "test2", "mock_hash_0987654321098765432109876543210987654321098765432109876543210987654321098765432109876543210987654321098765432109876543210987654321")
            
            log.append(entry1)
            log.append(entry2)
            
            print(f"Number of log entries during context: {len(log)}")
            print(f"First entry has prev_hash: {'prev_hash' in log[0]}")
            print(f"Second entry has prev_hash: {'prev_hash' in log[1]}")
        
        # After context exit, check that chain integrity is set up
        print(f"Number of log entries after context exit: {len(log)}")
        
        if len(log) >= 2:
            print(f"First entry prev_hash: {log[0].get('prev_hash', 'MISSING')}")
            print(f"Second entry prev_hash: {log[1].get('prev_hash', 'MISSING')}")
            
            # Verify chain integrity
            assert log[0]['prev_hash'] == PQC.ZERO_HASH, "First entry should have ZERO_HASH as prev_hash"
            assert log[1]['prev_hash'] == "mock_hash_123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789", "Second entry should have first entry's hash as prev_hash"
            
            print("✅ Chain integrity test passed")
            return True
        else:
            print("⚠️ Not enough log entries to test chain integrity")
            return False
        
    except ImportError as e:
        print(f"❌ Failed to import PQC module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_log_context_chain_integrity()
    if success:
        print("\n🏆 LogContext chain integrity implementation is working correctly!")
    else:
        print("\n❌ LogContext chain integrity implementation requires fixes.")
        sys.exit(1)