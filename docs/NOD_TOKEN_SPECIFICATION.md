# NOD Token Specification

**Name**: Node Operator (NOD)
**Purpose**: Exclusive governance and infrastructure staking for network operators. NOD enables participation in consensus, validation, and constitutional enforcement without influencing user-facing economics.
**Key Principle**: NOD is **strictly firewalled** from user parameters—preventing capture or speculation while securing the decentralized backbone.
**Transferability**: **Non-transferable** (❌ No). NOD cannot be traded, sold, or moved between wallets. It is soul-bound to operator identities.

---

## 1. Role in the 6-Token Harmonic Economy

The system uses closed-loop, bounded incentives:

| Token | Purpose                  | Transferable | User-Facing | Governance/Infrastructure |
|-------|--------------------------|--------------|-------------|----------------------------|
| FLX   | Flexibility (rewards/penalties) | ✅ Yes      | Yes        | No                        |
| CHR   | Coherence (stability/quality)   | ✅ Yes      | Yes        | No                        |
| PSI   | Psi-Sync (alignment/prediction) | ✅ Yes      | Yes        | No                        |
| ATR   | Attestation (reputation)        | ✅ Yes      | Yes        | No                        |
| RES   | Reserve (buffer/stability)      | ✅ Yes      | Yes        | Partial                   |
| **NOD** | **Node Operator (governance)** | ❌ No       | No         | **Yes**                   |

NOD complements the user tokens by securing the network layer—ensuring determinism, PQC validation, and AEGIS consensus without risking inequality or extraction.

---

## 2. Acquisition and Distribution

- **Initial Distribution**: Determined via constitutional genesis process (e.g., proof-of-coherence or attested contributions during Phase V/VI). No pre-mine or ICO—aligned with non-speculative design.
- **Ongoing Minting**: Limited minting through validated operator onboarding (e.g., staking RES + attestation). Burn on slash/offline.
- **Slashing/Penalties**: NOD slashed for non-determinism, downtime, or guard violations (e.g., proposing invalid state). Slashing emits explainable events.
- **No Yield Farming**: No passive yields—rewards tied to active validation duties.

---

## 3. Governance Functions

NOD holders participate in infrastructure-level decisions:

- **Proposal Submission/Voting**: Weighted by NOD stake; proposals for upgrades, parameter tweaks (e.g., TPS thresholds), or HSM integrations.
- **AEGIS Consensus**: Operators run nodes with NOD stake for PBFT/RΦV validation.
- **Constitutional Vetoes**: High-threshold NOD votes can veto user-facing changes that risk determinism.
- **Firewalled Scope**: NOD cannot influence user rewards, content scoring, or token mints—enforced by guards (EconomicsGuard, NODInvariantChecker).

---

## 4. Technical Implementation

- **Storage**: Non-transferable flag in ledger; soul-bound via wallet attestation.
- **Operations**: Stake/unstake via operator endpoints; voting via signed proposals (PQC).
- **Zero-Sim Compliance**: All NOD operations replayable (tick-based staking, deterministic slashing formulas).
- **Integration**: Wired in `v13/services/governance/` and AEGIS nodes.

---

## 5. Risks and Mitigations

- **Centralization Risk** — Mitigated by high onboarding barriers (attestation + stake) and slashing.
- **Inactivity** — Auto-slash for offline nodes.
- **Capture** — Non-transferable + firewalled scope prevents markets.

---

*Canonical Specification - Last updated: December 18, 2025*
