import sys
sys.path.append('src')

from src.libs.CertifiedMath import CertifiedMath

# Test memory exhaustion protection
try:
    # Create a huge log list that would consume a lot of memory
    # We need to create a list of dictionaries to match the expected type
    huge_log = [{"data": "x" * 1000000} for _ in range(1000)]  # 1GB equivalent
    
    # Try to get log hash - this should fail gracefully
    log_hash = CertifiedMath.get_log_hash(huge_log)
    print("✗ Memory exhaustion protection failed - should have raised an exception")
    sys.exit(1)
except Exception as e:
    print(f"✓ Memory exhaustion protection working: {type(e).__name__}")