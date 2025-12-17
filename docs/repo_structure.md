# QFS Repository Structure

This document outlines the organization of the QFS × ATLAS × AEGIS repository (V13).

## Top-Level Directories

* **`v13/`**: The core runtime codebase. Contains all logic for the Quantum Financial System, ATLAS API, and AEGIS UX.
* **`tests/`**: (Proposed consolidated location) - Currently tests are distributed in `v13/tests` and `tests/`.
* **`docs/`**: Documentation, specifications, and architecture records.
* **`tools/`** / **`v13/tools/`**: Development scripts, audits, and CI helpers.
* **`archive/`**: Deprecated scripts and historical artifacts.

## Core Components (`v13/`)

### QFS (Economics & Ledger)

* **`v13/core/`**: Core node logic.
* **`v13/ledger/`**: Ledger state and transaction processing.
* **`v13/libs/`**: Shared libraries including `PQC` (Post-Quantum Cryptography).

### ATLAS (Network & API)

* **`v13/ATLAS/`**:
  * `src/api/`: REST API endpoints (`secure_chat`, etc.).
  * `src/p2p/`: Network layer (`connection_manager.py`).
  * `src/models/`: Data models.

### AEGIS (UX & Governance)

* **`v13/AEGIS/`**:
  * `governance/`: Proposal and Registry logic.
  * `services/`: Evidence, Explanation, and Sandbox services.
  * `ui_contracts/`: Frontend-Backend schemas.

## Tools and Quality Assurance

* **`v13/tools/audit/`**: Scripts for Verify Zero-Simulation compliance (AST Checkers).
* **`v13/services/evidence/`**: Verification logic for AEGIS.
* **`v13/tests/`**: Unit and Integration tests.

## Archive

The `archive/` folder contains scripts and files that are no longer part of the active development path but are preserved for reference.
