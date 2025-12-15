# Explainability & Audit Framework

> **"If you can't explain it via replay, you can't show it."**

## 🌐 Overview

The QFS Explanation Audit Framework ensures that every algorithmic outcome—whether a content ranking, a reward payout, or a visibility filter—is:

1. **Transparent:** Users can see exactly *why* a decision was made.
2. **Verifiable:** Auditors can cryptographically prove the decision followed the rules.
3. **Immutable:** Decisions are anchored to the PQC-signed ledger and cannot be retroactively altered.

## 🏗️ Architecture

The system uses an **Event Sourcing** pattern. We do not store "audit logs" in a database. Instead, we store:

* **The Rules:** Versioned Policy configurations (e.g., Humor Policy v1.2).
* **The Inputs:** Immutable content hashes and context signals.
* **The Result:** The signed decision event.

To "audit" a decision, the **StorageEngine** replays the `(Input + Policy)` through the deterministic logic to verify the `Result`.

## 🔌 API Reference

### Retrieve Explanation

`GET /api/v1/audit/explanation/{event_id}`
Returns a detailed breakdown of the decision logic, including:

* **Base Score/Value**
* **Applied Multipliers** (e.g., "Humor Bonus: +10%")
* **Policy Context** (which rules were active)
* **Zero-Sim Proof** (Input/Output and Logic hashes)

### Verify Integrity

`POST /api/v1/audit/verify`
Client-side or third-party verification that re-runs the hashing function to detect tampering.

## 📊 UI Components

The **ExplanationAuditPanel** in ATLAS visualizes this data as a "Waterfall Chart," showing how a value started (Base) and flowed through various gates (Bonuses/Caps) to reach the final state.
