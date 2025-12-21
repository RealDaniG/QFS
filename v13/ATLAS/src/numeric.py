"""
ATLAS/src/numeric.py - ATLAS-Facing Numeric Adapters for QFS V13

Wraps QAmount / CertifiedMath primitives for ATLAS consumption.
Provides canonical serialization for API and P2P surfaces.
"""

from typing import Union, Any
import json
from ...libs.economics.QAmount import QAmount
from ...libs.BigNum128 import BigNum128

class AtlasNumeric:
    """
    ATLAS-facing numeric adapter.
    
    Wraps QAmount / CertifiedMath primitives with ATLAS-specific serialization
    and conversion methods for API and P2P surfaces.
    """
    
    @staticmethod
    def to_atlas_amount(amount: Union[QAmount, BigNum128, int, str, float]) -> QAmount:
        """
        Convert various numeric types to ATLAS-compatible QAmount.
        
        Args:
            amount: Amount to convert
            
        Returns:
            QAmount: ATLAS-compatible amount
        """
        if isinstance(amount, QAmount):
            return amount
        return QAmount(amount)
    
    @staticmethod
    def serialize_amount(amount: QAmount) -> str:
        """
        Serialize QAmount to canonical JSON for ATLAS API/P2P surfaces.
        
        Args:
            amount: QAmount to serialize
            
        Returns:
            str: Canonical JSON representation
        """
        return amount.to_canonical_json()
    
    @staticmethod
    def deserialize_amount(json_str: str) -> QAmount:
        """
        Deserialize QAmount from canonical JSON.
        
        Args:
            json_str: Canonical JSON string
            
        Returns:
            QAmount: Deserialized amount
        """
        return QAmount.from_canonical_json(json_str)
    
    @staticmethod
    def format_for_display(amount: QAmount, decimals: int = 6) -> str:
        """
        Format QAmount for human-readable display.
        
        Args:
            amount: QAmount to format
            decimals: Number of decimal places to show
            
        Returns:
            str: Formatted string for display
        """
        # Convert to string and format appropriately
        amount_str = str(amount)
        if '.' in amount_str:
            integer_part, fractional_part = amount_str.split('.')
            # Truncate or pad fractional part to desired decimals
            formatted_fractional = fractional_part[:decimals].ljust(decimals, '0')
            return f"{integer_part}.{formatted_fractional}".rstrip('0').rstrip('.')
        else:
            return amount_str

# Convenience functions for common operations
def atlas_amount(value: Union[QAmount, BigNum128, int, str, float]) -> QAmount:
    """
    Convenience function to create ATLAS-compatible QAmount.
    
    Args:
        value: Value to convert to QAmount
        
    Returns:
        QAmount: ATLAS-compatible amount
    """
    return AtlasNumeric.to_atlas_amount(value)

def serialize_atlas_amount(amount: QAmount) -> str:
    """
    Convenience function to serialize QAmount for ATLAS.
    
    Args:
        amount: QAmount to serialize
        
    Returns:
        str: Canonical JSON representation
    """
    return AtlasNumeric.serialize_amount(amount)

def deserialize_atlas_amount(json_str: str) -> QAmount:
    """
    Convenience function to deserialize QAmount from ATLAS.
    
    Args:
        json_str: Canonical JSON string
        
    Returns:
        QAmount: Deserialized amount
    """
    return AtlasNumeric.deserialize_amount(json_str)
