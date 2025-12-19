# State of the Union — QFS × ATLAS v15.5

> **Date:** December 19, 2025  
> **Version:** v15.5 (Planning Phase)  
> **Focus:** Admin/Moderator Panel — PoE-Backed Deterministic Moderation

---

## Executive Summary

QFS × ATLAS v15.5 introduces a **fully deterministic, PoE-backed Admin/Moderator Panel** that transforms content moderation from discretionary human judgment into a **verifiable governance instrument**.

Every moderation decision:

- Flows from **versioned, auditable rulesets**
- Is computed by a **deterministic function** `F(content, scores, rules, role)`
- Requires **wallet authentication** with RBAC scopes
- Is **hash-chained and PoE-anchored** in the governance ledger
- Can be **independently replayed and verified** by any auditor

This represents a fundamental shift: moderation is no longer a "black box" but a **transparent, replayable governance process** with the same rigor as treasury allocations or parameter changes.

---

## Current Status

### ✅ Foundation Complete (v15.3 - v15.4)

- **v15.3**: PoE integration, governance verification, structural verifiability
- **v15.4**: Wallet authentication (NonceManager, WalletAuth, SessionManager)
- **v15.4**: Frontend integration (useWalletAuth hook, WalletConnectButton)
- **v15.4**: Protected API routes with scope enforcement

### 🔄 v15.5 Planning Phase (Current)

- **Implementation Plan**: Comprehensive 3-phase rollout defined
- **Data Models**: Decision records, hash-chained logs, PoE schema designed
- **Deterministic Engine**: `F(inputs)` specification complete
- **RBAC Extension**: Moderator/admin/auditor scopes defined

### 📅 v15.5 Timeline

- **Q1 2026**: Phase 1 (Backend foundations)
- **Q2 2026**: Phase 2 (Panel APIs)
- **Q3 2026**: Phase 3 (Frontend panel)
- **Q4 2026**: Production rollout + agent integration

---

## Architectural Decisions

### 1. Deterministic Decision Engine

**Problem**: Traditional moderation relies on human judgment, leading to inconsistency and lack of auditability.

**Solution**: Pure function `F(content_features, scores, rules, moderator_role)` that:

- Takes only deterministic inputs (no timestamps, no random numbers)
- Applies versioned rules in priority order
- Returns same recommendation for same inputs (100% reproducible)
- Logs every computation step for replay

**Benefits**:

- **Consistency**: Same content + rules = same decision across all moderators
- **Auditability**: Decisions can be replayed and verified independently
- **Transparency**: Users see exact rule, threshold, and score that triggered action

### 2. PoE-Anchored Audit Trail

**Problem**: Traditional moderation logs are mutable databases that can be altered or deleted.

**Solution**: Hash-chained decision log anchored in governance ledger:

- Each decision is serialized to canonical JSON
- Decision hash is chained with previous hash (like blockchain)
- PoE hash is PQC-signed and written to `CoherenceLedger`
- Auditors can verify chain integrity and signature validity

**Benefits**:

- **Tamper-Evident**: Any alteration breaks hash chain
- **Independently Verifiable**: No trust in moderators or database required
- **Governance Integration**: Moderation decisions have same auditability as treasury allocations

### 3. Wallet-Based RBAC

**Problem**: Username/password authentication is vulnerable to credential theft and lacks non-repudiation.

**Solution**: EIP-191 wallet signatures + session scopes:

- Moderators sign nonce with wallet → session token with `mod:read`, `mod:act`
- Admins get additional `admin:override` scope
- Auditors get `audit:read` (view-only)
- Critical actions (ban, override) require 2FA with hardware key

**Benefits**:

- **Non-Custodial**: No passwords to steal or leak
- **Non-Repudiation**: Every action cryptographically tied to wallet
- **Hardware Security**: 2FA with YubiKey/Ledger for critical actions

### 4. Agent-Ready Architecture

**Problem**: AI moderation tools (SuperAGI, LangGraph) produce non-deterministic outputs.

**Solution**: Agent suggestions normalized through deterministic adapter:

- Agent produces raw scores + confidence
- Adapter maps to rule score types (safety_score, spam_score)
- Scores feed same deterministic function `F`
- Human moderator confirms final action

**Benefits**:

- **AI-Assisted**: Leverage agent insights without sacrificing determinism
- **Governance Preserved**: Agents never bypass PoE anchoring or rules
- **Incremental Adoption**: Can test agents in simulation mode first

---

## What's New in v15.5

Compared to previous versions:

| Feature | v15.4 & Earlier | v15.5 |
|---------|-----------------|-------|
| **Moderation Logging** | Database records | PoE-anchored hash chain |
| **Decision Process** | Human discretion | Deterministic function `F` |
| **Authentication** | Username/password | Wallet + 2FA |
| **Auditability** | Internal logs | Public PoE verification |
| **AI Integration** | None | Agent-ready adapter |
| **Simulation Mode** | None | Test rules without enforcement |

---

## Strategic Direction

### Governance as Code

v15.5 extends the "governance as code" principle to **content moderation**:

- **Rules are versioned config** (YAML), not tribal knowledge
- **Decisions are PoE entries**, not database rows
- **Moderators are governance executors**, not discretionary judges
- **Auditors can replay decisions**, not just read logs

### Agent Layer Evolution

> **Canonical Doctrine:** [Timeless Agent Integration & Evolution Plan](./AGENT_INTEGRATION_EVOLUTION.md)

v15.5 establishes the **Advisory-Only** pattern for all AI integrations:

- **Principle**: Agents are replaceable advisors, not foundations.
- **Protocol**: Agents emit `agent_advisory` events to the EvidenceBus.
- **Authority**: QFS deterministic logic (`F`) consumes signals but retains Full Authority.
- **Legacy**: Open-AGI is designated as "Legacy / Experimental".

**Migration Path**:

1. **Stabilize Core**: Wallet/GitHub flows and Governance UI take priority.
2. **Framework Agnostic**: Future integrations (CrewAI, LangGraph) will plug into the same read-only/advisory interface.
3. **Cost Control**: Sampling rates (e.g., 10-20%) limit OPEX exposure.

### Compliance & Transparency

PoE-backed moderation enables:

- **Public Audit Dashboard**: Anyone can verify decision integrity
- **Regulatory Compliance**: Tamper-evident logs for GDPR, DMCA, etc.
- **User Appeals**: Users can challenge decisions with PoE evidence
- **Governance Disputes**: NOD holders can propose rule changes via standard governance flow

---

## Conclusion

v15.5 represents a **paradigm shift** in content moderation:

- From **discretionary judgment** to **deterministic rules**
- From **mutable logs** to **PoE-anchored audit trails**
- From **password auth** to **wallet + 2FA**
- From **black box** to **transparent, replayable governance**

This aligns moderation with QFS's core principles: **determinism, verifiability, and sovereignty**. Every decision is a governance act, every moderator is a governance executor, and every audit is independently verifiable.

**QFS × ATLAS v15.5**: Moderation is governance. Governance is PoE. Trust, but verify. 🔐
