"""
DeterministicTime.py - Canonical Source of Truth for Time in QFS V13

This module defines the single source of truth for time across the QFS V13 system,
ensuring Zero-Simulation Compliance by deriving time solely from DRV Packets.
All time must be externally provided, PQC-verified, and monotonic across replay.

DESIGN CHOICES:
  - Monotonicity enforcement via stateless logical sequence (via DRV)
  - Integration with DRV_Packet.ttsTimestamp as ONLY source
  - Prevention of time regression (CIR-302 trigger condition)
  - No fallbacks, no defaults, no synthetic time
  - Full alignment with PsiSync logical time model
"""
from typing import Optional, Any

class DeterministicTime:
    """
    Static class for deterministic time operations.
    Enforces Zero-Simulation Compliance by deriving time solely from DRV Packets.
    """

    @staticmethod
    def canonical_time_from_packet(packet: Any) -> int:
        """
        Extracts the canonical deterministic timestamp from a DRV Packet.
        
        The ttsTimestamp (Time-To-Seed) in the DRV Packet is the authorized
        deterministic time source for all economics and recovery logic.
        
        This value MUST have been PQC-verified by the Consensus Layer prior
        to packet acceptance. No validation is performed here - only extraction.
        
        Returns:
            int: The deterministic timestamp (logical seconds/ticks).
            
        Raises:
            ValueError: If ttsTimestamp is missing, negative, or non-integer.
        """
        if not hasattr(packet, 'ttsTimestamp'):
            raise ValueError('DRV_Packet missing required field: ttsTimestamp')
        ts = packet.ttsTimestamp
        if not isinstance(ts, int):
            raise TypeError('DeterministicTime: ttsTimestamp must be int')
        if ts < 0:
            raise ValueError('DeterministicTime: ttsTimestamp must be non-negative')
        return ts

    @staticmethod
    def canonical_ordering_metric(packet: Any) -> int:
        """
        Combines sequence and previous hash for a deterministic ordering metric.
        
        This can be used for tie-breaking or entropy, but not for duration calculations.
        Ensures total ordering under PsiSync even if ttsTimestamp collides.
        
        Returns:
            int: A deterministic uint64 derived from sequence and previous hash.
        """
        prev_hash_int = int(packet.previous_hash, 16) if packet.previous_hash else 0
        hash_mod = prev_hash_int % 2 ** 64
        return (packet.sequence + hash_mod) % 2 ** 64

    @staticmethod
    def enforce_monotonicity(current_ts: int, prior_ts: Optional[int]) -> None:
        """
        Enforces strict monotonicity of logical time across state transitions.
        
        Required by CIR-302: "Any regression in logical time SHALL trigger immediate halt."
        
        This function is stateless - the caller must track prior_ts (e.g., from ledger head).
        
        Args:
            current_ts (int): The new timestamp (from current DRV_Packet).
            prior_ts (Optional[int]): The timestamp of the prior accepted state.
            
        Raises:
            ValueError: If current_ts < prior_ts (time regression detected).
        """
        if prior_ts is None:
            return
        if not isinstance(prior_ts, int) or prior_ts < 0:
            raise ValueError('DeterministicTime: prior_ts must be valid non-negative int')
        if current_ts < prior_ts:
            raise ValueError(f'DeterministicTime: Time regression detected! current={current_ts}, prior={prior_ts}')

    @staticmethod
    def require_timestamp(ts: int) -> None:
        """
        Validates that a timestamp is a valid non-negative integer.
        Used by economics modules to assert they received a valid timestamp.
        
        Args:
            ts: The timestamp to validate.
            
        Raises:
            ValueError: If timestamp is invalid.
        """
        if not isinstance(ts, int) or ts < 0:
            raise ValueError(f'Invalid deterministic timestamp: {ts}')

    @staticmethod
    def verify_and_use(timestamp: Any) -> None:
        """
        Explicitly prohibits raw timestamp usage.
        
        Raises:
            NotImplementedError: Always - raw timestamps are forbidden.
        """
        raise NotImplementedError('Raw timestamp injection prohibited in Phase 3. All time must originate from a PQC-verified DRV_Packet.')

    @staticmethod
    def verify_drv_packet(packet: Any, timestamp: int) -> None:
        """
        Verifies that the provided timestamp matches the DRV packet's timestamp.
        This ensures traceability of time to a signed source.
        
        Args:
            packet: The DRV_Packet object (or compatible structure with ttsTimestamp).
            timestamp: The deterministic timestamp to verify.
            
        Raises:
            ValueError: If the timestamps do not match or packet is invalid.
        """
        if hasattr(packet, 'ttsTimestamp'):
            packet_ts = packet.ttsTimestamp
        elif isinstance(packet, dict) and 'ttsTimestamp' in packet:
            packet_ts = packet['ttsTimestamp']
        else:
            raise ValueError('Invalid DRV packet: missing ttsTimestamp')
        if packet_ts != timestamp:
            raise ValueError(f'Timestamp mismatch: Packet={packet_ts}, Provided={timestamp}. Time must match DRV source.')