import sys
import os

# Add the libs directory to the path - updated to reflect new directory structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from CertifiedMath import CertifiedMath, BigNum128
import hashlib