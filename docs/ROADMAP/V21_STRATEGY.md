# v21 Strategic Advancements: Offline Consensus & Resilience

**Context:** Following the successful deployment of v20 (Auth + GitHub Integration), the next strategic horizon (v21) focuses on ensuring QFS remains operational and secure even in disconnected ("Offline") environments.

---

## 1. Offline Auth Priorities

### 1.1 Offline Session Caching (Critical Path: 2 Weeks)

To enable seamless user experience during network partition:

- **Deterministic Token Validity**: Use `MOCKPQC` (or real PQC) signatures that can be verified locally without checking against a central `session_id` database, provided trust anchors are synced.
- **Local Operation Counters**: Implement Lamport-style logical clocks (`v_local`) on the client to order offline transactions.
- **Reconciliation Protocol**: Define how offline sessions re-handshake with the server upon reconnection, exchanging `v_local` vs `v_server` state headers.

### 1.2 SessionStore Replication Surface (3 Weeks)

To prepare for distributed consensus (Raft/BFT):

- **API Design**: Extend `SessionStore` to support a `Replicate(log_entry)` RPC.
- **Append-Only Logs**: Move from in-memory dictionary storage to an append-only transaction log (`wal.log`) for session events.
- **Cross-Node Lookup**: Allow nodes to forward session validity checks to the session owner (stateless validation vs stateful storage).

### 1.3 Trust Degradation Policy (1 Week)

Not all operations are safe offline.

- **Scope Restrictions**: Define `OFFLINE_READ` vs `OFFLINE_WRITE` scopes.
- **Trust Context**: Extend `resolveTrustContext()` to return `TRUST_LEVEL_DEGRADED` when offline.
- **UI Indicators**: Flash "Offline Mode - Read Only" or "Offline Queueing" in the Atlas UI.

---

## 2. GitHub Integration: Next Steps

### 2.1 Import Real Contributions (Immediate)

With the Retro Rewards logic (`bounty_github.py`) verified:

1. **Run Import Tool**: Execute `v15/tools/github_import_contributions.py` on the target repository (`RealDaniG/QFS`).
2. **Verify Events**: Check EvidenceBus for `CONTRIB_RECORDED` events.
3. **Trigger Computation**: Run the reward computation loop for recent rounds.

### 2.2 GitHub Event Listeners (v21 Feature)

Instead of polling/manual import:

- **Webhook Endpoint**: Create `/api/webhooks/github` to receive real-time `push` and `pull_request` events.
- **Signature Verification**: strictly verify `X-Hub-Signature-256`.

---

## 3. Deployment Checklist for v21

- [ ] Migrate `SessionStore` to durable storage (Redis/Disk) before multi-node.
- [ ] Implement `check_offline_status()` heartbeat in frontend.
- [ ] Update `ROADMAP-ATLAS-QFS.md` with these milestones.
