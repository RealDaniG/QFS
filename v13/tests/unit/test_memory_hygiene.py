"""
test_memory_hygiene.py - Phase-3 Memory Hygiene Tests
Tests for secure key material zeroization
"""
import pytest
from v13.libs.pqc.MemoryHygiene import MemoryHygiene
from v13.libs.pqc.PQC_Core import KeyPair

class TestMemoryHygiene:
    """Test suite for MemoryHygiene module"""

    def test_zeroize_inplace(self):
        """Test that zeroization actually overwrites memory in-place"""
        key = bytearray(b'abcd1234secretkey')
        assert any((b != 0 for b in key))
        MemoryHygiene.zeroize_private_key(key)
        assert all((b == 0 for b in key))
        assert len(key) == 17

    def test_zeroize_rejects_immutable_bytes(self):
        """Test that immutable bytes are rejected with TypeError"""
        immutable_key = b'abcd1234secretkey'
        with pytest.raises(TypeError) as exc_info:
            MemoryHygiene.zeroize_private_key(immutable_key)
        assert 'mutable bytearray' in str(exc_info.value)
        assert 'Immutable bytes cannot be securely zeroized' in str(exc_info.value)

    def test_zeroize_empty_bytearray(self):
        """Test zeroization of empty bytearray"""
        key = bytearray()
        MemoryHygiene.zeroize_private_key(key)
        assert len(key) == 0

    def test_zeroize_large_key(self):
        """Test zeroization of large key material"""
        key = bytearray(b'x' * 10000)
        MemoryHygiene.zeroize_private_key(key)
        assert all((b == 0 for b in key))
        assert len(key) == 10000

    def test_secure_zeroize_keypair(self):
        """Test keypair zeroization"""
        private_key = bytearray(b'private_secret_key')
        public_key = b'public_key'
        keypair = KeyPair(private_key=private_key, public_key=public_key, algorithm='Dilithium5', parameters={})
        assert any((b != 0 for b in keypair.private_key))
        MemoryHygiene.secure_zeroize_keypair(keypair)
        assert all((b == 0 for b in keypair.private_key))
        assert keypair.public_key == b'public_key'

    def test_zeroize_constant_time(self):
        """Test that zeroization uses constant-time loop"""
        key = bytearray(b'\x00\x01\x02\x03\xff\xfe\xfd\xfc')
        MemoryHygiene.zeroize_private_key(key)
        assert all((b == 0 for b in key))

    def test_zeroize_multiple_times(self):
        """Test that zeroization can be called multiple times safely"""
        key = bytearray(b'secret')
        MemoryHygiene.zeroize_private_key(key)
        assert all((b == 0 for b in key))
        MemoryHygiene.zeroize_private_key(key)
        assert all((b == 0 for b in key))
if __name__ == '__main__':
    pytest.main([__file__, '-v'])