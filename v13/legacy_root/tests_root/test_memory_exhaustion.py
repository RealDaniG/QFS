import sys
sys.path.append('src')

from src.libs.CertifiedMath import CertifiedMath

def test_memory_exhaustion_protection():
    """Test memory exhaustion protection."""
    try:
        # Create a huge log list that would consume a lot of memory
        # We need to create a list of dictionaries to match the expected type
        huge_log = [{"data": "x" * 1000000} for _ in range(1000)]  # 1GB equivalent
        
        # Try to get log hash - this should fail gracefully
        log_hash = CertifiedMath.get_log_hash(huge_log)
        # If we get here, memory exhaustion protection failed
        assert False, "Memory exhaustion protection failed - should have raised an exception"
    except Exception as e:
        # Expected behavior - memory exhaustion protection working
        assert isinstance(e, (MemoryError, RuntimeError, ValueError))