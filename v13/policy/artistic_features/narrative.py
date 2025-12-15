"""
Deterministic Narrative Structure Analysis
Measures pacing against Fibonacci sequences.
"""

from typing import Dict, List
from v13.policy.artistic_constants import FIBONACCI, SCALE

def analyze_narrative(content_metadata: Dict) -> int:
    """
    Analyze temporal structure for Fibonacci alignment.
    
    Args:
        content_metadata: {
            "segments": List[{"duration": int}]  # In ticks
        }
    
    Returns:
        Narrative score (0-SCALE)
    """
    segments = content_metadata.get("segments", [])
    if not segments:
        return SCALE // 2
    
    # Extract segment durations
    durations = [seg.get("duration", 0) for seg in segments]
    
    # Check sequences of sufficient length
    if len(durations) < 2:
        return SCALE // 2
        
    deviations = []
    for i in range(len(durations) - 1):
        # Prevent division by zero
        d_curr = max(durations[i], 1)
        d_next = durations[i+1]
        
        # Calculate ratio scaled
        ratio = (d_next * SCALE) // d_curr
        
        # Find closest Fibonacci ratio
        # Ratios like 1/1, 2/1, 3/2, 5/3...
        # We compare against F(n+1)/F(n)
        closest_diff = SCALE * 10
        
        for j in range(len(FIBONACCI)-1):
            fib_ratio = (FIBONACCI[j+1] * SCALE) // FIBONACCI[j]
            diff = abs(ratio - fib_ratio)
            if diff < closest_diff:
                closest_diff = diff
        
        deviations.append(closest_diff)
    
    # Average deviation (lower = better)
    avg_deviation = sum(deviations) // max(len(deviations), 1)
    
    # Convert to score
    # Tolerance: let's say average deviation of 0.5 (Scale/2) yields 0 score
    tolerance = SCALE // 2
    
    if tolerance > 0:
        decrement = (avg_deviation * SCALE) // tolerance
        score = max(0, SCALE - decrement)
    else:
        score = 0
        
    return score
