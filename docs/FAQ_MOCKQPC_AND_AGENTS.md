# FAQ: MOCKQPC, Agents, and Best Practices

> **Status:** Evergreen v16 Baseline  
> **Audience:** Developers, Contributors, Integrators

---

## 🔐 MOCKQPC & Zero-Sim

### 1. Why do we use MOCKQPC instead of real crypto in dev?

Real PQC (Dilithium/Kyber) is computationally expensive (~200ms/op on standard hardware) and produces non-deterministic signatures (randomized). This makes:

1. **Debugging impossible**: You can't replay a bug if the hash changes every time.
2. **CI slow**: Tests would take hours instead of minutes.
3. **Cost high**: In a cloud environment, PQC eats CPU credits.

MOCKQPC is **mathematically deterministic** and **free** ($0 coin cost, <1ms CPU). It ensures `Input A + Key B = Signature C`, always.

### 2. Is MOCKQPC safe?

**Yes, for its purpose.** It is NOT a security layer for mainnet value. It is a **development safety harness**.

- It mimics the *shape* and *flow* of real PQC signatures.
- It fails if you try to use it in an environment tagged `mainnet`.
- It allows us to prove the *logic* of the system (Governance, PoE, Bounties) without the *weight* of the crypto.

### 3. When will real PQC be used?

Real PQC is used **only** for:

1. **Mainnet Anchors**: Periodic batches of events are hashed together, and the *root* is signed with real PQC.
2. **High-Value Governance**: Critical rule changes (e.g., modifying the Inflation Rate) on mainnet.

For 99% of interactions (posts, likes, bounty claims), MOCKQPC or Batched-PoE is sufficient and preferred.

### 4. How do I know if I broke Zero-Sim?

The CI pipeline runs `scripts/check_zero_sim.py`. It fails if:

- You import `pqcrystals` or `dilithium` directly (outside of `adapter.py`).
- You use `random.random()`, `uuid.uuid4()`, or `time.time()` in core logic.
- You perform floating-point math on economic values (use `BigNum128`).

---

## 🤖 Advisory-Only Agents

### 5. What does "Advisory-Only" mean?

It means an AI Agent (whether it's Open-AGI, CrewAI, or an LLM) **cannot** write to the database or execute a decision directly.

- **Allowed**: An agent reads a post, calculates a "Spam Score: 95%", and emits an event `agent_advisory(post_id, spam_score=95)`.
- **Forbidden**: An agent reads a post and deletes it.

The **Deterministic Core** (`F_moderation`) reads the advisory event and decides: "If spam_score > 90%, then delete."

### 6. Why can't agents decide?

Agents are **non-deterministic** (probabilistic). If you run the same prompt twice, you might get different answers.
QFS × ATLAS requires **100% replayability**. If we let agents decide, we break the audit trail. By forcing them to be advisors, we keep the final decision logic deterministic and auditable.

### 7. Can I use a new Agent Framework?

**Yes.** The platform is framework-agnostic.
As long as your agent:

1. Runs in its own container/process.
2. Reads from the API/EvidenceBus.
3. Writes *only* `agent_advisory` events.
You can use CrewAI, LangChain, AutoGPT, or anything else.

---

## 🛠️ Operational Best Practices

### 8. How do I get paid for a contribution?

Follow the **5-Step Journey**:

1. **Issue**: Find an open Bounty (labeled `area:bounties`).
2. **Link**: Connect your Wallet to your GitHub account (Dual-Proof).
3. **PR**: Submit code with the **Core Invariant Checklist**.
4. **Merge**: Maintainers review and merge.
5. **Reward**: Chronos (CHR) or Fluid (FLX) tokens are sent to your wallet.

### 9. What is the "EvidenceBus"?

It's the central nervous system of QFS. Instead of `logger.info("User logged in")`, we do:
`evidence_bus.emit("user_login", { wallet: "0x...", method: "mockqpc" })`.
These events are hashed into a chain. If someone deletes a log, the chain breaks. This is how we prove fairness.
