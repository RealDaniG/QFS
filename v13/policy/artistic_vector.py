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
    composition: int  # Golden ratio alignment in layout
    color_harmony: int  # Hue spacing following φ
    symmetry: int  # Geometric symmetry (polygonal grids)
    complexity: int  # Fractal/self-similarity score
    narrative: int  # Temporal structure (Fibonacci pacing)
    originality: int  # Deviation from historical patterns
    resonance: int  # Event-weighted impact (φ-decay)
    
    # Metadata
    content_id: str
    event_ids: List[str]  # Sorted for determinism
    phi_weights: Dict[str, int]  # Applied φ-based weights
    reason_codes: List[str]  # E.g., "composition_phi_aligned"
    vector_hash: str = field(init=False)
    
    def __post_init__(self):
        """Compute hash on initialization."""
        self.vector_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """
        Deterministic hash over all vector components.
        """
        # Sort weights for determinism
        sorted_weights = sorted(self.phi_weights.items())
        
        canonical = (
            f"{self.content_id}"
            f"{''.join(sorted(self.event_ids))}"
            f"{self.composition}{self.color_harmony}{self.symmetry}"
            f"{self.complexity}{self.narrative}{self.originality}{self.resonance}"
            f"{str(sorted_weights)}"
            f"{''.join(sorted(self.reason_codes))}"
        )
        return hashlib.sha3_256(canonical.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "composition": self.composition,
            "color_harmony": self.color_harmony,
            "symmetry": self.symmetry,
            "complexity": self.complexity,
            "narrative": self.narrative,
            "originality": self.originality,
            "resonance": self.resonance,
            "content_id": self.content_id,
            "event_ids": sorted(self.event_ids),
            "phi_weights": self.phi_weights,
            "reason_codes": sorted(self.reason_codes),
            "vector_hash": self.vector_hash
        }
