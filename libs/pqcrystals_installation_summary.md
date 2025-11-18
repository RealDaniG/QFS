# pqcrystals Installation Summary

## Installation Steps Completed

1. **Installed Python packages:**
   - `pqcrypto` - Provides post-quantum cryptography functions including ML-KEM (standardized Kyber)
   - `kyber` - A namespace package (though not functional on its own)
   - `liboqs-python` - Python bindings for the Open Quantum Safe library

2. **Cloned source code repositories:**
   - `kyber` - Official reference implementation of the Kyber key encapsulation mechanism
   - `liboqs` - Open Quantum Safe library with implementations of various post-quantum algorithms

## Available Post-Quantum Algorithms

The `pqcrypto` package provides several post-quantum cryptography algorithms:

### Key Encapsulation Mechanisms (KEM)
- **ML-KEM** (Standardized version of Kyber):
  - ML-KEM-512 (with 128-bit security)
  - ML-KEM-768 (with 192-bit security)
  - ML-KEM-1024 (with 256-bit security)
- **HQC** (Hamming Quasi-Cyclic)
- **McEliece** variants

### Digital Signature Schemes
- **Dilithium**
- **SPHINCS+**
- **Falcon**

## Usage Example

To use ML-KEM (Kyber) in Python:

```python
from pqcrypto.kem import ml_kem_512

# Generate a keypair
public_key, secret_key = ml_kem_512.generate_keypair()

# Encapsulate a shared secret using the public key
ciphertext, shared_secret = ml_kem_512.encrypt(public_key)

# Decapsulate to recover the shared secret using the secret key
recovered_secret = ml_kem_512.decrypt(ciphertext, secret_key)
```

## Building from Source

To build the C implementations:

1. **Kyber reference implementation:**
   ```bash
   cd kyber/ref
   make
   ```

2. **Kyber AVX2-optimized implementation (for x86 CPUs with AVX2):**
   ```bash
   cd kyber/avx2
   make
   ```

Note: Building from source requires a C compiler and Make utility.

## Next Steps

1. **For immediate use:** Use the `pqcrypto` Python package which provides ML-KEM (Kyber) implementations
2. **For performance:** Build the C implementations from the cloned kyber repository
3. **For broader algorithm support:** Install and build the liboqs library