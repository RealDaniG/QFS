"""
PQC Algorithm Registry for QFS V13
Defines supported Post-Quantum Cryptography algorithms and their properties.
"""

from enum import Enum
from dataclasses import dataclass


class PQCAlgorithm(Enum):
    DILITHIUM5 = "Dilithium5"
    FALCON1024 = "Falcon-1024"
    SPHINCS_SHA2_256F_SIMPLE = "SPHINCS+-SHA2-256f-simple"
    KYBER1024 = "Kyber1024"


@dataclass
class AlgorithmInfo:
    id: str
    security_level: int
    mechanism: str  # "signature" or "kem"
    description: str


REGISTRY = {
    PQCAlgorithm.DILITHIUM5: AlgorithmInfo(
        id="Dilithium5",
        security_level=5,
        mechanism="signature",
        description="NIST Level 5 (AES-256 equivalent) Lattice-based signature",
    ),
    PQCAlgorithm.FALCON1024: AlgorithmInfo(
        id="Falcon-1024",
        security_level=5,
        mechanism="signature",
        description="NIST Level 5 Lattice-based signature (compact)",
    ),
    PQCAlgorithm.KYBER1024: AlgorithmInfo(
        id="Kyber1024",
        security_level=5,
        mechanism="kem",
        description="NIST Level 5 Lattice-based Key Encapsulation Mechanism",
    ),
}
