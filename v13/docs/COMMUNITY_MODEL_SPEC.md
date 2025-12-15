# QFS × ATLAS: Community Model & Tools Specification

**Version:** 1.0
**Status:** DRAFT
**Scope:** P0 (Gap Analysis)

## 1. Purpose & Scope

The Community Model defines how users organize into **Guilds** (or Communities) within ATLAS.
It provides the structure for:

- Collective Reputation (Guild Coherence)
- Resource Pooling (Treasury/Staking)
- Governance (Policy Delegates)
- Content Curation (Topic Channels)

**Core Philosophy:** Communities are **not** just chat rooms. They are **economic and reputation units** on the QFS Ledger.

## 2. Functional Requirements

### 2.1 Guild Structure

- **Guild ID**: Unique DID (e.g., `did:atlas:guild:xyz`).
- **Manifest**: On-chain metadata defining purpose, rules, and staking requirements.
- **Roles**:
  - **Founder**: Initial creator (can be rotated).
  - **Council**: Elected or appointed admins (Multi-sig control).
  - **Member**: Standard participant (Staked/Unstaked).
  - **Observer**: Read-only.

### 2.2 Reputation & Coherence

- **Guild Coherence Score**: Weighted average of top N members' coherence + Guild interactions history.
- **Impact**: Higher coherence guilds get priority in global feeds and lower fees for governance proposals.

### 2.3 Governance & Treasury

- **Treasury Wallet**: A multi-sig wallet controlled by the Council/Founder.
- **Dues/Fees**: Communities can set entry fees or monthly dues (handled via QFS smart policies).
- **Proposals**: Local governance for upgrading the Guild Manifest or spending treasury funds.

### 2.4 Content Channels

- **Feed**: A coherent feed specific to the Guild.
- **Chat**: Direct Messaging group context (off-ledger storage, on-ledger gating).

## 3. Data Models

### 3.1 Guild Manifest (On-Ledger / Pinned Storage)

```json
{
  "id": "did:atlas:guild:...",
  "name": "Quantum Researchers",
  "description": "Explorers of QFS mechanics.",
  "coherence_threshold": 400,
  "staking_requirement": { "token": "QFS", "amount": 100 },
  "treasury_address": "0x...",
  "created_at": "iso8601",
  "version": 1
}
```

### 3.2 Membership Record (Ledger Event)

```json
{
  "event_type": "GUILD_JOIN",
  "user_id": "0xUser...",
  "guild_id": "did:atlas:guild:...",
  "stake_locked": 100,
  "role": "MEMBER"
}
```

## 4. Implementation Plan

- [ ] **Phase 1**: Guild Registry & Manifest definition (Ledger).
- [ ] **Phase 2**: Membership & Staking logic (Policy Engine).
- [ ] **Phase 3**: Treasury integration (Economics).
- [ ] **Phase 4**: UI/Feed integration.
