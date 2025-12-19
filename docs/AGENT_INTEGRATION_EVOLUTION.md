# QFS × ATLAS: Timeless Agent Integration & Evolution Plan

> **Status:** Canonical Doctrine  
> **Principle:** Agents are advisory, replaceable, and non-authoritative.

---

## Principle Statement (Non-Negotiable)

**Agents are advisory, replaceable, and non-authoritative.**  
**Deterministic functions, governance logic, and EvidenceBus are the sole sources of truth.**

This principle governs all current and future agent integrations, regardless of framework, vendor, or model capability.

---

## 1. Canonical Role of the Agent Layer

### 1.1 What the Agent Layer Is

The agent layer exists to:

- Produce advisory signals
- Perform non-binding analysis
- Emit structured events into the EvidenceBus

**Agents may:**

- Score content
- Suggest classifications
- Surface anomalies
- Propose actions

**Agents may never:**

- Mutate state
- Trigger irreversible actions
- Allocate rewards
- Override deterministic logic

**All authority remains with:**

- `F_moderation_v1+`
- Governance rules
- Wallet-bound identity and evidence

---

## 2. Status of Open-AGI (Legacy Integration)

### 2.1 Official Classification

Open-AGI is designated as: **Legacy / Experimental Agent Integration**

This designation is permanent unless explicitly revoked by governance.

### 2.2 Policy for Open-AGI

- The codebase remains in place
- No new features depend on it
- No refactors are performed for improvement
- Only security-critical fixes are allowed
- Documentation and headers clearly mark it as: **“Experimental – Not on the critical path”**

This preserves prior investment and historical context without accruing further technical debt.

---

## 3. Why Agent Framework Choice Is Not Urgent

This is a structural fact, not a temporary condition.

**Because:**

- Agents emit events, not decisions
- Events are logged, replayable, ignorable
- Deterministic functions consume or ignore them
- EvidenceBus enforces uniform interfaces

**Therefore:**

- The agent framework is an implementation detail, not a platform dependency.
- Security, determinism, cost, and compliance do not depend on which agent framework is used.

---

## 4. Short-Term Doctrine (Always Applicable)

Until core product surfaces are mature, the system follows this rule:

### 4.1 No New Agent Investment Until Core Flows Are Stable

**Core flows include:**

- Wallet ↔ GitHub dual-proof
- Bounty lifecycle (create → submit → verify → reward)
- Contributor dashboards
- Governance & moderation UI
- Secure social primitives (chat, spaces, posts)
- Cost and observability tooling

**As long as these are evolving:**

- Agent framework migration is deferred
- Open-AGI is frozen
- New agent logic is conceptual or simulated only

This prevents parallel stacks, documentation drift, and maintenance overhead.

---

## 5. Medium-Term Integration Pattern (Framework-Agnostic)

When core flows stabilize, the platform adopts a single advisory-only agent interface, regardless of framework.

### 5.1 The Only Allowed Integration Shape

All agent frameworks must:

1. Run out of band
2. Consume read-only data
3. Write only to EvidenceBus
4. Have zero write access elsewhere

**Emit events of the form:**

```json
{
  "type": "agent_advisory",
  "source": "agent_framework_name",
  "subject": "content | user | action",
  "signal": "score | label | explanation",
  "confidence": 0.0-1.0,
  "timestamp": "...",
  "trace_id": "..."
}
```

---

## 6. Migration Strategy (Incremental, Low-Risk)

### 6.1 Introduction of a New Agent Stack

When ready:

1. Select one modern framework (e.g., CrewAI, LangGraph, n8n)
2. Deploy it in Advisory-only, Read-only, Log-only mode

### 6.2 Side-by-Side Evaluation

For a fixed observation window, compare:

- Agent signals vs deterministic heuristics
- Open-AGI outputs (if any)
- Cost, latency, explainability

**No live decisions depend on it.**

### 6.3 Narrow Activation

If performance is acceptable, activate one narrow use case (e.g., content scoring) as **advisory, overrideable, and logged**.

---

## 7. Decommissioning Open-AGI

Open-AGI is removed only when all of the following are true:

1. A replacement advisory stack is live
2. Signals are demonstrably equal or better
3. No documentation references Open-AGI as active
4. CI and EvidenceBus show no dependency

At that point, Open-AGI is archived and marked “Historical Integration”.

---

## 8. Long-Term Steady State

The platform converges to:

- One official code-level agent stack (e.g., CrewAI or LangGraph)
- Optional low-code orchestration (n8n)
- Strict advisory boundaries
- Governance-controlled upgrades

---

## 9. When an Immediate Switch Would Be Justified

A full migration is justified **only if**:

1. **Open-AGI becomes:**
   - Unmaintained
   - Incompatible with AGPL
   - A security liability

2. **A strategic requirement exists:**
   - Enterprise partner mandate
   - SLA-backed vendor requirement
   - Regulatory constraint

Absent those conditions, switching early is negative ROI.

---

## 10. Final Doctrine

**Stabilize the product surface first; agents are replaceable advisors, not foundations.**

This plan remains valid regardless of framework trends, model capabilities, or market cycles.
