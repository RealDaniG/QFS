"""
Deterministic Complexity Analysis
Measures self-similarity across scales.
"""

from typing import Dict, List
from v13.policy.artistic_constants import SCALE

def analyze_complexity(content_metadata: Dict) -> int:
    """
    Measure fractal-like self-similarity.
    
    Args:
        content_metadata: {
            "structures": List[{"scale": int, "pattern_id": str}]
        }
    
    Returns:
        Complexity score (0-SCALE)
    """
    structures = content_metadata.get("structures", [])
    if not structures:
        return SCALE // 4  # Low complexity baseline
    
    # Group by pattern_id and check for repetition across scales
    pattern_scales = {}
    for struct in structures:
        pid = struct.get("pattern_id", "unknown")
        scale = struct.get("scale", 0)
        if pid not in pattern_scales:
            pattern_scales[pid] = []
        pattern_scales[pid].append(scale)
    
    # Count patterns that appear at multiple scales (fractal nature)
    multi_scale_patterns = sum(1 for scales in pattern_scales.values() if len(scales) > 1)
    
    # Score = ratio of multi-scale patterns to total patterns
    total_patterns = len(pattern_scales)
    
    if total_patterns == 0:
        return 0
        
    score = (multi_scale_patterns * SCALE) // total_patterns
    return score
