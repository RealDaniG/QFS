# QFS V13.5 Phase 2 - Linux PQC Deployment Execution Checklist

**Date:** 2025-12-11  
**Phase 1 Status:** ✅ CLOSED AT 80% COMPLETION  
**Phase 2 Objective:** Deploy production PQC backend → 100% Phase 1 completion  
**Estimated Duration:** 4 hours

---

## Pre-Execution Verification

**Before starting Phase 2, verify Phase 1 closure:**

- [ ] All Phase 1 tests passing (15/15)
  ```powershell
  cd "d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"
  $env:PYTHONHASHSEED="0"; $env:TZ="UTC"
  python -m pytest tests/security/test_pqc_integration_mock.py tests/handlers/test_cir302_handler.py -v --tb=line -q
  ```
  **Expected:** `15 passed in ~6s`

- [ ] All Phase 1 closure documents exist with correct SHA-256 hashes
  ```powershell
  # Run bulk verification script
  # See: evidence/phase1/VERIFY_PHASE1_CLOSURE_HASHES.md
  ```

- [ ] Phase 1 Evidence Index reviewed
  - File: `evidence/phase1/PHASE1_EVIDENCE_INDEX.md`
  - 17 artifacts catalogued

---

## Phase 2 Execution: 5 Concrete Actions

### ✅ Action 1: Provision Linux Environment (30 min)

**Status:** [ ] NOT STARTED | [ ] IN PROGRESS | [ ] COMPLETE

**Tasks:**
- [ ] Choose deployment method (Multipass VM / Docker / GitHub Actions)
- [ ] Provision Ubuntu 22.04 LTS with 4+ CPUs, 8GB+ RAM
- [ ] Verify network access to GitHub & PyPI
- [ ] Clone QFS V13.5 repository to Linux environment

**Commands:**
```bash
# Option A: Multipass VM (recommended)
multipass launch 22.04 --name qfs-pqc-build --cpus 4 --mem 8G --disk 40G
multipass shell qfs-pqc-build

# Clone repository
git clone <QFS_V13_REPO> ~/qfs-v13.5
cd ~/qfs-v13.5
```

**Evidence Artifact:**
- [ ] `pqc_linux_environment_setup.log` created
- [ ] SHA-256 hash computed

**Success Criteria:**
- [ ] Ubuntu 22.04 LTS running
- [ ] QFS V13.5 repository cloned
- [ ] Environment info logged (OS version, CPU, RAM)

---

### ✅ Action 2: Install liboqs C Library (15 min)

**Status:** [ ] NOT STARTED | [ ] IN PROGRESS | [ ] COMPLETE

**Tasks:**
- [ ] Install system prerequisites (gcc, g++, cmake, ninja)
- [ ] Clone liboqs repository (version 0.10.1)
- [ ] Build liboqs with CMake
- [ ] Install to /usr/local
- [ ] Verify shared library available

**Commands:**
```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y build-essential cmake git ninja-build libssl-dev python3-dev python3-pip python3-venv

# Build liboqs (see PQC_DEPLOYMENT_PLAN_LINUX.md for full script)
git clone --branch 0.10.1 --depth 1 https://github.com/open-quantum-safe/liboqs.git ~/liboqs-build
cd ~/liboqs-build
mkdir -p build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_BUILD_TYPE=Release -DOQS_BUILD_ONLY_LIB=ON -DOQS_DIST_BUILD=ON -DOQS_USE_OPENSSL=ON ..
ninja
sudo ninja install
sudo ldconfig

# Verify
ldconfig -p | grep liboqs
```

**Evidence Artifacts:**
- [ ] `pqc_linux_deployment_log.txt` created (full build output)
- [ ] `liboqs_version_info.json` created (version + commit hash)
- [ ] SHA-256 hashes computed

**Success Criteria:**
- [ ] liboqs C library installed to /usr/local/lib
- [ ] `ldconfig -p | grep liboqs` shows library
- [ ] No compilation errors

---

### ✅ Action 3: Install liboqs-python & Verify Backend (5 min)

**Status:** [ ] NOT STARTED | [ ] IN PROGRESS | [ ] COMPLETE

**Tasks:**
- [ ] Create Python virtual environment
- [ ] Install liboqs-python 0.10.0
- [ ] Verify Dilithium-5 available
- [ ] Run quick sign/verify test

**Commands:**
```bash
# Create virtual environment
python3 -m venv ~/qfs_venv
source ~/qfs_venv/bin/activate

# Install liboqs-python
pip install liboqs-python==0.10.0

# Verify backend
python3 scripts/verify_dilithium5.py
```

**Script to Create:** `scripts/verify_dilithium5.py`
```python
#!/usr/bin/env python3
import sys
import hashlib
from oqs import Signature

sig = Signature("Dilithium5")
print(f"✅ Algorithm: {sig.details['name']}")
print(f"✅ Public key size: {sig.details['length_public_key']} bytes")
print(f"✅ Signature size: {sig.details['length_signature']} bytes")

# Quick sign/verify test
public_key = sig.generate_keypair()
message = b"QFS V13.5 PQC Production Test"
signature = sig.sign(message)
is_valid = sig.verify(message, signature, public_key)

print(f"✅ Signature verification: {'PASS' if is_valid else 'FAIL'}")
sys.exit(0 if is_valid else 1)
```

**Evidence Artifacts:**
- [ ] `pqc_backend_verification.json` created
- [ ] `dilithium5_quick_test.log` created
- [ ] SHA-256 hashes computed

**Success Criteria:**
- [ ] liboqs-python imports successfully
- [ ] Dilithium5 signature creation works
- [ ] Signature verification passes
- [ ] No runtime errors

---

### ✅ Action 4: Create Production PQC Tests (2 hours)

**Status:** [ ] NOT STARTED | [ ] IN PROGRESS | [ ] COMPLETE

**Tasks:**
- [ ] Create `tests/security/test_pqc_integration_real.py`
- [ ] Implement 5 test scenarios:
  1. Real backend detection
  2. Sign/verify workflow
  3. Performance benchmarks
  4. Memory zeroization
  5. Negative tests (invalid inputs)
- [ ] Run production PQC tests
- [ ] Verify 100% pass rate

**Test File Template:**
```python
"""
Production PQC Integration Tests - Real Dilithium-5 Backend
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from libs.PQC import PQC
from libs.BigNum128 import BigNum128

class TestPQCIntegrationReal:
    def test_real_backend_detection(self):
        """Verify real PQC backend is active"""
        backend_info = PQC.get_backend_info()
        assert backend_info["backend"] in ["liboqs", "pqcrystals"]
        assert backend_info["production_ready"] is True
    
    def test_real_sign_verify_workflow(self):
        """Test sign/verify with real Dilithium-5"""
        # ... (implement sign/verify test)
    
    def test_real_performance_benchmark(self):
        """Measure real PQC performance"""
        # ... (implement benchmark test)
    
    # ... (3 more tests)
```

**Run Command:**
```bash
PYTHONHASHSEED=0 TZ=UTC python -m pytest tests/security/test_pqc_integration_real.py -v --tb=short -o junit_family=xunit2 --junitxml=evidence/phase2/pqc_production_test_results.xml
```

**Evidence Artifacts:**
- [ ] `tests/security/test_pqc_integration_real.py` created
- [ ] `pqc_production_test_results.json` created
- [ ] `pqc_production_test_results.xml` created (JUnit format)
- [ ] SHA-256 hashes computed

**Success Criteria:**
- [ ] All production PQC tests passing (100%)
- [ ] Performance within acceptable ranges:
  - [ ] Keygen < 5ms
  - [ ] Sign < 1ms
  - [ ] Verify < 0.5ms
- [ ] No zero-simulation violations

---

### ✅ Action 5: Generate Evidence & Update Status (1 hour)

**Status:** [ ] NOT STARTED | [ ] IN PROGRESS | [ ] COMPLETE

**Tasks:**
- [ ] Generate performance benchmark report
- [ ] Create PQC Linux deployment evidence document
- [ ] Compute all Phase 2 evidence hashes
- [ ] Update ROADMAP-V13.5-REMEDIATION.md
- [ ] Update Phase 1 status to 100%

**Commands:**
```bash
# Generate performance benchmark
python scripts/benchmark_pqc_performance.py > evidence/phase2/pqc_performance_benchmark.json

# Compute evidence hashes
cd evidence/phase2
sha256sum *.json *.xml *.log > evidence_hashes_phase2.txt
```

**Evidence Artifacts to Create:**
- [ ] `pqc_performance_benchmark.json`
- [ ] `PQC_LINUX_DEPLOYMENT_EVIDENCE.md` (narrative report)
- [ ] `evidence_hashes_phase2.txt` (master hash list)

**Roadmap Updates:**
```diff
# In ROADMAP-V13.5-REMEDIATION.md
- PQC: 🟡 PARTIALLY_IMPLEMENTED (mock only, platform-blocked)
+ PQC: ✅ IMPLEMENTED (liboqs-python on Linux, all tests passing)

- Phase 1: 80% (4/5 CRITICAL)
+ Phase 1: 100% (5/5 CRITICAL)
```

**Success Criteria:**
- [ ] All evidence artifacts generated
- [ ] All SHA-256 hashes computed and documented
- [ ] Phase 1 status updated to 100% in roadmap
- [ ] PQC status changed to IMPLEMENTED
- [ ] Deployment narrative complete

---

## Post-Execution Verification

**After completing all 5 actions:**

- [ ] Run full Phase 1 test suite (PQC mock + real + CIR-302)
  ```bash
  PYTHONHASHSEED=0 TZ=UTC python -m pytest \
    tests/security/test_pqc_integration_mock.py \
    tests/security/test_pqc_integration_real.py \
    tests/handlers/test_cir302_handler.py \
    -v --tb=short
  ```
  **Expected:** All tests passing (100%)

- [ ] Verify Phase 2 evidence artifacts exist
  - [ ] pqc_linux_environment_setup.log
  - [ ] pqc_linux_deployment_log.txt
  - [ ] liboqs_version_info.json
  - [ ] pqc_backend_verification.json
  - [ ] dilithium5_quick_test.log
  - [ ] pqc_production_test_results.json
  - [ ] pqc_production_test_results.xml
  - [ ] pqc_performance_benchmark.json
  - [ ] PQC_LINUX_DEPLOYMENT_EVIDENCE.md
  - [ ] evidence_hashes_phase2.txt

- [ ] Verify all SHA-256 hashes computed
  ```bash
  cat evidence/phase2/evidence_hashes_phase2.txt
  ```

- [ ] Update compliance status
  - [ ] CRIT-1.6: Production PQC signatures → SATISFIED
  - [ ] CRIT-1.7: Production PQC verification → SATISFIED
  - [ ] CRIT-1.8: Production key generation → SATISFIED
  - [ ] Overall compliance: 10/10 requirements SATISFIED (100%)

---

## Timeline Tracker

| Action | Estimated | Actual | Status |
|--------|-----------|--------|--------|
| 1. Provision Linux | 30 min | ___ min | [ ] |
| 2. Install liboqs | 15 min | ___ min | [ ] |
| 3. Verify backend | 5 min | ___ min | [ ] |
| 4. Production tests | 2 hours | ___ hours | [ ] |
| 5. Evidence & update | 1 hour | ___ hours | [ ] |
| **Total** | **~4 hours** | **___** | [ ] |

---

## Troubleshooting Reference

**If liboqs build fails:**
- Check CMake version: `cmake --version` (need 3.22.1+)
- Ensure all dependencies: `sudo apt-get install -y build-essential cmake ninja-build libssl-dev`

**If liboqs-python import fails:**
- Set LD_LIBRARY_PATH: `export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH`
- Run ldconfig: `sudo ldconfig`

**If tests fail with ModuleNotFoundError:**
- Activate venv: `source ~/qfs_venv/bin/activate`
- Set PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:~/qfs-v13.5/src`

**Reference:** See [PQC_DEPLOYMENT_PLAN_LINUX.md](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/docs/deployment/PQC_DEPLOYMENT_PLAN_LINUX.md) Section "Risks & Constraints"

---

## Success Definition

**Phase 2 is successful when:**

✅ All 5 actions completed  
✅ All checkboxes marked  
✅ Production PQC tests passing (100%)  
✅ Performance benchmarks within targets  
✅ All evidence artifacts generated with SHA-256 hashes  
✅ Phase 1 status updated to 100%  
✅ Compliance requirements: 10/10 SATISFIED

---

## Next Steps After Phase 2

**Once Phase 2 completes:**

1. Run Audit v2.0 to verify 100% Phase 1 completion
2. Generate final Phase 1 completion certificate
3. Plan Phase 3: Integration testing (HSMF + PQC + CIR-302)
4. Consider external PQC security audit

---

**Document Status:** ✅ EXECUTION CHECKLIST READY  
**Usage:** Track progress by checking boxes during Phase 2 execution  
**Reference Docs:**
- [PQC_DEPLOYMENT_PLAN_LINUX.md](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/docs/deployment/PQC_DEPLOYMENT_PLAN_LINUX.md)
- [PHASE2_QUICK_START.md](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/PHASE2_QUICK_START.md)
- [QFS_V13.5_PHASE1_TO_PHASE2_HANDOFF.md](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/evidence/phase1/QFS_V13.5_PHASE1_TO_PHASE2_HANDOFF.md)

**SHA-256 Hash (this file):** _(to be computed upon finalization)_
