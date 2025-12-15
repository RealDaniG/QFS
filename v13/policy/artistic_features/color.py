"""
Deterministic Color Harmony Analysis
Measures hue spacing according to Golden Angle.
"""

from typing import Dict, List
from v13.policy.artistic_constants import GOLDEN_ANGLE, SCALE

def analyze_color_harmony(content_metadata: Dict) -> int:
    """
    Analyze color palette against Golden Angle spacing.
    
    Args:
        content_metadata: {
            "palette": List[{"hue": int}]  # Hue in degrees * 10^6
        }
    
    Returns:
        Harmony score (0-SCALE)
    """
    palette = content_metadata.get("palette", [])
    if len(palette) < 2:
        return SCALE // 2  # Neutral score for monochrome
    
    # Extract hues and sort
    hues = sorted([color.get("hue", 0) for color in palette])
    
    # Check spacing between consecutive hues against Golden Angle
    deviations = []
    for i in range(len(hues) - 1):
        spacing = (hues[i+1] - hues[i]) % (360 * 10**6)
        deviation = abs(spacing - GOLDEN_ANGLE)
        deviations.append(deviation)
    
    # Average deviation (lower = better)
    avg_deviation = sum(deviations) // len(deviations)
    
    # Convert to score (perfect alignment = SCALE)
    tolerance = 10 * 10**6  # 10° tolerance
    
    # Score formula: SCALE * (1 - avg_deviation / tolerance)
    if tolerance > 0:
        decrement = (avg_deviation * SCALE) // tolerance
        score = max(0, SCALE - decrement)
    else:
        score = 0
        
    return score
