import sys
import os
import json

# Add the libs directory to the path - updated to reflect new directory structure

from CertifiedMath import (
    CertifiedMath, BigNum128, 
    LogContext
)

# Import DRV_Packet (assuming it's in the same libs directory)
from DRV_Packet import DRV_Packet