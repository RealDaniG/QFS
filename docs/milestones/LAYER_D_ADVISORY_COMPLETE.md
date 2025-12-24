# Layer D: Agent Advisory (v17.1 Ready)

> **Purpose:** Provide deterministic, non-authoritative signals to help human stewards focus their attention.

## Overview

Layer D acts as a transparent overlay on the QFS Governance and Bounty systems. It consumes state events (like `GOV_PROPOSAL_CREATED`) and emits advisory events (`AGENT_ADVISORY_*`). These signals are displayed in the Admin Dashboard but **never** alter the execution logic of the F-Layer.

## Architecture

### 1. Invariants

- **Advisory Only:** Signals are labeled as "Suggestions" or "Flags".
- **Deterministic:** Same history + Same Code = Same Signals.
- **Stateless Adapters:** Heuristics rely on event payloads (content, metadata).
- **Explicit Timestamps:** Sourced from the cause-event to ensure reliable replay.

### 2. Components

- **`v17/agents/governance_advisory.py`**
  - **Triggers:** Proposal Creation.
  - **Heuristics:** High amount checks (>10k), Low context counts (<50 chars), Risk keywords.
  - **Output:** `AGENT_ADVISORY_PROPOSAL`.

- **`v17/agents/bounty_advisory.py`**
  - **Triggers:** Contribution Submission.
  - **Heuristics:** Reference link verification (http/ipfs), Content length checks.
  - **Output:** `AGENT_ADVISORY_BOUNTY`.

- **`v17/agents/social_advisory.py`**
  - **Triggers:** Dispute Opening.
  - **Heuristics:** Urgency keyword detection ("scam", "fraud").
  - **Output:** `AGENT_ADVISORY_SOCIAL`.

### 3. Future Models

The system is designed to support advanced models (e.g., Local LLMs) via the `DeterministicAdvisoryModel` interface defined in `v17/agents/interfaces.py`. Future implementations must:

1. Wrap stochastic model calls with a deterministic caching layer (Proof-of-inference).
2. Use the standard `AdvisorySignal` schema.

## Usage Guide

- **Stewards:** Look for "Needs Review" badges in the dashboard. These indicate items that may require closer inspection or discussion.
- **Developers:** Use `scripts/smoke_test_layer_d.py` to verify advisory pipeline health.
