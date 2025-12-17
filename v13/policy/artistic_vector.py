"""
AES Multi-Dimensional Vector
Each axis represents a deterministic artistic property.
"""
from dataclasses import dataclass, field
from typing import List, Dict
import hashlib
import json

@dataclass
class ArtisticVector:
    """
    7-dimensional artistic evaluation vector.
    All values are integers (scaled by 10^9).
    """
    composition: int
    color_harmony: int
    symmetry: int
    complexity: int
    narrative: int
    originality: int
    resonance: int
    content_id: str
    event_ids: List[str]
    phi_weights: Dict[str, int]
    reason_codes: List[str]
    vector_hash: str = field(init=False)

    def __post_init__(self):
        """Compute hash on initialization."""
        self.vector_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """
        Deterministic hash over all vector components.
        """
        sorted_weights = sorted(self.phi_weights.items())
        canonical = f"{self.content_id}{''.join(sorted(self.event_ids))}{self.composition}{self.color_harmony}{self.symmetry}{self.complexity}{self.narrative}{self.originality}{self.resonance}{str(sorted_weights)}{''.join(sorted(self.reason_codes))}"
        return hashlib.sha3_256(canonical.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {'composition': self.composition, 'color_harmony': self.color_harmony, 'symmetry': self.symmetry, 'complexity': self.complexity, 'narrative': self.narrative, 'originality': self.originality, 'resonance': self.resonance, 'content_id': self.content_id, 'event_ids': sorted(self.event_ids), 'phi_weights': self.phi_weights, 'reason_codes': sorted(self.reason_codes), 'vector_hash': self.vector_hash}