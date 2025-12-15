# NOD Infrastructure Token Specification (V1.0)

## 1. Overview

The **Node Operator Determination (NOD)** token is the governance and infrastructure scaling token of the QFS ecosystem. Unlike FLX (Access) or CHR (Coherence), NOD represents **infrastructure ownership** and **operational capacity**.

## 2. Token Utility

* **Infrastructure Proofs**: Required to operate storage nodes and participate in the AEGIS verification capability.
* **Governance Weight**: Provides voting power for protocol upgrades in the AEGIS Governance module.
* **Staking for Reliability**: Operators stake NOD to prove commitment; uptime failures result in slashing (via `CIR-302`).

## 3. Economic Model (Draft)

* **Supply**: Fixed periodic emission based on network storage capacity growth.
* **Distribution**:
  * 40% Node Operators (based on verifiable uptime & storage)
  * 30% Treasury Reserve (for crisis stabilization)
  * 30% Developer/Founder pool (vested)

## 4. Integration with Zero-Sim

NOD balances are tracked in the `TokenStateBundle` (`nod_state`) and are subject to Zero-Simulation verification. Any mutation of NOD supply outside of the `hsmf_metrics` calculation triggers a `CIR-302` halt.

## 5. AEGIS Verification

Only nodes with a valid PQC identity (Dilithium-5) and a minimum NOD stake can pass the `AEGISNodeVerification` check.
