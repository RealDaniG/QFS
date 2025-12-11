"""
CEE (Coherent Economic Engine) v2 - Phase-4 Module
Zero-Simulation Compliant, PQC-Secured, Deterministic Economic Kernel

This package implements a civilization-grade economic engine with:
- Strict module isolation
- PQC-signed message passing
- Deterministic simulation
- Full auditability
"""

__version__ = "2.4.0-phase4"
__all__ = [
    "PQCInterface",
    "CEEModule",
    "SignedMessage",
    "ModuleInput",
    "ModuleOutput",
]

from .interfaces.pqc_interface import PQCInterface
from .interfaces.module_interface import CEEModule, ModuleInput, ModuleOutput
from .interfaces.message_protocol import SignedMessage
