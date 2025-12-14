"""
ArtisticObservatory.py - Observability layer for AES signals

This module provides an observability layer that aggregates and analyzes AES signal outputs
over time, providing statistics and insights for operators.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict
from .artistic_policy import ArtisticObservationStats

@dataclass
class ArtisticSignalSnapshot:
    """A snapshot of an artistic signal evaluation."""
    timestamp: int
    content_id: str
    dimensions: Dict[str, float]
    confidence: float
    bonus_factor: float
    policy_version: str

@dataclass
class ArtisticObservabilityReport:
    """Comprehensive observability report for AES signals."""
    total_signals_processed: int
    average_confidence: float
    dimension_averages: Dict[str, float]
    dimension_distributions: Dict[str, Dict[str, float]]
    bonus_statistics: Dict[str, float]
    anomaly_count: int
    top_performing_content: List[Dict[str, Any]]
    policy_version: str

class ArtisticSignalObservatory:
    """
    Observability layer for AES signals.
    """
    
    def __init__(self):
        self.signal_history: List[ArtisticSignalSnapshot] = []
        self.bucket_size = 0.1
        self.MAX_HISTORY = 1000 # Cap history in memory for Zero-Sim safety

    def record_signal(self, snapshot: ArtisticSignalSnapshot):
        self.signal_history.append(snapshot)
        if len(self.signal_history) > self.MAX_HISTORY:
            self.signal_history.pop(0)

    def get_observability_report(self, policy_version: str = "") -> ArtisticObservabilityReport:
        if not self.signal_history:
            return ArtisticObservabilityReport(0, 0.0, {}, {}, {}, 0, [], policy_version)

        total_signals = len(self.signal_history)
        avg_confidence = sum(s.confidence for s in self.signal_history) / total_signals
        
        # Averages
        dim_sums = defaultdict(float)
        dim_counts = defaultdict(int)
        for s in self.signal_history:
             for d, v in s.dimensions.items():
                 dim_sums[d] += v
                 dim_counts[d] += 1
        
        dim_avgs = {d: dim_sums[d]/dim_counts[d] for d in dim_sums}
        
        # Distributions
        dim_dists = {}
        for d in dim_sums:
            dim_dists[d] = self._calculate_histogram(d)
            
        # Bonuses
        bonuses = [s.bonus_factor for s in self.signal_history]
        bonus_stats = {
            "mean": sum(bonuses) / len(bonuses),
            "min": min(bonuses),
            "max": max(bonuses),
            "median": sorted(bonuses)[len(bonuses)//2]
        }
        
        # Anomalies (> 2x mean)
        mean_bonus = bonus_stats["mean"]
        anomalies = sum(1 for b in bonuses if b > mean_bonus * 2)
        
        # Top content
        top_content = [
            {"content_id": s.content_id, "bonus": s.bonus_factor}
            for s in sorted(self.signal_history, key=lambda x: x.bonus_factor, reverse=True)[:10]
        ]
        
        return ArtisticObservabilityReport(
            total_signals_processed=total_signals,
            average_confidence=avg_confidence,
            dimension_averages=dim_avgs,
            dimension_distributions=dim_dists,
            bonus_statistics=bonus_stats,
            anomaly_count=anomalies,
            top_performing_content=top_content,
            policy_version=policy_version
        )

    def _calculate_histogram(self, dimension: str) -> Dict[str, float]:
        scores = [s.dimensions[dimension] for s in self.signal_history if dimension in s.dimensions]
        if not scores: return {}
        
        total = len(scores)
        buckets = defaultdict(int)
        for s in scores:
            bucket = f"{int(s//self.bucket_size)*self.bucket_size:.1f}"
            buckets[bucket] += 1
            
        return {b: c/total for b, c in buckets.items()}
