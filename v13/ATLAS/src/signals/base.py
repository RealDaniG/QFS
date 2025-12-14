"""
Base SignalAddon Framework for QFS V13.7

This module provides the base framework for deterministic, isolated SignalAddons
that evaluate content and context to produce signal results.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import json


@dataclass
class SignalResult:
    """Result of a SignalAddon evaluation"""
    addon_id: str
    score: float  # Normalized score between 0.0 and 1.0
    confidence: float  # Confidence in the score between 0.0 and 1.0
    metadata: Dict[str, Any]  # Additional metadata about the evaluation
    content_hash: str  # Hash of the content that was evaluated
    context_hash: str  # Hash of the context that was evaluated
    result_hash: str  # Hash of the entire result for deterministic verification

    def __post_init__(self):
        """Generate deterministic hash for the result"""
        if not self.result_hash:
            # Create a deterministic representation of the result
            result_data = {
                "addon_id": self.addon_id,
                "score": self.score,
                "confidence": self.confidence,
                "metadata": self.metadata,
                "content_hash": self.content_hash,
                "context_hash": self.context_hash
            }
            # Sort keys for deterministic JSON serialization
            result_json = json.dumps(result_data, sort_keys=True, separators=(',', ':'))
            self.result_hash = hashlib.sha256(result_json.encode('utf-8')).hexdigest()


class SignalAddon:
    """
    Base class for SignalAddons in the QFS ecosystem.
    
    SignalAddons are deterministic evaluators that take content and context
    and produce signal results. They must adhere to strict invariants:
    
    1. No Side Effects: evaluate() must not mutate global state
    2. Deterministic: Same inputs must always produce same outputs
    3. Isolation: No cross-addon dependencies
    4. No External I/O: No network calls to non-content-addressed storage
    """
    
    def __init__(self, addon_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SignalAddon.
        
        Args:
            addon_id: Unique identifier for this addon
            config: Optional configuration dictionary
        """
        self.addon_id = addon_id
        self.config = config or {}
    
    def evaluate(self, content: str, context: Dict[str, Any]) -> SignalResult:
        """
        Evaluate content and context to produce a signal result.
        
        This method must be implemented by subclasses and must be deterministic.
        
        Args:
            content: The content to evaluate (e.g., post text, image data)
            context: Contextual information (e.g., user info, engagement metrics)
            
        Returns:
            SignalResult: The evaluation result
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")
        
        # Create deterministic hashes of inputs
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Sort keys for deterministic JSON serialization
        context_json = json.dumps(context, sort_keys=True, separators=(',', ':'))
        context_hash = hashlib.sha256(context_json.encode('utf-8')).hexdigest()
        
        # Perform the actual evaluation
        score, confidence, metadata = self._evaluate_content(content, context)
        
        # Create and return the result
        return SignalResult(
            addon_id=self.addon_id,
            score=score,
            confidence=confidence,
            metadata=metadata,
            content_hash=content_hash,
            context_hash=context_hash,
            result_hash=""  # Will be generated in __post_init__
        )
    
    def _evaluate_content(self, content: str, context: Dict[str, Any]) -> tuple[float, float, Dict[str, Any]]:
        """
        Internal method to perform the actual content evaluation.
        
        Subclasses must implement this method.
        
        Args:
            content: The content to evaluate
            context: Contextual information
            
        Returns:
            Tuple of (score, confidence, metadata)
        """
        raise NotImplementedError("_evaluate_content must be implemented by subclasses")
    
    def get_addon_info(self) -> Dict[str, Any]:
        """
        Get information about this addon.
        
        Returns:
            Dictionary with addon information
        """
        return {
            "addon_id": self.addon_id,
            "type": self.__class__.__name__,
            "config": self.config
        }
