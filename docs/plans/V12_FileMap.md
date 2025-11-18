# QFS V12 File Structure Documentation

This document provides a high-level overview of the QFS V12 directory structure.

## Root Directory
- QFS/
  - V12/
    - Core Python files (.py)
    - Contract files (.sol)
    - Documentation files (.md)
    - Test files
    - Script files
    - Configuration files
    - Package files
    - Service directories

## Key Components
- CertifiedMath implementations
- Core token contracts (FLX.sol, ATR.sol, PSY.sol, RES.sol)
- Utility contracts (Penalty.sol, Staking.sol)
- Core services (ActionCostEngine.py, AtomicCommit.py, CoherenceLedger.py)
- Security components (PQC_Verifier.py)
- Deterministic time services (DRV_ClockService.py)
- Path optimization components (PathOptimizer.py, StateSpaceExplorer.py)
- Utility components (UtilityOracle.py, AuditTrail.py)