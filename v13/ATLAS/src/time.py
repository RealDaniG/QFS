"""
ATLAS/src/time.py - ATLAS-Facing Time Adapters for QFS V13

Wraps deterministic time functions for ATLAS consumption.
Provides canonical serialization for API and P2P surfaces.
"""

from typing import Union
from ...libs.deterministic.time import (
    det_time_now, det_perf_counter, det_time_isoformat,
    det_timestamp_ms, det_timestamp_us
)

class AtlasTime:
    """
    ATLAS-facing time adapter.
    
    Wraps deterministic time functions with ATLAS-specific serialization
    and conversion methods for API and P2P surfaces.
    """
    
    @staticmethod
    def current_timestamp() -> int:
        """
        Get current deterministic timestamp.
        
        Returns:
            int: Current timestamp in seconds since epoch
        """
        return det_time_now()
    
    @staticmethod
    def current_timestamp_ms() -> int:
        """
        Get current deterministic timestamp in milliseconds.
        
        Returns:
            int: Current timestamp in milliseconds since epoch
        """
        return det_timestamp_ms()
    
    @staticmethod
    def current_timestamp_us() -> int:
        """
        Get current deterministic timestamp in microseconds.
        
        Returns:
            int: Current timestamp in microseconds since epoch
        """
        return det_timestamp_us()
    
    @staticmethod
    def iso_format_timestamp() -> str:
        """
        Get current deterministic timestamp in ISO format.
        
        Returns:
            str: ISO format timestamp string
        """
        return det_time_isoformat()
    
    @staticmethod
    def performance_counter() -> float:
        """
        Get deterministic performance counter value.
        
        Returns:
            float: Performance counter value
        """
        return det_perf_counter()
    
    @staticmethod
    def serialize_timestamp(timestamp: Union[int, float]) -> str:
        """
        Serialize timestamp to canonical string format for ATLAS.
        
        Args:
            timestamp: Timestamp to serialize
            
        Returns:
            str: Canonical string representation
        """
        if isinstance(timestamp, float):
            # Format float timestamps with fixed precision
            return f"{timestamp:.6f}"
        else:
            return str(timestamp)

# Convenience functions for common operations
def atlas_timestamp() -> int:
    """
    Convenience function to get current ATLAS timestamp.
    
    Returns:
        int: Current timestamp in seconds since epoch
    """
    return AtlasTime.current_timestamp()

def atlas_timestamp_ms() -> int:
    """
    Convenience function to get current ATLAS timestamp in milliseconds.
    
    Returns:
        int: Current timestamp in milliseconds since epoch
    """
    return AtlasTime.current_timestamp_ms()

def atlas_timestamp_us() -> int:
    """
    Convenience function to get current ATLAS timestamp in microseconds.
    
    Returns:
        int: Current timestamp in microseconds since epoch
    """
    return AtlasTime.current_timestamp_us()

def atlas_iso_timestamp() -> str:
    """
    Convenience function to get current ATLAS timestamp in ISO format.
    
    Returns:
        str: ISO format timestamp string
    """
    return AtlasTime.iso_format_timestamp()

def serialize_atlas_timestamp(timestamp: Union[int, float]) -> str:
    """
    Convenience function to serialize timestamp for ATLAS.
    
    Args:
        timestamp: Timestamp to serialize
        
    Returns:
        str: Canonical string representation
    """
    return AtlasTime.serialize_timestamp(timestamp)
