"""
Refactored HumorSignalAddon Implementation for QFS V13.7 - Zero-Simulation Compliant

This module implements the 7-dimensional comedic signal addon that conforms to 
QFS V13.7 SignalAddon contract and Zero-Sim invariants.
"""

from typing import Dict, Any
from .base import SignalAddon, SignalResult
import hashlib
import json
import re


class HumorSignalAddon(SignalAddon):
    """
    7-Dimensional Comedic Signal Addon for QFS V13.7
    
    Provides a pure signal vector with 7 normalized scores in [0,1], one per dimension.
    Aggregation and reward calculation happens in PolicyRegistry/TreasuryEngine.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the HumorSignalAddon.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__("humor_signal_addon", config)
    
    def _evaluate_content(self, content: str, context: Dict[str, Any]) -> tuple[float, float, Dict[str, Any]]:
        """
        Evaluate content across all 7 humor dimensions.
        
        Args:
            content: The content to evaluate
            context: Contextual information with ledger-derived metrics
            
        Returns:
            Tuple of (ignored_composite_score, confidence, metadata_with_dimensions)
        """
        # Evaluate each humor dimension as pure signals
        dimensions = {
            "chronos": self._evaluate_timing(content, context),
            "lexicon": self._evaluate_wordplay(content, context),
            "surreal": self._evaluate_absurdity(content, context),
            "empathy": self._evaluate_relatability(content, context),
            "critique": self._evaluate_satire(content, context),
            "slapstick": self._evaluate_physical_comedy(content, context),
            "meta": self._evaluate_meta_humor(content, context)
        }
        
        # Confidence is purely a function of ledger-derived metrics
        confidence = self._calculate_confidence(context)
        
        # Create metadata with dimensions and ledger context
        metadata = {
            "signal": "comedic_value",
            "version": "v1",
            "dimensions": dimensions,
            "ledger_context": {
                "views": context.get("views", 0),
                "laughs": context.get("laughs", 0),
                "saves": context.get("saves", 0),
                "replays": context.get("replays", 0),
                "author_reputation": context.get("author_reputation", 500000000000000000)  # 0.5 as integer scaled by 10^18
            }
        }
        
        # Return a dummy score (will be ignored by policy) and confidence
        # Actual aggregation happens in PolicyRegistry/TreasuryEngine
        # Return 0.0 as dummy score since aggregation happens elsewhere
        dummy_score = 0.0
        
        return dummy_score, confidence, metadata
    
    def _evaluate_timing(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Timing Dimension (Chronos) - Perfectly timed posts/responses.
        
        Uses ledger-derived metrics for deterministic evaluation.
        """
        # Use ledger-derived metrics for timing evaluation
        replays = context.get("replays", 0)
        views = context.get("views", 1)  # Avoid division by zero
        
        # Timing score based on replay/view ratio (viral timing)
        # Use only ledger-derived metrics for deterministic evaluation
        if views > 0:
            # Calculate timing ratio using integer math to avoid floating point issues
            # Scale by 10000 to preserve precision in integer operations
            scaled_replays = replays * 10000
            scaled_ratio = scaled_replays // views
            # Convert back to [0,1] range
            timing_ratio = min(10000, scaled_ratio) / 10000
            return timing_ratio
        
        return 0.0
    
    def _evaluate_wordplay(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Wordplay Dimension (Lexicon) - Clever puns, double entendres.
        
        Uses deterministic text analysis with ledger context.
        """
        # Count linguistic complexity indicators
        word_count = len(content.split())
        char_count = len(content)
        
        # Lexicon score based on linguistic diversity
        # Use deterministic calculation based on content characteristics
        if word_count > 0 and char_count > 0:
            unique_chars = len(set(content.lower()))
            # Scale by 10000 to preserve precision
            scaled_ratio = (unique_chars * 10000) // char_count
            lexicon_ratio = min(10000, scaled_ratio) / 10000
            return lexicon_ratio
        
        return 0.0
    
    def _evaluate_absurdity(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Absurdity Dimension (Surreal) - Nonsensical humor, absurdism.
        
        Uses deterministic text analysis with ledger context.
        """
        # Absurdity score based on text structure anomalies
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        
        # Surreal score based on sentence complexity
        # Use deterministic calculation based on content structure
        if sentence_count > 0 and sentence_count <= 1000:  # Reasonable bounds
            # Calculate average words per sentence with scaling
            scaled_avg = (word_count * 1000) // sentence_count
            # Normalize to [0,1] with reasonable bounds
            # Assume maximum reasonable complexity is 50 words per sentence
            surreal_score = min(10000, scaled_avg * 200 // 1000) / 10000
            return surreal_score
        
        return 0.0
    
    def _evaluate_relatability(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Relatability Dimension (Empathy) - Shared experiences, universal themes.
        
        Uses ledger-derived engagement metrics for deterministic evaluation.
        """
        # Relatability score based on engagement ratios
        views = context.get("views", 1)  # Avoid division by zero
        saves = context.get("saves", 0)
        
        # Empathy score based on save/view ratio (content that gets saved is relatable)
        # Use only ledger-derived metrics for deterministic evaluation
        if views > 0:
            # Calculate empathy ratio using integer math
            scaled_saves = saves * 10000
            scaled_ratio = scaled_saves // views
            empathy_ratio = min(10000, scaled_ratio) / 10000
            return empathy_ratio
        
        return 0.0
    
    def _evaluate_satire(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Satire Dimension (Critique) - Social commentary through humor.
        
        Uses ledger-derived metrics for deterministic evaluation.
        """
        # Critique score based on engagement diversity
        laughs = context.get("laughs", 0)
        saves = context.get("saves", 0)
        
        # Satire score based on balanced engagement (both laughs and saves)
        # Use only ledger-derived metrics for deterministic evaluation
        total_engagement = laughs + saves
        if total_engagement > 0 and total_engagement <= 1000000:  # Reasonable bounds
            # Calculate balance factor using integer math
            # Balanced engagement suggests thoughtful satire
            if laughs > saves:
                diff = laughs - saves
            else:
                diff = saves - laughs
            
            # Calculate balance as (total - diff) / total
            balance_numerator = (total_engagement - diff) * 10000
            balance_factor = balance_numerator // total_engagement
            return balance_factor / 10000
        
        return 0.0
    
    def _evaluate_physical_comedy(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Physical Comedy Dimension (Slapstick) - Visual humor, memes.
        
        Uses deterministic text analysis for visual humor indicators.
        """
        # Slapstick score based on visual indicators
        emoji_count = len(re.findall(r'[😀-🙏]', content))
        exclamation_count = content.count('!')
        
        # Physical comedy score based on expressive elements
        # Use deterministic calculation based on content features
        expressive_elements = emoji_count + exclamation_count
        if expressive_elements > 0:
            # Scale by 10000 to preserve precision
            scaled_score = min(10000, expressive_elements * 10000 // 100)  # Normalize by 100
            visual_score = scaled_score / 10000
            return visual_score
        
        return 0.0
    
    def _evaluate_meta_humor(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Meta-Humor Dimension (Self-Aware) - Humor about humor/platform dynamics.
        
        Uses deterministic text analysis for self-referential content.
        """
        # Meta-humor score based on self-reference patterns
        content_lower = content.lower()
        
        # Count self-referential terms
        self_ref_terms = ['this', 'my', 'i', 'me']
        words = content_lower.split()
        word_count = len(words)
        
        if word_count > 0 and word_count <= 10000:  # Reasonable bounds
            self_ref_count = sum(1 for word in words if word in self_ref_terms)
            # Calculate ratio using integer math
            scaled_count = self_ref_count * 10000
            scaled_ratio = scaled_count // word_count
            meta_ratio = scaled_ratio / 10000
            return meta_ratio
        
        return 0.0
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """
        Calculate confidence based purely on ledger-derived metrics.
        
        Args:
            context: Context with ledger-derived engagement metrics
            
        Returns:
            float: Confidence value in [0,1]
        """
        # Confidence based on total engagement volume
        # Use only ledger-derived metrics for deterministic evaluation
        views = context.get("views", 0)
        laughs = context.get("laughs", 0)
        saves = context.get("saves", 0)
        replays = context.get("replays", 0)
        
        # Total engagement as confidence proxy
        total_engagement = views + laughs + saves + replays
        
        # Normalize to [0,1] with diminishing returns
        # Using integer math for deterministic behavior
        if total_engagement > 0 and total_engagement <= 10000000:  # Reasonable upper bound
            # Apply logarithmic-like scaling for diminishing returns
            # For simplicity, use square root-like scaling: sqrt(x) ≈ x^(1/2)
            # We'll approximate with integer operations
            if total_engagement >= 10000:
                # Cap at high confidence for substantial engagement
                return 0.95
            elif total_engagement >= 1000:
                return 0.8
            elif total_engagement >= 100:
                return 0.6
            elif total_engagement >= 10:
                return 0.4
            else:
                # Linear scaling for very low engagement
                scaled_confidence = min(10000, total_engagement * 1000)
                return scaled_confidence / 10000
        
        return 0.0