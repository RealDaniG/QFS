"""
Deterministic Symmetry Analysis
Detects geometric symmetries (rotational, reflective).
"""

from typing import Dict, List
from v13.policy.artistic_constants import HEX_ANGLE, SCALE

def analyze_symmetry(content_metadata: Dict) -> int:
    """
    Detect symmetry patterns in element placement.
    
    Args:
        content_metadata: {
            "elements": List[{"x": int, "y": int, "type": str}]
        }
    
    Returns:
        Symmetry score (0-SCALE)
    """
    elements = content_metadata.get("elements", [])
    if len(elements) < 2:
        return 0
    
    # Check for hexagonal symmetry (6-fold rotation)
    # For each element, check if 5 others exist at 60° intervals
    center_x = sum(e.get("x", 0) for e in elements) // len(elements)
    center_y = sum(e.get("y", 0) for e in elements) // len(elements)
    
    symmetry_matches = 0
    for elem in elements:
        # Convert to polar coordinates (deterministic integer approach)
        dx = elem.get("x", 0) - center_x
        dy = elem.get("y", 0) - center_y
        r_sq = dx**2 + dy**2
        
        if r_sq == 0:
            continue
            
        # Check for matching elements at 60° intervals
        # Since we don't have atan2 in minimal integer math easily,
        # we check for elements at same radius r_sq within tolerance.
        # This is a simplified "radial symmetry" check.
        
        matches = 0
        tolerance_sq = max(1, r_sq // 10) # 10% radius squared tolerance
        
        for other in elements:
             odx = other.get("x", 0) - center_x
             ody = other.get("y", 0) - center_y
             other_r_sq = odx**2 + ody**2
             
             if abs(other_r_sq - r_sq) <= tolerance_sq:
                 matches += 1
        
        # If we find at least 2 points (itself + 1 other) at same radius, we assume partial symmetry
        if matches >= 2:
            symmetry_matches += 1
            
        # Higher score if matches are multiples of 6 (hexagonal) or 3 (triangular)
        if matches % 6 == 0 and matches > 0:
            symmetry_matches += 2
    
    # Normalize to score
    # Max possible would be if every element was part of a perfect symmetry group
    max_possible = len(elements) * 3 # Heuristic max
    
    score = (symmetry_matches * SCALE) // max(max_possible, 1)
    return min(score, SCALE)
