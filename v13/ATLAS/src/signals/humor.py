"""
Refactored HumorSignalAddon Implementation for QFS V13.7 - Zero-Simulation Compliant

This module implements the 7-dimensional comedic signal addon that conforms to
QFS V13.7 SignalAddon contract and Zero-Sim invariants.
"""

from typing import Dict, Any
from .base import SignalAddon, SignalResult
from v13.libs.economics.QAmount import QAmount
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

    def _evaluate_content(
        self, content: str, context: Dict[str, Any]
    ) -> tuple[QAmount, QAmount, Dict[str, Any]]:
        """
        Evaluate content across all 7 humor dimensions.

        Args:
            content: The content to evaluate
            context: Contextual information with ledger-derived metrics

        Returns:
            Tuple of (ignored_composite_score, confidence, metadata_with_dimensions)
        """
        dimensions = {
            "chronos": self._evaluate_timing(content, context),
            "lexicon": self._evaluate_wordplay(content, context),
            "surreal": self._evaluate_absurdity(content, context),
            "empathy": self._evaluate_relatability(content, context),
            "critique": self._evaluate_satire(content, context),
            "slapstick": self._evaluate_physical_comedy(content, context),
            "meta": self._evaluate_meta_humor(content, context),
        }
        confidence = self._calculate_confidence(context)
        metadata = {
            "signal": "comedic_value",
            "version": "v1",
            "dimensions": dimensions,
            "ledger_context": {
                "views": context.get("views", 0),
                "laughs": context.get("laughs", 0),
                "saves": context.get("saves", 0),
                "replays": context.get("replays", 0),
                "author_reputation": context.get(
                    "author_reputation", 500000000000000000
                ),
            },
        }
        dummy_score = QAmount(0)
        return (dummy_score, confidence, metadata)

    def _evaluate_timing(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Timing Dimension (Chronos) - Perfectly timed posts/responses.

        Uses ledger-derived metrics for deterministic evaluation.
        """
        replays = context.get("replays", 0)
        views = context.get("views", 1)
        if views > 0:
            scaled_replays = replays * 10000
            scaled_ratio = scaled_replays // views
            timing_ratio = min(10000, scaled_ratio)
            return QAmount(timing_ratio) // QAmount(10000)
        return QAmount(0)

    def _evaluate_wordplay(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Wordplay Dimension (Lexicon) - Clever puns, double entendres.

        Uses deterministic text analysis with ledger context.
        """
        word_count = len(content.split())
        char_count = len(content)
        if word_count > 0 and char_count > 0:
            unique_chars = len(set(content.lower()))
            scaled_ratio = unique_chars * 10000 // char_count
            lexicon_ratio = min(10000, scaled_ratio)
            return QAmount(lexicon_ratio) // QAmount(10000)
        return QAmount(0)

    def _evaluate_absurdity(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Absurdity Dimension (Surreal) - Nonsensical humor, absurdism.

        Uses deterministic text analysis with ledger context.
        """
        word_count = len(content.split())
        sentence_count = len(re.split("[.!?]+", content))
        if sentence_count > 0 and sentence_count <= 1000:
            scaled_avg = word_count * 1000 // sentence_count
            surreal_score = min(10000, scaled_avg * 200 // 1000)
            return QAmount(surreal_score) // QAmount(10000)
        return QAmount(0)

    def _evaluate_relatability(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Relatability Dimension (Empathy) - Shared experiences, universal themes.

        Uses ledger-derived engagement metrics for deterministic evaluation.
        """
        views = context.get("views", 1)
        saves = context.get("saves", 0)
        if views > 0:
            scaled_saves = saves * 10000
            scaled_ratio = scaled_saves // views
            empathy_ratio = min(10000, scaled_ratio)
            return QAmount(empathy_ratio) // QAmount(10000)
        return QAmount(0)

    def _evaluate_satire(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Satire Dimension (Critique) - Social commentary through humor.

        Uses ledger-derived metrics for deterministic evaluation.
        """
        laughs = context.get("laughs", 0)
        saves = context.get("saves", 0)
        total_engagement = laughs + saves
        if total_engagement > 0 and total_engagement <= 1000000:
            if laughs > saves:
                diff = laughs - saves
            else:
                diff = saves - laughs
            balance_numerator = (total_engagement - diff) * 10000
            balance_factor = balance_numerator // total_engagement
            return QAmount(balance_factor) // QAmount(10000)
        return QAmount(0)

    def _evaluate_physical_comedy(
        self, content: str, context: Dict[str, Any]
    ) -> QAmount:
        """
        Evaluate Physical Comedy Dimension (Slapstick) - Visual humor, memes.

        Uses deterministic text analysis for visual humor indicators.
        """
        emoji_count = len(re.findall("[😀-🙏]", content))
        exclamation_count = content.count("!")
        expressive_elements = emoji_count + exclamation_count
        if expressive_elements > 0:
            scaled_score = min(10000, expressive_elements * 10000 // 100)
            return QAmount(scaled_score) // QAmount(10000)
        return QAmount(0)

    def _evaluate_meta_humor(self, content: str, context: Dict[str, Any]) -> QAmount:
        """
        Evaluate Meta-Humor Dimension (Self-Aware) - Humor about humor/platform dynamics.

        Uses deterministic text analysis for self-referential content.
        """
        content_lower = content.lower()
        self_ref_terms = ["this", "my", "i", "me"]
        words = content_lower.split()
        word_count = len(words)
        if word_count > 0 and word_count <= 10000:
            self_ref_count = sum((1 for word in words if word in self_ref_terms))
            scaled_count = self_ref_count * 10000
            scaled_ratio = scaled_count // word_count
            meta_ratio = scaled_ratio
            return QAmount(meta_ratio) // QAmount(10000)
        return QAmount(0)

    def _calculate_confidence(self, context: Dict[str, Any]) -> QAmount:
        """
        Calculate confidence based purely on ledger-derived metrics.

        Args:
            context: Context with ledger-derived engagement metrics

        Returns:
            QAmount: Confidence value in [0,1]
        """
        views = context.get("views", 0)
        laughs = context.get("laughs", 0)
        saves = context.get("saves", 0)
        replays = context.get("replays", 0)
        total_engagement = views + laughs + saves + replays
        if total_engagement > 0 and total_engagement <= 10000000:
            if total_engagement >= 10000:
                return QAmount(95) // QAmount(100)
            elif total_engagement >= 1000:
                return QAmount(80) // QAmount(100)
            elif total_engagement >= 100:
                return QAmount(60) // QAmount(100)
            elif total_engagement >= 10:
                return QAmount(40) // QAmount(100)
            else:
                scaled_confidence = min(10000, total_engagement * 1000)
                return QAmount(scaled_confidence) // QAmount(10000)
        return QAmount(0)

