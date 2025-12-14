# Compatibility shim to support legacy imports
# This file re-exports modules from the v13 package to maintain backward compatibility

# For direct execution of test files that expect src.* imports
import sys
import os

# Add the v13 directory to the path
v13_path = os.path.join(os.path.dirname(__file__), '..', 'v13')
if v13_path not in sys.path:
    sys.path.insert(0, v13_path)

# Re-export commonly used modules
try:
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    pass

try:
    from v13.libs.PQC import PQC
except ImportError:
    pass

try:
    from v13.libs.BigNum128 import BigNum128 as BigNum128_direct
except ImportError:
    pass