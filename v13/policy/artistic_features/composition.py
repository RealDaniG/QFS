"""
Deterministic Composition Analysis
Measures alignment with Golden Ratio grid and spiral.
"""
from typing import Dict, List
from v13.policy.artistic_constants import PHI, SCALE, phi_ratio

def analyze_composition(content_metadata: Dict) -> int:
    """
    Analyze visual composition against φ-based grid.
    
    Args:
        content_metadata: {
            "width": int,
            "height": int,
            "elements": List[{"x": int, "y": int, "w": int, "h": int}]
        }
    
    Returns:
        Composition score (0-SCALE), higher = better φ alignment
    """
    width = content_metadata.get('width', 1)
    height = content_metadata.get('height', 1)
    elements = content_metadata.get('elements', [])
    aspect_deviation = phi_ratio(width, height)
    phi_x = width * SCALE // PHI
    phi_y = height * SCALE // PHI
    alignment_scores = []
    for elem in sorted(elements):
        elem_x = elem.get('x', 0) * SCALE
        elem_y = elem.get('y', 0) * SCALE
        dist_x = min(abs(elem_x - phi_x), abs(elem_x - (width * SCALE - phi_x)))
        dist_y = min(abs(elem_y - phi_y), abs(elem_y - (height * SCALE - phi_y)))
        tolerance_range = min(width, height) * SCALE // 20
        dist_avg = (dist_x + dist_y) // 2
        if tolerance_range > 0:
            score = max(0, SCALE - dist_avg * SCALE // tolerance_range)
        else:
            score = 0
        alignment_scores.append(score)
    avg_alignment = sum(alignment_scores) // len(alignment_scores) if alignment_scores else 0
    aspect_bonus = max(0, SCALE - aspect_deviation)
    final_score = (avg_alignment + aspect_bonus) // 2
    return min(final_score, SCALE)