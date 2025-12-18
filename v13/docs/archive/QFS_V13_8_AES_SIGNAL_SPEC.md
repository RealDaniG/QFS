> ⚠️ Historical Document (Archived)
> This file describes QFS V13.5 / V13.7 / V13.8 behavior and is **not** representative of the current Phase IV/V implementation.
> For up-to-date information, see `v13/docs/phase4_walkthrough.md`, `task.md`, and `docs/EXECUTIVE_SUMMARY.md`.

# QFS V13.8 AES (Artistic Evaluation Signal) Specification

**Version:** 1.0 (Zero-Sim)
**Date:** 2025-12-14
**Status:** DRAFT

## 1. Overview

The Artistic Evaluation Signal (AES) is a major signal slice in ATLAS 1.2, providing a 5-dimensional qualitative assessment of content. It strictly adheres to QFS V13.8 Zero-Simulation invariants.

## 2. Dimensions (Normalized [0,1])

1. **Composition (0.20):** Structural balance, flow, and coherence.
   - *Heuristic:* Variance of paragraph lengths (lower variance = better balance).
2. **Originality (0.25):** Uniqueness of content relative to corpus.
   - *Heuristic:* Inverse frequency of common words + content hash entropy.
3. **Emotional Resonance (0.25):** Engagement depth/quality.
   - *Heuristic:* Save/View ratio (10x multiplier).
4. **Technical Execution (0.15):** Formatting rigor.
   - *Heuristic:* Usage of markdown features (bold, headers, links).
5. **Cultural Context (0.15):** (Placeholder/Neutral)
   - *Heuristic:* Fixed neutral score (0.5), pending Knowledge Graph slice.

## 3. Integration Architecture

### 3.1 Signal Addon (`src/signals/artistic.py`)

- **Responsibility:** Pure function mapping `(Content, Context)` -> `Dimensions`.
- **Invariant:** Hash-deterministic output. No random(), no calls to external ML services.

### 3.2 Signal Policy (`policy/artistic_policy.py`)

- **Responsibility:** Mapping `Dimensions` -> `Reward Bonus`.
- **Logic:**
  - `Base Bonus = sum(dim * weight)`
  - `AEGIS Multiplier`: Apply based on user reputation tier.
    - Veteran: 1.15x
    - Established: 1.05x
    - New: 1.0x

### 3.3 Explainability

- **Traceability:** Every reward modification must be traceable to specific dimension scores.
- **Audit:** Bonuses are logged as explicit line items in the `RewardAllocated` event.

## 4. Zero-Sim Compliance

- **No external I/O:** All evaluations use provided context.
- **No Floating Point drift:** Use integer math scaling (x10000) for internal calcs, float only for final normalized display.
- **No Time:** Dependencies on `datetime.now()` conform to `epoch` or `timestamp` from context.

## 5. AEGIS Integration

- **Gate:** Only `verified=True` users are eligible for AES bonuses.
- **Tier:** Reputation tier is extracted from validated AEGIS VC in context.
