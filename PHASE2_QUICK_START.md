# QFS V13.5 Phase 2 - Quick Start Guide

**Phase 1 Status:** ✅ CLOSED AT 80% COMPLETION  
**Phase 2 Objective:** Linux PQC Deployment → 100% Phase 1 Completion  
**Target Duration:** ~4 hours

---

## Context

Phase 1 closed with 4/5 CRITICAL components IMPLEMENTED. The remaining component (PQC) has:
- ✅ Implementation code complete (590 lines, production-ready)
- ✅ Mock integration tests passing (7/7, 100%)
- ❌ Production backend blocked (liboqs-python Windows compilation failure)

**Solution:** Deploy on Linux (Ubuntu 22.04 LTS) where liboqs-python works natively.

---

## Phase 2 Entry: 5 Concrete Actions

### Action 1: Provision Linux Environment (30 min)

**Options:**

```bash
# Option A: Multipass VM (recommended for local development)
multipass launch 22.04 --name qfs-pqc-build --cpus 4 --mem 8G --disk 40G
multipass shell qfs-pqc-build

# Option B: Docker Container
docker run -it --name qfs-pqc-build ubuntu:22.04 /bin/bash

# Option C: GitHub Actions (for CI/CD)
# Use ubuntu-22.04 runner in .github/workflows/pqc-deployment.yml
```

**Success Criteria:**
- Ubuntu 22.04 LTS running
- 4+ CPU cores, 8GB+ RAM
- Network access to GitHub & PyPI

---

### Action 2: Install liboqs C Library (15 min)

**Script:** Create `scripts/install_liboqs.sh` from deployment plan

```bash
#!/bin/bash
set -euo pipefail

# Install system prerequisites
sudo apt-get update
sudo apt-get install -y build-essential cmake git ninja-build libssl-dev python3-dev python3-pip python3-venv

# Clone and build liboqs
LIBOQS_VERSION="0.10.1"
git clone --branch "$LIBOQS_VERSION" --depth 1 https://github.com/open-quantum-safe/liboqs.git ~/liboqs-build
cd ~/liboqs-build

mkdir -p build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_BUILD_TYPE=Release -DOQS_BUILD_ONLY_LIB=ON -DOQS_DIST_BUILD=ON -DOQS_USE_OPENSSL=ON ..
ninja
sudo ninja install
sudo ldconfig

# Verify
ldconfig -p | grep liboqs
```

**Run:**
```bash
bash scripts/install_liboqs.sh 2>&1 | tee ~/pqc_linux_deployment_log.txt
```

**Evidence:** `pqc_linux_deployment_log.txt` with SHA-256 hash

---

### Action 3: Install liboqs-python & Verify (5 min)

**Commands:**

```bash
# Create virtual environment
python3 -m venv ~/qfs_venv
source ~/qfs_venv/bin/activate

# Install liboqs-python
pip install liboqs-python==0.10.0

# Verify Dilithium-5
python3 -c "from oqs import Signature; sig = Signature('Dilithium5'); print(f'✅ Dilithium5 available: {sig.details}')"
```

**Quick Test:** Create `scripts/verify_dilithium5.py`

```python
#!/usr/bin/env python3
import sys
import hashlib
from oqs import Signature

sig = Signature("Dilithium5")
print(f"Algorithm: {sig.details['name']}")
print(f"Public key size: {sig.details['length_public_key']} bytes")

# Test sign/verify
public_key = sig.generate_keypair()
message = b"QFS V13.5 PQC Test"
signature = sig.sign(message)
is_valid = sig.verify(message, signature, public_key)

print(f"Signature verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
sys.exit(0 if is_valid else 1)
```

**Run:** `python3 scripts/verify_dilithium5.py`

**Evidence:** `dilithium5_quick_test.log`

---

### Action 4: Create Production PQC Tests (2 hours)

**File:** `tests/security/test_pqc_integration_real.py`

**Template:** Copy from `test_pqc_integration_mock.py` and adapt:

```python
"""
Production PQC Integration Tests - Real Dilithium-5 Backend

Tests real liboqs-python backend (NOT mock).
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from libs.PQC import PQC
from libs.BigNum128 import BigNum128

class TestPQCIntegrationReal:
    """Production PQC tests using real Dilithium-5 backend"""
    
    def test_real_backend_detection(self):
        """Verify real PQC backend is active"""
        backend_info = PQC.get_backend_info()
        assert backend_info["backend"] in ["liboqs", "pqcrystals"]
        assert backend_info["production_ready"] is True
        assert backend_info["quantum_resistant"] is True
    
    def test_real_sign_verify_workflow(self):
        """Test sign/verify with real Dilithium-5"""
        # ... (copy from mock test and adapt)
    
    def test_real_performance_benchmark(self):
        """Measure real PQC performance"""
        import time
        
        # Keygen latency
        keygen_times = []
        for _ in range(100):
            start = time.perf_counter()
            PQC.generate_keypair(log_list=[], seed=b"test_seed")
            keygen_times.append(time.perf_counter() - start)
        
        median_keygen_ms = sorted(keygen_times)[50] * 1000
        print(f"\n✅ Keygen latency: {median_keygen_ms:.2f}ms")
        
        # Assert performance target
        assert median_keygen_ms < 5.0, "Keygen too slow"
```

**Run:**
```bash
PYTHONHASHSEED=0 TZ=UTC python -m pytest tests/security/test_pqc_integration_real.py -v --tb=short
```

**Evidence:** `pqc_production_test_results.json`

---

### Action 5: Generate Evidence & Update Status (1 hour)

**Commands:**

```bash
# Generate performance benchmark
python scripts/benchmark_pqc_performance.py > evidence/phase2/pqc_performance_benchmark.json

# Compute evidence hashes
cd evidence/phase2
sha256sum *.json *.log > evidence_hashes_phase2.txt

# Create deployment report
# (manual: PQC_LINUX_DEPLOYMENT_EVIDENCE.md)
```

**Update Phase 1 Status:**

Edit `ROADMAP-V13.5-REMEDIATION.md`:
```diff
- PQC: 🟡 PARTIALLY_IMPLEMENTED (mock only, platform-blocked)
+ PQC: ✅ IMPLEMENTED (liboqs-python on Linux, all tests passing)

- Phase 1: 80% (4/5 CRITICAL)
+ Phase 1: 100% (5/5 CRITICAL)
```

**Evidence:** 
- `pqc_performance_benchmark.json`
- `PQC_LINUX_DEPLOYMENT_EVIDENCE.md`
- `evidence_hashes_phase2.txt`

---

## Success Criteria Checklist

Phase 2 deployment is successful when:

- [ ] Ubuntu 22.04 LTS environment provisioned
- [ ] liboqs C library built and installed
- [ ] liboqs-python package installed
- [ ] Dilithium-5 backend verified (quick test passing)
- [ ] Production PQC tests created and passing (100%)
- [ ] Performance benchmarks within acceptable ranges (<5ms keygen, <1ms sign, <0.5ms verify)
- [ ] Evidence artifacts generated with SHA-256 hashes
- [ ] Phase 1 status updated to 100%
- [ ] PQC status updated to IMPLEMENTED

---

## Reference Documents

**Must Read Before Starting:**

1. **PQC Deployment Plan:** `docs/deployment/PQC_DEPLOYMENT_PLAN_LINUX.md`
   - Complete installation workflow
   - Performance targets
   - Risks & mitigations

2. **Phase 1 Closure Report:** `evidence/phase1/QFS_V13.5_PHASE1_CLOSURE_REPORT.md`
   - Compliance mapping
   - Outstanding requirements

3. **Phase 1 → Phase 2 Handoff:** `evidence/phase1/QFS_V13.5_PHASE1_TO_PHASE2_HANDOFF.md`
   - Detailed action breakdown
   - Ownership matrix

4. **Evidence Index:** `evidence/phase1/PHASE1_EVIDENCE_INDEX.md`
   - All Phase 1 artifacts catalogued

---

## Troubleshooting

### Issue: liboqs build fails

**Solution:** Check CMake version (need 3.22+), ensure all dependencies installed

```bash
cmake --version  # Should be 3.22.1+
sudo apt-get install -y build-essential cmake ninja-build libssl-dev
```

### Issue: liboqs-python import fails

**Solution:** Verify LD_LIBRARY_PATH includes `/usr/local/lib`

```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
sudo ldconfig
python3 -c "from oqs import Signature; print('OK')"
```

### Issue: Tests fail with "ModuleNotFoundError"

**Solution:** Ensure virtual environment activated and QFS src in path

```bash
source ~/qfs_venv/bin/activate
export PYTHONPATH=$PYTHONPATH:~/qfs-v13.5/src
```

---

## Timeline

| Action | Duration | Cumulative |
|--------|----------|------------|
| 1. Provision Linux | 30 min | 0:30 |
| 2. Install liboqs | 15 min | 0:45 |
| 3. Verify backend | 5 min | 0:50 |
| 4. Production tests | 2 hours | 2:50 |
| 5. Evidence & update | 1 hour | 3:50 |

**Total:** ~4 hours

---

## Quick Commands

```bash
# Full deployment in one go
git clone <QFS_REPO> ~/qfs-v13.5
cd ~/qfs-v13.5
bash scripts/install_liboqs.sh
source ~/qfs_venv/bin/activate
pip install liboqs-python==0.10.0
python3 scripts/verify_dilithium5.py
PYTHONHASHSEED=0 TZ=UTC pytest tests/security/test_pqc_integration_real.py -v
```

---

**Document Status:** 📋 QUICK START GUIDE READY  
**Next Action:** Provision Ubuntu 22.04 LTS and begin Action 1  
**Expected Outcome:** Phase 1 advancement from 80% → 100%
