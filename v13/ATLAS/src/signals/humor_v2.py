"""
Refactored HumorSignalAddon Implementation for QFS V13.7

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
                "author_reputation": context.get("author_reputation", 0.5)
            }
        }
        
        # Return a dummy composite score (will be ignored by policy) and confidence
        # Actual aggregation happens in PolicyRegistry/TreasuryEngine
        composite_score = sum(dimensions.values()) / len(dimensions)
        
        return composite_score, confidence, metadata
    
    def _evaluate_timing(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Timing Dimension (Chronos) - Perfectly timed posts/responses.
        
        Uses ledger-derived metrics for deterministic evaluation.
        """
        # Use ledger-derived metrics for timing evaluation
        replays = context.get("replays", 0)
        views = context.get("views", 0)
        
        # Timing score based on replay/view ratio (viral timing)
        if views > 0:
            timing_ratio = min(1.0, replays / views)
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
        if word_count > 0:
            # Ratio of unique characters to total characters as a proxy for wordplay
            unique_chars = len(set(content.lower()))
            lexicon_ratio = min(1.0, unique_chars / char_count) if char_count > 0 else 0.0
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
        if sentence_count > 0:
            avg_words_per_sentence = word_count / sentence_count
            # Normalize to [0,1] - higher complexity suggests more surreal content
            surreal_score = min(1.0, avg_words_per_sentence / 20.0)
            return surreal_score
        
        return 0.0
    
    def _evaluate_relatability(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Relatability Dimension (Empathy) - Shared experiences, universal themes.
        
        Uses ledger-derived engagement metrics for deterministic evaluation.
        """
        # Relatability score based on engagement ratios
        views = context.get("views", 0)
        saves = context.get("saves", 0)
        
        # Empathy score based on save/view ratio (content that gets saved is relatable)
        if views > 0:
            empathy_ratio = min(1.0, saves / views)
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
        total_engagement = laughs + saves
        if total_engagement > 0:
            # Balanced engagement suggests thoughtful satire
            balance_factor = 1.0 - abs(laughs - saves) / total_engagement
            return balance_factor
        
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
        visual_score = min(1.0, (emoji_count + exclamation_count) / 10.0)
        return visual_score
    
    def _evaluate_meta_humor(self, content: str, context: Dict[str, Any]) -> float:
        """
        Evaluate Meta-Humor Dimension (Self-Aware) - Humor about humor/platform dynamics.
        
        Uses deterministic text analysis for self-referential content.
        """
        # Meta-humor score based on self-reference patterns
        content_lower = content.lower()
        
        # Count self-referential terms
        self_ref_terms = ['this', 'my', 'i', 'me']
        word_count = len(content.split())
        
        if word_count > 0:
            self_ref_count = sum(1 for word in content_lower.split() if word in self_ref_terms)
            meta_ratio = min(1.0, self_ref_count / word_count)
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
        views = context.get("views", 0)
        laughs = context.get("laughs", 0)
        saves = context.get("saves", 0)
        replays = context.get("replays", 0)
        
        # Total engagement as confidence proxy
        total_engagement = views + laughs + saves + replays
        
        # Normalize to [0,1] with diminishing returns
        confidence = 1.0 - (1.0 / (1.0 + total_engagement / 100.0))
        return min(1.0, confidence)