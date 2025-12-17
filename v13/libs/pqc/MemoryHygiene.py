"""
MemoryHygiene.py - Phase-3 Module 2.4
Secure Memory Zeroization for PQC Key Material

Zero-Simulation Compliant, Side-Channel Resistant
"""
from typing import Union

class MemoryHygiene:
    """
    Provides secure memory zeroization for cryptographic key material.
    Uses constant-time operations for side-channel resistance.
    """

    @staticmethod
    def zeroize_private_key(private_key: bytearray) -> None:
        """
        Overwrites the provided key material in-place with zeros.
        Only accepts bytearray, ensuring actual memory zeroization.
        
        Args:
            private_key: Mutable key material to zeroize (bytearray)
            
        Raises:
            TypeError: If private_key is not a bytearray
            
        Note:
            Uses constant-time loop for side-channel resistance.
            Immutable bytes cannot be securely zeroized and will raise TypeError.
        """
        if not isinstance(private_key, bytearray):
            raise TypeError('zeroize_private_key() requires a mutable bytearray. Immutable bytes cannot be securely zeroized.')
        for i in range(len(private_key)):
            private_key[i] = 0

    @staticmethod
    def secure_zeroize_keypair(keypair) -> None:
        """
        Securely zeroizes a keypair's private key material.
        
        Args:
            keypair: KeyPair object with private_key attribute
        """
        MemoryHygiene.zeroize_private_key(keypair.private_key)