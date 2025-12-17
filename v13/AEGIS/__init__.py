"""
AEGIS - Advisory AI Layer for QFS x ATLAS

This package provides deterministic advisory AI capabilities on top of QFS's
deterministic core, aligned with the AEGIS Advisory Boundaries Contract v1.0.

AEGIS must never:
- Mutate economic state or parameters
- Bypass or weaken guards
- Affect consensus or deterministic replay

All AEGIS outputs are strictly advisory and traceable to proof vectors.
"""

__version__ = "0.1.0"
__contract_version__ = "AEGIS_ADVISORY_CONTRACT_v1.0"

# Track-based module organization
from . import models
from . import governance
from . import services
from . import sandbox
from . import ui_contracts

__all__ = ["models", "governance", "services", "sandbox", "ui_contracts"]
