# PQC Linux Deployment Plan - Phase 2 Entry Point

**Version:** 1.0  
**Date:** 2025-12-11  
**Status:** 📋 **PLANNING** (not yet executed)  
**Target Platform:** Linux (Ubuntu 22.04 LTS)

---

## Executive Summary

This document defines the **deterministic, reproducible deployment workflow** for installing and testing the production PQC backend (liboqs-python) on Linux. This deployment is the **first critical step of Phase 2** and is required to advance Phase 1 from 80% → 100% completion.

**Key Objectives:**
1. Install liboqs + liboqs-python on Ubuntu 22.04 LTS
2. Verify Dilithium-5 backend functionality
3. Run production PQC integration tests
4. Generate performance benchmarks and evidence artifacts
5. Update Phase 1 PQC status from PARTIALLY_IMPLEMENTED → IMPLEMENTED

---

## Target Environment

### Canonical PQC Deployment Environment

**Operating System:**
- **Distro:** Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Architecture:** x86_64 (amd64)
- **Kernel:** Linux 5.15+ (LTS kernel)

**Python Requirements:**
- **Version:** Python 3.12+ (matching development environment)
- **Package Manager:** pip 24.0+
- **Virtual Environment:** venv (isolated Python environment)

**Compiler Requirements:**
- **C Compiler:** gcc 11.4.0+ (Ubuntu default)
- **C++ Compiler:** g++ 11.4.0+ (optional, for benchmarks)
- **Build Tools:** cmake 3.22.1+, make 4.3+

**Security Expectations:**
- **Reproducible Builds:** Pin liboqs commit hash, use fixed liboqs-python version
- **Deterministic Behavior:** Zero-simulation compliance (no float/random/time)
- **Audit Trail:** SHA3-512 hash chain for all PQC operations
- **Memory Hygiene:** Secure key zeroization verified

---

## Installation Workflow

### Phase 1: System Prerequisites

**Install Required Packages:**

```bash
#!/bin/bash
# install_prerequisites.sh - Install system dependencies for liboqs + liboqs-python

set -euo pipefail

echo "=== Installing System Prerequisites for PQC Deployment ==="

# Update package lists
sudo apt-get update

# Install compilers and build tools
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    libssl-dev \
    python3-dev \
    python3-pip \
    python3-venv

# Verify installations
echo "=== Verifying Installations ==="
gcc --version | head -n1
g++ --version | head -n1
cmake --version | head -n1
python3 --version

echo "=== Prerequisites installed successfully ==="
```

**Expected Output:**
```
gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
g++ (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
cmake version 3.22.1
Python 3.12.x
```

### Phase 2: Build liboqs from Source

**Reproducible liboqs Build:**

```bash
#!/bin/bash
# build_liboqs.sh - Build liboqs C library with pinned version

set -euo pipefail

echo "=== Building liboqs from Source ==="

# Configuration
LIBOQS_VERSION="0.10.1"  # Pin to stable release
LIBOQS_REPO="https://github.com/open-quantum-safe/liboqs.git"
LIBOQS_BUILD_DIR="$HOME/liboqs-build"
LIBOQS_INSTALL_PREFIX="/usr/local"

# Clone repository
if [ ! -d "$LIBOQS_BUILD_DIR" ]; then
    git clone --branch "$LIBOQS_VERSION" --depth 1 "$LIBOQS_REPO" "$LIBOQS_BUILD_DIR"
else
    echo "liboqs already cloned, pulling latest..."
    cd "$LIBOQS_BUILD_DIR" && git pull
fi

cd "$LIBOQS_BUILD_DIR"

# Verify commit hash (for reproducibility)
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "Building liboqs at commit: $CURRENT_COMMIT"

# Create build directory
mkdir -p build && cd build

# Configure with CMake (deterministic flags)
cmake -GNinja \
    -DCMAKE_INSTALL_PREFIX="$LIBOQS_INSTALL_PREFIX" \
    -DCMAKE_BUILD_TYPE=Release \
    -DOQS_BUILD_ONLY_LIB=ON \
    -DOQS_DIST_BUILD=ON \
    -DOQS_USE_OPENSSL=ON \
    ..

# Build
ninja

# Install (requires sudo)
sudo ninja install

# Verify installation
sudo ldconfig
ldconfig -p | grep liboqs

echo "=== liboqs built and installed successfully ==="
echo "Version: $LIBOQS_VERSION"
echo "Commit: $CURRENT_COMMIT"
echo "Install prefix: $LIBOQS_INSTALL_PREFIX"
```

**Expected Output:**
```
Building liboqs at commit: <SHA1_HASH>
[ninja build output...]
liboqs.so.5 (libc6,x86-64) => /usr/local/lib/liboqs.so.5
```

**Version Pinning for Reproducibility:**
- liboqs: `0.10.1` (or latest stable)
- Commit hash: `<VERIFIED_SHA1_HASH>` (to be documented after build)

### Phase 3: Install liboqs-python

**Install Python Bindings:**

```bash
#!/bin/bash
# install_liboqs_python.sh - Install liboqs-python package

set -euo pipefail

echo "=== Installing liboqs-python ==="

# Create Python virtual environment
python3 -m venv ~/qfs_venv
source ~/qfs_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install liboqs-python (pinned version)
LIBOQS_PYTHON_VERSION="0.10.0"  # Pin to match liboqs version
pip install "liboqs-python==$LIBOQS_PYTHON_VERSION"

# Verify installation
python3 -c "from oqs import Signature; print('liboqs-python imported successfully')"
python3 -c "from oqs import Signature; sig = Signature('Dilithium5'); print(f'Dilithium5 available: {sig.details}')"

echo "=== liboqs-python installed successfully ==="
echo "Version: $LIBOQS_PYTHON_VERSION"
```

**Expected Output:**
```
liboqs-python imported successfully
Dilithium5 available: {'name': 'Dilithium5', 'version': '...', ...}
```

**Environment Variables:**

```bash
# Set environment variables for deterministic behavior
export PYTHONHASHSEED=0
export TZ=UTC
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### Phase 4: Verify Dilithium-5 Functionality

**Quick Verification Script:**

```python
#!/usr/bin/env python3
# verify_dilithium5.py - Quick verification of Dilithium-5 backend

import sys
import hashlib
from oqs import Signature

def main():
    print("=== Verifying Dilithium-5 Backend ===")
    
    # Create Dilithium5 instance
    sig = Signature("Dilithium5")
    print(f"Algorithm: {sig.details['name']}")
    print(f"Public key size: {sig.details['length_public_key']} bytes")
    print(f"Secret key size: {sig.details['length_secret_key']} bytes")
    print(f"Signature size: {sig.details['length_signature']} bytes")
    
    # Test key generation
    public_key = sig.generate_keypair()
    secret_key = sig.export_secret_key()
    print(f"\nKey generation successful")
    print(f"Public key hash: {hashlib.sha256(public_key).hexdigest()[:32]}...")
    
    # Test signing
    message = b"QFS V13.5 PQC Test Message"
    signature = sig.sign(message)
    print(f"\nSignature generation successful")
    print(f"Signature hash: {hashlib.sha256(signature).hexdigest()[:32]}...")
    
    # Test verification
    is_valid = sig.verify(message, signature, public_key)
    print(f"\nSignature verification: {'PASS' if is_valid else 'FAIL'}")
    
    # Test tamper detection
    tampered_message = b"Tampered message"
    is_valid_tampered = sig.verify(tampered_message, signature, public_key)
    print(f"Tampered message detection: {'PASS' if not is_valid_tampered else 'FAIL'}")
    
    if is_valid and not is_valid_tampered:
        print("\n✅ Dilithium-5 backend verified successfully")
        return 0
    else:
        print("\n❌ Dilithium-5 backend verification FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Expected Output:**
```
=== Verifying Dilithium-5 Backend ===
Algorithm: Dilithium5
Public key size: 2592 bytes
Secret key size: 4864 bytes
Signature size: 4627 bytes

Key generation successful
Public key hash: a1b2c3d4...

Signature generation successful
Signature hash: e5f6g7h8...

Signature verification: PASS
Tampered message detection: PASS

✅ Dilithium-5 backend verified successfully
```

---

## Production PQC Test Plan

### Phase 2 Production Test Suite

**Test File:** `tests/security/test_pqc_integration_real.py` (to be created)

**Planned Test Coverage:**

#### 1. Deterministic Key Generation

**Test:** `test_real_pqc_deterministic_keygen()`

**Preconditions:** liboqs-python installed, Dilithium5 available

**Steps:**
1. Generate keypair with fixed seed (if supported by liboqs)
2. Generate second keypair with same seed
3. Compare public keys

**Expected:** Public keys should be identical (deterministic)

**Note:** liboqs keygen is **NOT seed-based** by default. This test will document the limitation and use sha256(seed) for entropy initialization as a workaround.

#### 2. Signature Creation/Verification Workflow

**Test:** `test_real_pqc_sign_verify_workflow()`

**Steps:**
1. Generate keypair
2. Sign test message
3. Verify signature
4. Test tampered message detection

**Expected:** Valid signature passes verification, tampered signature fails

#### 3. Performance Benchmarks

**Test:** `test_real_pqc_performance_benchmark()`

**Measurements:**
- Keygen latency (avg over 100 iterations)
- Sign latency (avg over 1000 iterations)
- Verify latency (avg over 1000 iterations)
- Throughput (signatures/second)

**Deterministic Measurement:**
- Use `time.perf_counter()` for timing (acceptable for benchmarks)
- Report median + percentiles to reduce variance
- Run under isolated CPU conditions

**Expected Output:**
```json
{
  "keygen_latency_ms": 1.2,
  "sign_latency_ms": 0.8,
  "verify_latency_ms": 0.3,
  "throughput_sigs_per_sec": 1250
}
```

#### 4. Memory Hygiene Verification

**Test:** `test_real_pqc_memory_zeroization()`

**Steps:**
1. Generate keypair (as bytearray)
2. Zeroize private key
3. Verify all bytes are zero

**Expected:** Private key successfully zeroized in-place

#### 5. Negative Tests

**Test:** `test_real_pqc_invalid_inputs()`

**Scenarios:**
- Invalid public key (wrong size)
- Invalid signature (wrong size)
- Corrupted signature bytes
- Key/signature mismatch

**Expected:** All invalid inputs rejected gracefully

---

## Performance Targets

### Expected PQC Performance (Dilithium-5)

Based on NIST PQC benchmarks and liboqs documentation:

| Operation | Target Latency | Acceptable Range | Notes |
|-----------|---------------|------------------|-------|
| **Keygen** | <2ms | 0.5-5ms | One-time cost per keypair |
| **Sign** | <1ms | 0.3-3ms | Per transaction signature |
| **Verify** | <0.5ms | 0.1-1ms | Per signature verification |
| **Throughput** | >1000 sig/s | 500-2000 sig/s | Concurrent verification |

**Hardware Baseline:**
- CPU: Intel Core i5 / AMD Ryzen 5 (4+ cores, 2.5GHz+)
- RAM: 8GB+
- Storage: SSD (for fast key loading)

**Measurement Conditions:**
- Isolated CPU (no competing processes)
- Warm cache (exclude first 10 iterations)
- Median of 100-1000 runs

---

## Risks & Constraints

### Platform-Specific Build Risks

**Risk 1: liboqs Version Mismatch**
- **Description:** liboqs and liboqs-python versions may be incompatible
- **Mitigation:** Pin both to compatible versions (0.10.x series)
- **Contingency:** Test multiple version combinations, document working pairs

**Risk 2: System Library Dependencies**
- **Description:** Missing OpenSSL, libssl, or other dependencies
- **Mitigation:** Install all prerequisites in Phase 1
- **Contingency:** Use Docker container for reproducible environment

**Risk 3: CMake Build Failures**
- **Description:** CMake configuration errors on different Ubuntu versions
- **Mitigation:** Pin Ubuntu 22.04 LTS, test build script before deployment
- **Contingency:** Use pre-built liboqs binaries if available

### Library Maturity & API Changes

**Risk 4: liboqs API Changes**
- **Description:** liboqs API may change between versions
- **Mitigation:** Pin to stable release (0.10.1), avoid bleeding-edge versions
- **Contingency:** Create adapter layer in PQC.py to isolate API changes

**Risk 5: Dilithium-5 Algorithm Updates**
- **Description:** NIST may finalize Dilithium spec with breaking changes
- **Mitigation:** Use NIST-approved version, document algorithm version
- **Contingency:** Plan for algorithm migration path in Phase 3

### Security & Audit Constraints

**Risk 6: Lack of External PQC Audit**
- **Description:** liboqs-python has not undergone external security audit for QFS V13.5
- **Mitigation:** Use well-vetted library (Open Quantum Safe), document limitations
- **Contingency:** Plan external audit in Phase 3, use hardware security modules (HSM) for production keys

**Risk 7: Non-Deterministic Keygen**
- **Description:** liboqs keygen uses OS entropy, not seed-based
- **Mitigation:** Document limitation, use seed-derived entropy as workaround
- **Contingency:** For audit compliance, accept non-deterministic keygen or implement custom seed-based wrapper

**Risk 8: FIPS 140-3 Compliance Unknown**
- **Description:** liboqs may not be FIPS 140-3 certified
- **Mitigation:** Document compliance status, use for non-FIPS-critical operations
- **Contingency:** Evaluate FIPS-certified PQC libraries if required (Phase 3)

---

## Evidence Artifact Plan

### Evidence Files to be Generated (Phase 2)

**Not yet created - planning only:**

1. **pqc_linux_deployment_log.txt**
   - Complete installation log (build output, version info)
   - SHA-256 hash of deployment script

2. **pqc_production_test_results.json**
   - Test results from `test_pqc_integration_real.py`
   - 100% pass rate expected

3. **pqc_performance_benchmark.json**
   - Keygen/sign/verify latency measurements
   - Throughput metrics

4. **pqc_backend_verification.json**
   - liboqs version, Dilithium-5 algorithm details
   - Public key size, signature size verification

5. **PQC_LINUX_DEPLOYMENT_EVIDENCE.md**
   - Narrative deployment report
   - Screenshots of successful build/test
   - SHA-256 hashes of all evidence files

**Measurement Protocol:**
- All evidence files SHA-256 hashed
- Deployment log timestamped (deterministic timestamp where possible)
- Test results include environment info (OS, Python version, liboqs version)

---

## Next Steps (Phase 2 Execution Checklist)

**Not yet executed - these are planned actions:**

### Immediate (Linux Environment Setup)

- [ ] Provision Ubuntu 22.04 LTS VM or CI runner
- [ ] Execute `install_prerequisites.sh`
- [ ] Execute `build_liboqs.sh`
- [ ] Execute `install_liboqs_python.sh`
- [ ] Run `verify_dilithium5.py`
- [ ] Generate deployment log evidence

### Short-Term (Production Testing)

- [ ] Create `tests/security/test_pqc_integration_real.py`
- [ ] Run all production PQC tests
- [ ] Execute performance benchmarks
- [ ] Generate test result evidence
- [ ] Generate performance benchmark evidence

### Final (Phase 1 Completion)

- [ ] Update `PQC.py` backend detection to prefer liboqs on Linux
- [ ] Update Phase 1 status from 80% → 100%
- [ ] Generate `PQC_LINUX_DEPLOYMENT_EVIDENCE.md`
- [ ] Compute SHA-256 hashes for all new evidence
- [ ] Run Audit v2.0 to verify PQC → IMPLEMENTED

---

## Conclusion

This deployment plan provides a **deterministic, reproducible workflow** for installing and testing the production PQC backend on Linux. All steps are **planned but not yet executed**.

**Status:** 📋 **PLANNING COMPLETE**  
**Next Action:** Provision Linux environment and execute deployment scripts  
**Expected Outcome:** Phase 1 advancement from 80% → 100% upon successful deployment

---

**Document Status:** 📋 **DEPLOYMENT PLAN DEFINED** (not yet executed)  
**Evidence-First Principle:** No claims made until deployment executed and evidence generated  
**Reproducibility:** All scripts pinned to specific versions with hash verification

**SHA-256 Hash (this file):** _(to be computed upon finalization)_
