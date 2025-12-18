# AEGIS Guard Specification (Zero-Simulation)

## Overview

AEGIS (Automated Enforcement & Governance Integrity System) provides safety and compliance guards for the ATLAS network. In the Zero-Simulation architecture, the authoritative enforcement of these guards moves from the client-side to the QFS Backend.

## Architecture

### 1. Client-Side (Pre-Flight)

- **Role:** User feedback and basic format validation.
- **Component:** `GuardService` (Frontend).
- **Behavior:**
  - Checks message formatting (max length, allowed chars).
  - Checks required fields.
  - **Note:** Client-side checks are *non-binding*. A "pass" here does not guarantee ledger acceptance.

### 2. Backend (Enforcement)

- **Role:** Authoritative validation and state transition.
- **Component:** QFS Policy Engine (Python).
- **Behavior:**
  - **Safety Guard:** Scans content for prohibitted items (PII, hate speech, etc.) using QFS classifiers.
  - **Privacy Guard:** Enforces DID-based access controls and encryption requirements.
  - **Quality Guard:** Evaluates Coherence thresholds for rewards (via `CoherenceEngine`).

## Zero-Simulation Policy

All critical guard logic executes on the QFS Backend. The client MUST NOT simulate these checks for the purpose of "predicting" the outcome securely. The only source of truth is the signed acknowledgment from the Ledger.

## Integration

- **Submission:** `QFSClient.submit(event)`
- **Validation:** QFS Backend runs `policy_registry.check(event)`
- **Rejection:** If a guard fails, the backend returns the specific error code (e.g., `ERR_SAFETY_VIOLATION`) which the client displays to the user.
