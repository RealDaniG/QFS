# Zero-Simulation Violations Fix Plan

## Overview
Several modules have Zero-Simulation violations that need to be addressed to make them compliant with QFS V13 requirements. The violations primarily involve:
1. Use of non-deterministic imports (`time`)
2. Use of non-deterministic functions (`time.time()`)
3. Use of global variables that could introduce non-determinism

## Modules to Fix

### 1. PQC.py
**Violations:**
- Import of `time` module
- Use of `time.time()` in logging functions
- Use of global variables for configuration

**Fix Plan:**
- Remove `time` import
- Replace `time.time()` with deterministic timestamp parameter
- Convert global configuration to instance-based configuration
- Add timestamp parameter to all logging functions

### 2. CIR302_Handler.py
**Violations:**
- Import of `time` module
- Use of `time.time()` in multiple functions
- Use of global variables for configuration

**Fix Plan:**
- Remove `time` import
- Replace `time.time()` with deterministic timestamp parameter
- Add timestamp parameter to constructor or methods
- Make quantum metadata timestamp configurable

### 3. CertifiedMath.py
**Violations:**
- Use of global variables for configuration (`_CONFIG_SERIES_TERMS`, `_CONFIG_PHI_INTENSITY_B_STR`, `_CONFIG_EXP_LIMIT_STR`)

**Fix Plan:**
- Convert global configuration to instance-based configuration
- Add configuration parameters to CertifiedMath constructor
- Remove global variables and use instance variables instead

## Implementation Approach
1. Fix PQC.py first as it's used by other modules
2. Fix CIR302_Handler.py next
3. Fix CertifiedMath.py last
4. Update all dependent modules to pass timestamps explicitly
5. Verify all fixes with the audit script