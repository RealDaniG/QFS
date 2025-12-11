# CertifiedMath ProofVectors Specification

**Component:** CertifiedMath  
**Version:** V13.5  
**Purpose:** Define canonical test inputs with exact deterministic outputs for all CertifiedMath functions  
**Compliance:** Zero-Simulation, Fully Deterministic  
**Last Updated:** 2025-12-11

---

## Overview

ProofVectors are **canonical test cases** that define:
1. **Exact input values** (deterministic, reproducible)
2. **Expected output values** (computed with reference implementation)
3. **Maximum allowed error bounds** (for fixed-point approximations)

These serve as **ground truth** for validating CertifiedMath implementations across platforms, ensuring bit-for-bit deterministic behavior.

---

## Mathematical Functions Coverage

### 1. Exponential Function: `exp(x)`

**Function Signature:** `exp(x: BigNum128) -> BigNum128`  
**Algorithm:** Taylor series expansion (deterministic)  
**Error Bound:** ±0.000000001 (10^-9)

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 1.0 | exp(0) = 1 |
| 1 | 2.718281828 | exp(1) = e |
| 2 | 7.389056099 | exp(2) = e^2 |
| -1 | 0.367879441 | exp(-1) = 1/e |
| 0.5 | 1.648721271 | exp(0.5) |
| 10 | 22026.465794807 | exp(10) - large value |

---

### 2. Natural Logarithm: `ln(x)`

**Function Signature:** `ln(x: BigNum128) -> BigNum128`  
**Algorithm:** Newton's method (deterministic iterations)  
**Error Bound:** ±0.000000001 (10^-9)

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 1 | 0.0 | ln(1) = 0 |
| 2.718281828 | 1.0 | ln(e) = 1 |
| 2 | 0.693147181 | ln(2) |
| 10 | 2.302585093 | ln(10) |
| 0.5 | -0.693147181 | ln(0.5) = -ln(2) |
| 100 | 4.605170186 | ln(100) |

---

### 3. Sine Function: `sin(x)`

**Function Signature:** `sin(x: BigNum128) -> BigNum128`  
**Algorithm:** Taylor series (angle reduction)  
**Error Bound:** ±0.000000001 (10^-9)  
**Note:** Input x in radians

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 0.0 | sin(0) = 0 |
| 1.570796327 | 1.0 | sin(π/2) = 1 |
| 3.141592654 | 0.0 | sin(π) = 0 |
| 0.523598776 | 0.5 | sin(π/6) = 0.5 |
| 1.0 | 0.841470985 | sin(1) |
| -1.570796327 | -1.0 | sin(-π/2) = -1 |

---

### 4. Cosine Function: `cos(x)`

**Function Signature:** `cos(x: BigNum128) -> BigNum128`  
**Algorithm:** Taylor series (angle reduction)  
**Error Bound:** ±0.000000001 (10^-9)  
**Note:** Input x in radians

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 1.0 | cos(0) = 1 |
| 1.570796327 | 0.0 | cos(π/2) = 0 |
| 3.141592654 | -1.0 | cos(π) = -1 |
| 1.047197551 | 0.5 | cos(π/3) = 0.5 |
| 1.0 | 0.540302306 | cos(1) |
| -1.570796327 | 0.0 | cos(-π/2) = 0 |

---

### 5. Hyperbolic Tangent: `tanh(x)`

**Function Signature:** `tanh(x: BigNum128) -> BigNum128`  
**Algorithm:** (exp(2x) - 1) / (exp(2x) + 1)  
**Error Bound:** ±0.000000001 (10^-9)

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 0.0 | tanh(0) = 0 |
| 1 | 0.761594156 | tanh(1) |
| 2 | 0.964027580 | tanh(2) |
| -1 | -0.761594156 | tanh(-1) |
| 0.5 | 0.462117157 | tanh(0.5) |
| 10 | 0.999999996 | tanh(10) → 1 |

---

### 6. Sigmoid Function: `sigmoid(x)`

**Function Signature:** `sigmoid(x: BigNum128) -> BigNum128`  
**Algorithm:** 1 / (1 + exp(-x))  
**Error Bound:** ±0.000000001 (10^-9)

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 0.5 | sigmoid(0) = 0.5 |
| 1 | 0.731058579 | sigmoid(1) |
| 2 | 0.880797078 | sigmoid(2) |
| -1 | 0.268941421 | sigmoid(-1) |
| -2 | 0.119202922 | sigmoid(-2) |
| 10 | 0.999954602 | sigmoid(10) → 1 |

---

### 7. Error Function: `erf(x)`

**Function Signature:** `erf(x: BigNum128) -> BigNum128`  
**Algorithm:** Taylor series approximation  
**Error Bound:** ±0.000001 (10^-6)

#### ProofVectors

| Input (x) | Expected Output | Description |
|-----------|----------------|-------------|
| 0 | 0.0 | erf(0) = 0 |
| 1 | 0.842700793 | erf(1) |
| 2 | 0.995322265 | erf(2) |
| 0.5 | 0.520499878 | erf(0.5) |
| -1 | -0.842700793 | erf(-1) |
| 3 | 0.999977910 | erf(3) → 1 |

---

## Implementation Requirements

### 1. ProofVector Test Structure

```python
def test_exp_proofvector_0():
    """ProofVector: exp(0) = 1.0"""
    input_val = BigNum128("0")
    expected = BigNum128("1.0")
    result = CertifiedMath.exp(input_val)
    assert abs(result - expected) <= EPSILON

def test_exp_proofvector_1():
    """ProofVector: exp(1) = e"""
    input_val = BigNum128("1")
    expected = BigNum128("2.718281828")
    result = CertifiedMath.exp(input_val)
    assert abs(result - expected) <= EPSILON
```

### 2. Error Bound Constants

```python
# Maximum allowed error for each function family
EPSILON_EXPONENTIAL = BigNum128("0.000000001")  # 10^-9 for exp, ln
EPSILON_TRIGONOMETRIC = BigNum128("0.000000001")  # 10^-9 for sin, cos
EPSILON_HYPERBOLIC = BigNum128("0.000000001")  # 10^-9 for tanh, sigmoid
EPSILON_ERF = BigNum128("0.000001")  # 10^-6 for erf (larger tolerance)
```

### 3. Determinism Validation

All ProofVectors **MUST**:
- ✅ Use fixed input values (no random generation)
- ✅ Produce identical output across runs (bit-for-bit)
- ✅ Use BigNum128 fixed-point arithmetic (no floating-point)
- ✅ Avoid time-based or platform-specific operations

---

## Compliance Checklist

- [ ] All 7 functions have ProofVector definitions
- [ ] Error bounds documented and enforced in tests
- [ ] Test suite created: `tests/unit/test_certified_math_proofvectors.py`
- [ ] Evidence artifact generated: `evidence/phase1/certified_math_proofvectors.json`
- [ ] Zero-simulation compliance verified (no float, random, time)
- [ ] Cross-platform determinism validated

---

## References

- **CertifiedMath Implementation:** `src/libs/CertifiedMath.py`
- **BigNum128 Specification:** `src/libs/BigNum128.py`
- **AUDIT-V13 Requirements:** Deterministic math engine with audit trail
- **Phase 1.2 Roadmap:** CertifiedMath ProofVectors (Tasks P1-T004 to P1-T008)

---

**Document Status:** ✅ COMPLETE  
**Next Step:** Implement ProofVector test suite in `tests/unit/test_certified_math_proofvectors.py`
