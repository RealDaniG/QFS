# Crypto Library

This directory contains cryptographic utilities for QFS V13.8+, including deterministic wallet derivation and other crypto primitives.

## HD/BIP-Style Derivation

The `derivation.py` module implements a Hierarchical Deterministic (HD) wallet derivation system inspired by BIP-32 standards, adapted for QFS requirements.

### Key Features

#### Hierarchical Structure
- Master key derivation from seed
- Child key derivation (normal and hardened)
- Arbitrary derivation paths
- Extended key serialization

#### Deterministic Behavior
- Fully reproducible key generation from the same seed
- No use of random number generators
- Timestamp-controlled operations
- Compatible with Zero-Simulation requirements

#### Security Properties
- Chain codes for key separation
- Parent fingerprint tracking
- Depth tracking
- Hardened derivation for key isolation

### Components

#### ExtendedKey
Represents an extended key in the HD derivation tree:
- `key`: The actual key material (32 bytes)
- `chain_code`: Chain code for derivation (32 bytes)
- `depth`: Derivation depth (0 for master key)
- `parent_fingerprint`: Parent key identifier (4 bytes)
- `child_number`: Child index
- `is_private`: Whether this is a private key

#### Constants
- `HARDENED_OFFSET`: Offset for hardened key derivation (0x80000000)
- `MASTER_KEY_SALT`: Salt for master key derivation
- `DERIVATION_INFO_PREFIX`: Prefix for derivation info

### Usage

#### Master Key Derivation
```python
from v13.libs.crypto.derivation import derive_master_key

seed = b"your_seed_here"
master_key = derive_master_key(seed)
```

#### Child Key Derivation
```python
from v13.libs.crypto.derivation import derive_child_key, HARDENED_OFFSET

# Normal child derivation
child_key = derive_child_key(master_key, 0)

# Hardened child derivation
hardened_child_key = derive_child_key(master_key, 0 + HARDENED_OFFSET)
```

#### Path Derivation
```python
from v13.libs.crypto.derivation import derive_path

# Derive key at path m/44'/9999'/0'/0/0
path = [44 + HARDENED_OFFSET, 9999 + HARDENED_OFFSET, 0 + HARDENED_OFFSET, 0, 0]
derived_key = derive_path(master_key, path)
```

#### Creator Keypair Derivation
```python
from v13.libs.crypto.derivation import derive_creator_keypair

# Derive creator keypair for DEV scope with default path
private_key, public_address = derive_creator_keypair("DEV")

# Derive creator keypair with custom path
custom_path = [1, 2, 3]
private_key, public_address = derive_creator_keypair("TESTNET", custom_path)
```

### Testing

The HD derivation module includes comprehensive tests:
- Master key derivation
- Child key derivation (normal and hardened)
- Path derivation
- Deterministic behavior verification
- Scope validation

Run tests with:
```bash
python -m pytest v13/tests/unit/test_hd_derivation.py -v
```

### Zero-Simulation Compliance

The HD derivation module is fully Zero-Simulation compliant:
- No use of `random`, `time`, `datetime.now`, `uuid.uuid4`
- Deterministic iteration over collections using `sorted`
- No float literals in consensus surfaces
- Fully auditable operations