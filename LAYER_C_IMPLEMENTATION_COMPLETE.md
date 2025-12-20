# Layer C: Social Surface Implementation Complete

**Date:** 2025-12-20
**Status:** ✅ Complete
**Module:** `v17.social` / `v17.ui.social_projection`

---

## 1. Overview

Layer C binds governance and bounty entities to a social context, enabling:

- **Conversation Binding:** Determinsitic Threads linked to `proposal_id` or `bounty_id`.
- **User History:** Aggregated timeline of Votes, Proposals, Bounties, Contributions, Comments, and Disputes.
- **Dispute Flows:** Formal dispute events raised against entities, visible in user history.

## 2. Components

### **F-Layer (`v17/social`)**

- `create_thread(space_id, ... reference_id)` -> `SOCIAL_THREAD_CREATED`
- `post_comment(thread_id, ...)` -> `SOCIAL_COMMENT_POSTED`
- `create_dispute(target_id, ...)` -> `SOCIAL_DISPUTE_OPENED`

### **UI Layer (`v17/ui/social_projection.py`)**

- `SocialProjection` aggregates events from `EvidenceBus`.
- `get_user_history(wallet)`: Returns comprehensive stats and timeline.
- `get_threads_for_entity(id)`: Returns linked conversations.

### **Integration**

- `v15.ui.admin_dashboard.AdminDashboard` updated to expose:
  - `get_user_profile(wallet)`
  - `get_conversations(entity)`

## 3. Testing

- **Unit Tests (`v17/tests/test_ui_social.py`):**
  - Verified binding structure.
  - Verified user timeline aggregation across Governance/Bounty/Social events.
  - Verified dispute visibility.
- **Integration Tests (`v17/tests/test_ui_integration.py`):**
  - Verified `AdminDashboard` correctly delegates to `SocialProjection` using live `EvidenceBus`.

## 4. Invariants

- **Determinism:** All Thread/Comment/Dispute IDs are hash-derived.
- **Privacy:** Public content only; PII handled via wallet addresses.
- **Zero-Sim:** No side effects; pure state reconstruction from EvidenceBus.
