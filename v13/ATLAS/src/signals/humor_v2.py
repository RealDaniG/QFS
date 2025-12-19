"""
from v13.libs.economics.QAmount import QAmount
Refactored HumorSignalAddon Implementation for QFS V13.7

This module implements the 7-dimensional comedic signal addon that conforms to 
QFS V13.7 SignalAddon contract and Zero-Sim invariants.
"""
from fractions import Fraction
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

    def __init__(self, config: Dict[str, Any]=None):
        """
        Initialize the HumorSignalAddon.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__('humor_signal_addon', config)

    def _evaluate_content(self, content: str, context: Dict[str, Any]) -> tuple[float, float, Dict[str, Any]]:
        """
        Evaluate content across all 7 humor dimensions.
        
        Args:
            content: The content to evaluate
            context: Contextual information with ledger-derived metrics
            
        Returns:
            Tuple of (ignored_composite_score, confidence, metadata_with_dimensions)
        """
        dimensions = {'chronos': self._evaluate_timing(content, context), 'lexicon': self._evaluate_wordplay(content, context), 'surreal': self._evaluate_absurdity(content, context), 'empathy': self._evaluate_relatability(content, context), 'critique': self._evaluate_satire(content, context), 'slapstick': self._evaluate_physical_comedy(content, context), 'meta': self._evaluate_meta_humor(content, context)}
        confidence = self._calculate_confidence(context)
        metadata = {'signal': 'comedic_value', 'version': 'v1', 'dimensions': dimensions, 'ledger_context': {'views': context.get('views', 0), 'laughs': context.get('laughs', 0), 'saves': context.get('saves', 0), 'replays': context.get('replays', 0), 'author_reputation': context.get('author_reputation', Fraction(1, 2))}}
        composite_score = sum(dimensions.values()) / len(dimensions)
        return (composite_score, confidence, metadata)

    def _evaluate_timing(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Timing Dimension (Chronos) - Perfectly timed posts/responses.
        
        Uses ledger-derived metrics for deterministic evaluation.
        """
        replays = context.get('replays', 0)
        views = context.get('views', 0)
        if views > 0:
            timing_ratio = min(1, replays / views)
            return timing_ratio
        return 0

    def _evaluate_wordplay(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Wordplay Dimension (Lexicon) - Clever puns, double entendres.
        
        Uses deterministic text analysis with ledger context.
        """
        word_count = len(content.split())
        char_count = len(content)
        if word_count > 0:
            unique_chars = len(set(content.lower()))
            lexicon_ratio = min(1, unique_chars / char_count) if char_count > 0 else 0
            return lexicon_ratio
        return 0

    def _evaluate_absurdity(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Absurdity Dimension (Surreal) - Nonsensical humor, absurdism.
        
        Uses deterministic text analysis with ledger context.
        """
        word_count = len(content.split())
        sentence_count = len(re.split('[.!?]+', content))
        if sentence_count > 0:
            avg_words_per_sentence = word_count / sentence_count
            surreal_score = min(1, avg_words_per_sentence / 20)
            return surreal_score
        return 0

    def _evaluate_relatability(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Relatability Dimension (Empathy) - Shared experiences, universal themes.
        
        Uses ledger-derived engagement metrics for deterministic evaluation.
        """
        views = context.get('views', 0)
        saves = context.get('saves', 0)
        if views > 0:
            empathy_ratio = min(1, saves / views)
            return empathy_ratio
        return 0

    def _evaluate_satire(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Satire Dimension (Critique) - Social commentary through humor.
        
        Uses ledger-derived metrics for deterministic evaluation.
        """
        laughs = context.get('laughs', 0)
        saves = context.get('saves', 0)
        total_engagement = laughs + saves
        if total_engagement > 0:
            balance_factor = 1 - abs(laughs - saves) / total_engagement
            return balance_factor
        return 0

    def _evaluate_physical_comedy(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Physical Comedy Dimension (Slapstick) - Visual humor, memes.
        
        Uses deterministic text analysis for visual humor indicators.
        """
        emoji_count = len(re.findall('[😀-🙏]', content))
        exclamation_count = content.count('!')
        visual_score = min(1, (emoji_count + exclamation_count) / 10)
        return visual_score

    def _evaluate_meta_humor(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Meta-Humor Dimension (Self-Aware) - Humor about humor/platform dynamics.
        
        Uses deterministic text analysis for self-referential content.
        """
        content_lower = content.lower()
        self_ref_terms = ['this', 'my', 'i', 'me']
        word_count = len(content.split())
        if word_count > 0:
            self_ref_count = sum((1 for word in content_lower.split() if word in self_ref_terms))
            meta_ratio = min(1, self_ref_count / word_count)
            return meta_ratio
        return 0

    def _calculate_confidence(self, context: Dict[str, Any]) -> QAmount:
        """
        Calculate confidence based purely on ledger-derived metrics.
        
        Args:
            context: Context with ledger-derived engagement metrics
            
        Returns:
            float: Confidence value in [0,1]
        """
        views = context.get('views', 0)
        laughs = context.get('laughs', 0)
        saves = context.get('saves', 0)
        replays = context.get('replays', 0)
        total_engagement = views + laughs + saves + replays
        confidence = 1 - 1 / (1 + total_engagement / 100)
        return min(1, confidence)