# PQC Provider Framework

This directory contains the Post-Quantum Cryptography (PQC) provider framework for QFS V13.8+, implementing an abstraction layer that supports multiple PQC algorithms while maintaining deterministic behavior for Zero-Simulation compliance.

## Architecture Overview

```
IPQCProvider (Interface)
├── ConcretePQCProvider (Production Implementation)
└── MockPQCProvider (Deterministic Testing Implementation)
```

## Components

### IPQCProvider.py
Defines the interface contract for all PQC providers:
- `PrivKeyHandle` - Opaque private key handle to prevent exposure of raw private key material
- `KeyPair` - Container with private key handle instead of raw bytes
- `ValidationResult` - Standardized validation result structure
- Abstract methods for key generation, signing, and verification
- Support for algorithm identifiers (`algo_id`)

### ConcretePQCProvider.py
Production implementation that wraps the existing PQC implementation:
- Extends the legacy PQC implementation with `algo_id` and `PrivKeyHandle` support
- Maintains backward compatibility
- Falls back to mock implementation when real backend is unavailable
- Supports multiple PQC algorithms through the `algo_id` mechanism

### MockPQCProvider.py
Deterministic mock provider for development and testing:
- Uses SHA-256 simulation for consistent, predictable results
- Fully deterministic for replay testing
- Not cryptographically secure - for testing only

## Key Features

### Algorithm Identification
All providers support explicit algorithm labeling through `algo_id`, enabling:
- Multi-algorithm support
- Clear audit trails
- Future-proof extensibility

### Opaque Private Key Handles
Private keys are never exposed as raw bytes in core logic:
- `PrivKeyHandle` encapsulates private key material
- Prevents accidental exposure in logs or memory dumps
- Enables secure memory management

### Deterministic Behavior
All operations are fully deterministic:
- Seed-based key generation
- Timestamp-controlled operations
- Audit logging with chained hashes
- Compatible with Zero-Simulation requirements

## Usage

### Key Generation
```python
provider = ConcretePQCProvider(IPQCProvider.DILITHIUM5)
log_list = []
seed = b"deterministic_seed"

keypair = provider.generate_keypair(
    log_list=log_list,
    seed=seed,
    pqc_cid="example_correlation_id",
    deterministic_timestamp=1234567890
)
```

### Signing
```python
data = {"message": "Hello, World!", "timestamp": 1234567890}
signature = provider.sign_data(
    private_key_handle=keypair.private_key_handle,
    data=data,
    log_list=log_list,
    pqc_cid="example_correlation_id",
    deterministic_timestamp=1234567890
)
```

### Verification
```python
validation_result = provider.verify_signature(
    public_key=keypair.public_key,
    data=data,
    signature=signature,
    log_list=log_list,
    pqc_cid="example_correlation_id",
    deterministic_timestamp=1234567890
)
```

## Zero-Simulation Compliance

All PQC providers are designed to be Zero-Simulation compliant:
- No use of `random`, `time`, `datetime.now`, `uuid.uuid4`
- Deterministic iteration over collections using `sorted`
- No float literals in consensus surfaces
- Full audit logging capability

## Testing

The framework includes comprehensive tests:
- Structural compatibility between providers
- Signature replayability
- Deterministic behavior verification
- Cross-provider compatibility checks

Run tests with:
```bash
python -m pytest v13/tests/unit/test_pqc_provider_consistency_shim.py -v
```