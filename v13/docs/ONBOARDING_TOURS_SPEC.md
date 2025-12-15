# QFS × ATLAS: Onboarding Tours Specification

**Version:** 1.0
**Status:** DRAFT
**Scope:** P0 (Gap Analysis)

## 1. Purpose & Scope

The **QFS Onboarding Tours** provide interactive, guided experiences for new users to understand:

- How QFS rewards work
- What Coherence means and how to build it
- How to participate in governance
- The transparency guarantees (Zero-Simulation, Explain-This)

**Core Philosophy:** Education through **interactive ledger exploration**, not static tutorials.

## 2. Functional Requirements

### 2.1 Tour Types

1. **Welcome Tour**: First-time user orientation (5 steps).
2. **Rewards Deep-Dive**: Understanding the economics (7 steps).
3. **Governance Primer**: How to propose and vote (5 steps).
4. **Explain-This Workshop**: Using the transparency tools (4 steps).

### 2.2 Tour Mechanics

- **Progressive Disclosure**: Each step unlocks after the previous is completed.
- **Interactive Tasks**: Users perform real actions (e.g., post content, request an explanation).
- **Ledger-Backed Progress**: Tour completion is tracked via ledger events.
- **Rewards**: Small QFS rewards for completing tours to incentivize engagement.

### 2.3 User Experience

- **Dismissible**: Users can skip or exit at any time.
- **Resumable**: Progress is saved to the ledger.
- **Contextual**: Tours can be triggered by specific user actions (e.g., first coherence change).

## 3. Data Models

### 3.1 Tour Definition

```json
{
  "tour_id": "welcome_v1",
  "name": "Welcome to QFS × ATLAS",
  "description": "Learn the basics...",
  "steps": [
    {
      "id": "step_1",
      "title": "Your First Action",
      "description": "Post your first piece of content",
      "task_type": "POST_CONTENT",
      "reward": 10
    },
    {
      "id": "step_2",
      "title": "Check Your Coherence",
      "description": "View your coherence score",
      "task_type": "VIEW_COHERENCE",
      "reward": 5
    }
  ]
}
```

### 3.2 Tour Progress Event (On-Ledger)

```json
{
  "event_type": "TOUR_STEP_COMPLETED",
  "user_id": "0x...",
  "tour_id": "welcome_v1",
  "step_id": "step_1",
  "timestamp": "iso8601"
}
```

## 4. Implementation Plan

- [ ] **Phase 1**: Tour definition schema and storage.
- [ ] **Phase 2**: Progress tracking service.
- [ ] **Phase 3**: Task validation logic.
- [ ] **Phase 4**: UI overlay component for step presentations.

## 5. Success Metrics

- 80% of new users complete at least one tour.
- Tour completion increases 30-day retention by 25%.
- Zero complaints about "not understanding how it works".
