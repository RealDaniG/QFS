sys.path.append('src')
from src.libs.CertifiedMath import CertifiedMath

def test_memory_exhaustion_protection():
    """Test memory exhaustion protection."""
    try:
        huge_log = [{'data': 'x' * 1000000} for _ in range(1000)]
        log_hash = CertifiedMath.get_log_hash(huge_log)
        assert False, 'Memory exhaustion protection failed - should have raised an exception'
    except Exception as e:
        assert isinstance(e, (MemoryError, RuntimeError, ValueError))