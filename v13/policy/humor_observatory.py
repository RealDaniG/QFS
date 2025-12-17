"""
HumorObservatory.py - Observability layer for humor signals

This module provides an observability layer that aggregates and analyzes humor signal outputs
over time, providing statistics and insights for operators.
"""
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from .humor_policy import HumorObservationStats

@dataclass
class HumorSignalSnapshot:
    """A snapshot of a humor signal evaluation."""
    timestamp: int
    content_id: str
    dimensions: Dict[str, float]
    confidence: float
    bonus_factor: float
    policy_version: str

@dataclass
class HumorObservabilityReport:
    """Comprehensive observability report for humor signals."""
    total_signals_processed: int
    average_confidence: float
    dimension_averages: Dict[str, float]
    dimension_distributions: Dict[str, Dict[str, float]]
    bonus_statistics: Dict[str, float]
    anomaly_count: int
    top_performing_content: List[Dict[str, Any]]
    policy_settings_summary: Dict[str, Any]
    policy_version: str
    policy_hash: str

class HumorSignalObservatory:
    """
    Observability layer for humor signals.
    
    This class provides:
    1. Aggregation of humor signal outputs over time
    2. Statistical analysis and distributions
    3. Anomaly detection
    4. Reporting capabilities for operators
    """

    def __init__(self):
        """Initialize the humor signal observatory."""
        self.signal_history: List[HumorSignalSnapshot] = []
        self.bucket_size = 0.1

    def record_signal(self, snapshot: HumorSignalSnapshot):
        """
        Record a humor signal snapshot.
        
        Args:
            snapshot: Humor signal snapshot to record
        """
        self.signal_history.append(snapshot)

    def get_observability_report(self, policy_version: str='', policy_hash: str='') -> HumorObservabilityReport:
        """
        Generate a comprehensive observability report.
        
        Args:
            policy_version: Current policy version
            policy_hash: Current policy hash
            
        Returns:
            HumorObservabilityReport: Comprehensive report
        """
        if not self.signal_history:
            return HumorObservabilityReport(total_signals_processed=0, average_confidence=0, dimension_averages={}, dimension_distributions={}, bonus_statistics={}, anomaly_count=0, top_performing_content=[], policy_settings_summary={}, policy_version=policy_version, policy_hash=policy_hash)
        total_signals = len(self.signal_history)
        avg_confidence = sum((s.confidence for s in self.signal_history)) / total_signals
        dimension_sums = defaultdict(float)
        dimension_counts = defaultdict(int)
        for snapshot in sorted(self.signal_history):
            for dimension, score in snapshot.dimensions.items():
                dimension_sums[dimension] += score
                dimension_counts[dimension] += 1
        dimension_averages = {dim: dimension_sums[dim] / dimension_counts[dim] for dim in dimension_sums}
        dimension_distributions = {}
        for dimension in sorted(dimension_sums):
            dimension_distributions[dimension] = self._calculate_histogram(dimension)
        bonuses = [s.bonus_factor for s in self.signal_history]
        bonus_statistics = {'mean': sum(bonuses) / len(bonuses), 'min': min(bonuses), 'max': max(bonuses), 'median': sorted(bonuses)[len(bonuses) // 2]}
        mean_bonus = bonus_statistics['mean']
        variance = sum(((b - mean_bonus) ** 2 for b in bonuses)) / len(bonuses)
        bonus_statistics['std_dev'] = variance ** 0.5
        anomaly_count = sum((1 for b in bonuses if b > mean_bonus * 2))
        sorted_signals = sorted(self.signal_history, key=lambda x: x.bonus_factor, reverse=True)
        top_performing_content = [{'content_id': signal.content_id, 'bonus_factor': signal.bonus_factor, 'dimensions': signal.dimensions, 'confidence': signal.confidence} for signal in sorted_signals[:10]]
        policy_settings_summary = {'observation_window': f'{total_signals} signals', 'data_collection_status': 'active', 'version': policy_version, 'hash': policy_hash}
        return HumorObservabilityReport(total_signals_processed=total_signals, average_confidence=avg_confidence, dimension_averages=dimension_averages, dimension_distributions=dimension_distributions, bonus_statistics=bonus_statistics, anomaly_count=anomaly_count, top_performing_content=top_performing_content, policy_settings_summary=policy_settings_summary, policy_version=policy_version, policy_hash=policy_hash)

    def _calculate_histogram(self, dimension: str) -> Dict[str, float]:
        """
        Calculate histogram distribution for a dimension.
        
        Args:
            dimension: Dimension name
            
        Returns:
            Dict: Bucket -> count mapping
        """
        dimension_scores = [snapshot.dimensions[dimension] for snapshot in self.signal_history if dimension in snapshot.dimensions]
        if not dimension_scores:
            return {}
        buckets = defaultdict(int)
        for score in sorted(dimension_scores):
            bucket = f'{int(score // self.bucket_size) * self.bucket_size:.1f}-{(int(score // self.bucket_size) + 1) * self.bucket_size:.1f}'
            buckets[bucket] += 1
        total = len(dimension_scores)
        return {bucket: count / total for bucket, count in buckets.items()}

    def get_dimension_correlations(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate correlations between humor dimensions.
        
        Returns:
            Dict: Correlation matrix
        """
        if len(self.signal_history) < 2:
            return {}
        all_dimensions = set()
        for snapshot in sorted(self.signal_history):
            all_dimensions.update(snapshot.dimensions.keys())
        correlations = {}
        dimension_lists = {dim: [snapshot.dimensions.get(dim, 0) for snapshot in self.signal_history] for dim in all_dimensions}
        for dim1 in sorted(all_dimensions):
            correlations[dim1] = {}
            for dim2 in sorted(all_dimensions):
                if dim1 == dim2:
                    correlations[dim1][dim2] = 1
                else:
                    list1 = dimension_lists[dim1]
                    list2 = dimension_lists[dim2]
                    mean1 = sum(list1) / len(list1)
                    mean2 = sum(list2) / len(list2)
                    numerator = sum(((a - mean1) * (b - mean2) for a, b in zip(list1, list2)))
                    denom1 = sum(((a - mean1) ** 2 for a in list1)) ** 0.5
                    denom2 = sum(((b - mean2) ** 2 for b in list2)) ** 0.5
                    if denom1 == 0 or denom2 == 0:
                        correlation = 0
                    else:
                        correlation = numerator / (denom1 * denom2)
                    correlations[dim1][dim2] = correlation
        return correlations

    def export_observability_data(self, policy_version: str='', policy_hash: str='') -> Dict[str, Any]:
        """
        Export observability data in a structured format.
        
        Args:
            policy_version: Current policy version
            policy_hash: Current policy hash
            
        Returns:
            Dict: Exportable observability data
        """
        report = self.get_observability_report(policy_version, policy_hash)
        export_data = {'report': {'total_signals_processed': report.total_signals_processed, 'average_confidence': report.average_confidence, 'dimension_averages': report.dimension_averages, 'bonus_statistics': report.bonus_statistics, 'anomaly_count': report.anomaly_count, 'policy_version': report.policy_version, 'policy_hash': report.policy_hash}, 'dimension_distributions': report.dimension_distributions, 'top_performing_content': report.top_performing_content, 'correlations': self.get_dimension_correlations(), 'raw_data_sample': [{'timestamp': snapshot.timestamp, 'content_id': snapshot.content_id, 'dimensions': snapshot.dimensions, 'confidence': snapshot.confidence, 'bonus_factor': snapshot.bonus_factor} for snapshot in self.signal_history[-100:]]}
        return export_data