import sys
import os
import json
import hashlib
from typing import List, Dict, Any

# Add the libs directory to the path - updated to reflect new directory structure

from CertifiedMath import (
    CertifiedMath, BigNum128, 
    MathOverflowError, MathValidationError,
    PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO,
    set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config,
    LogContext
)