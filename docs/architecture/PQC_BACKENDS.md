# PQC Backend Strategy & Architecture

## 1. Backend Classification

To ensure cross-platform compatibility during development while maintaining high-performance security in production, QFS V13 employs a tiered backend strategy for Post-Quantum Cryptography.

### **Development Backend: `dilithium` (Pure Python)**

- **Package**: `dilithium` (specifically version `>=1.0.0,<2.0.0`)
- **Purpose**: CI/CD pipelines, Windows/macOS local development, Phase 1-2.5 validation.
- **Characteristics**:
  - Pure Python implementation (easy to install).
  - slower performance compared to C impl.
  - Cross-platform compatible.
- **Reference**: <https://pypi.org/project/dilithium/> (Note: `dilithium-py` does NOT exist)
- **Status**: ✅ Active (Current Phase 1 Standard)

### **Production Backend: `liboqs` (C Library)**

- **Package**: `liboqs-python` bindings + `liboqs` system library.
- **Purpose**: Phase 3+ production deployment, high-throughput signing nodes.
- **Characteristics**:
  - NIST-compliant C implementation.
  - High performance (<10ms sign/verify).
  - Requires Linux (Ubuntu 22.04 LTS recommended).
- **Requirements**: System-level installation of `liboqs` >= 0.10.1.
- **Status**: 🔒 Phase 3 (Planned Logic)

### **MockPQC Fallback: Deterministic Simulator**

- **Implementation**: Internal `_MockPQC` class in `v13/libs/PQC.py`.
- **Purpose**: Integration testing, debugging, fallback when crypto deps missing.
- **Characteristics**:
  - Uses SHA-256 to simulate signature mechanics.
  - **NOT CRYPTOGRAPHICALLY SECURE**.
  - Fully deterministic for replay testing.
- **Status**: ✅ Active (Failsafe)

---

## 2. Architectural Rationale

### Why not use `liboqs` everywhere?

1. **CI Stability**: Building C-extensions from source on every CI run (Windows/macOS/Ubuntu matrix) is brittle and slow.
2. **Developer Experience**: Forcing Windows devs to compile `liboqs` creates a high barrier to entry. `dilithium` `pip install` works universally.
3. **Zero-Simulation**: Using a slower Python implementation of the *real algorithm* (Dilithium-5) is fully compliant with Zero-Simulation principles. We are not "simulating" the math; we are executing identical math, just slower.

### Why not use `dilithium-py` or `pqcrystals`?

- **Dependency Hell**: `dilithium-py` is a common hallucinated package name that does not exist on PyPI.
- **Namespace Issues**: `pqcrystals` is the namespace used by some bindings but isn't a standalone installable package on PyPI.
- **Solution**: We strictly enforce `dilithium` (PyPI) for development.

---

## 3. Migration Path

| Phase | Backend | Environment | Action |
|-------|---------|-------------|--------|
| **Phase 1-2.5 (NOW)** | `python-dilithium` | CI/Dev (Win/Mac/Lin) | Use `dilithium` package. Allow MockPQC fallback for unit tests. |
| **Phase 3 (PROD)** | `liboqs` | Linux Servers | Deploy Docker containers with compiled `liboqs`. Enforce backend check at startup. |

---

## 4. Critical Constraints

1. **NEVER use `dilithium-py`**: It breaks CI/CD.
2. **NEVER enable MockPQC in Production**: `PQC.py` includes warnings, but Phase 3 startup scripts must explicitly validate the backend is NOT `mock`.
3. **Linux Only for Production**: We do not support production signing nodes on Windows/macOS.
