# Production PQC Deployment Guide

**Target Environment**: Phase 3 Production Infrastructure
**Applicability**: QFS V13.5+ Signing Nodes

This document outlines the strict requirements for deploying the QFS Post-Quantum Cryptography (PQC) layer in a production environment. Unlike development environments which use pure Python, production requires high-performant C-bindings.

## 1. System Requirements

### Hardware / OS

- **OS**: Ubuntu 22.04 LTS (Jammy Jellyfish) or RHEL 8+
- **Arch**: x86_64 or ARM64
- **Memory**: Minimum 4GB RAM (for key generation overhead)

### Software

- **Python**: 3.12+
- **Library**: `liboqs` >= 0.10.1 (Open Quantum Safe)
- **Container**: Docker CE (Recommended)

## 2. Installation Steps (Ubuntu 22.04)

Building `liboqs` shared library from source is required before installing Python bindings.

```bash
# 1. Install Build Dependencies
sudo apt update
sudo apt install -y cmake ninja-build libssl-dev git build-essential python3-dev

# 2. Build liboqs (C Library)
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
# Checkout stable release tag matches production plan
git checkout 0.10.1 
mkdir build && cd build
cmake -GNinja -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=/usr/local ..
ninja
sudo ninja install

# 3. Update Linker
sudo ldconfig

# 4. Install Python Bindings
pip install liboqs-python>=0.10.0
```

## 3. Configuration & Enforcement

In production, you must strictly prevent fallback to insecure backends.

### Environment Variables

```bash
# Force the system to expect liboqs; fails if not found
export QFS_PQC_BACKEND="liboqs"

# Critical: Disable MockPQC to prevent insecure bypass
export QFS_PQC_MOCK_ALLOWED="false"

# Path config if installed in non-standard location
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

### Verification Script

Run this validation before starting any signing service:

```python
from v13.libs.PQC import get_pqc_backend

backend_info = get_pqc_backend_info() # Hypothetical helper or access internal
# Current PQC implementation might need specific introspection method, 
# e.g. checking PQC._PQC_BACKEND if exposed, or checking PQC.get_backend_info()

info = PQC.get_backend_info()
print(f"Detected PQC Backend: {info['backend']}")

assert info['backend'] == 'liboqs', \
    f"CRITICAL SECURITY FAILURE: Production requires 'liboqs', found '{info['backend']}'"

assert info['production_ready'] is True, \
    "Backend reports not production ready"

print("✅ PQC Production Compliance Verified")
```

## 4. Limitations (Phase 1-2.5)

The following configurations are **NOT SUPPORTED** for production:

- **Windows/macOS**: No official production builds. Dev/Test only.
- **Pure Python (`dilithium` package)**: Too slow for mainnet throughput constraints.
- **WSL2**: Supported for advanced development, not for production node hosting.
