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
    segments = content_metadata.get('segments', [])
    if not segments:
        return SCALE // 2
    durations = [seg.get('duration', 0) for seg in segments]
    if len(durations) < 2:
        return SCALE // 2
    deviations = []
    for i in range(len(durations) - 1):
        d_curr = max(durations[i], 1)
        d_next = durations[i + 1]
        ratio = d_next * SCALE // d_curr
        closest_diff = SCALE * 10
        for j in range(len(FIBONACCI) - 1):
            fib_ratio = FIBONACCI[j + 1] * SCALE // FIBONACCI[j]
            diff = abs(ratio - fib_ratio)
            if diff < closest_diff:
                closest_diff = diff
        deviations.append(closest_diff)
    avg_deviation = sum(deviations) // max(len(deviations), 1)
    tolerance = SCALE // 2
    if tolerance > 0:
        decrement = avg_deviation * SCALE // tolerance
        score = max(0, SCALE - decrement)
    else:
        score = 0
    return score