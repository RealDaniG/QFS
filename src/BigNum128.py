# Compatibility shim for BigNum128
# This file re-exports from the v13 package to maintain backward compatibility

# Add the v13 directory to the path
import sys
import os

# Add the v13 directory to the path
v13_path = os.path.join(os.path.dirname(__file__), '..', 'v13')
if v13_path not in sys.path:
    sys.path.insert(0, v13_path)

# Re-export from v13
from v13.libs.BigNum128 import *