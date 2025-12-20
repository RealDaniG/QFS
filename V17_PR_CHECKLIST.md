# v17 PR Checklist: Compression & Reveal

**Purpose:** Surface existing deterministic governance and bounty engines through human-legible UI/UX  
**Constraint:** Engine frozen - no new mechanisms, only visibility and evidence  
**Status:** In Progress

---

## A. Preconditions (Branch & Engine) ✅

- [x] Work on `feat/v17-governance-bounty-f-layer` with v17 engine implemented
- [x] v17 governance F-layer complete and tested
- [x] v17 bounties F-layer complete and tested
- [x] Zero-Sim + MOCKQPC checks pass
- [x] All engine tests passing

**Verified:**

```bash
✅ python v17/tests/test_governance_f_layer.py - All tests passed
✅ python v17/tests/test_bounties_f_layer.py - All tests passed
✅ Zero-Sim: 0 critical violations
```

---

## B. Layer A – Engine (Frozen, Verify Only) ✅

- [x] v17 engine tests passing (determinism, PoE logging, outcomes)
- [x] All F-layer functions pure (state from events only)
- [x] No side effects beyond EvidenceBus emission

**Status:** Engine complete and frozen

---

## C. Layer B – Authority Visibility (Admin & Steward)

### C1. Governance Timelines 🔄

- [ ] Extend `v15/ui/admin_dashboard.py` with Governance Timeline view
  - [ ] Proposal → votes → outcome → execution rendered in order
  - [ ] Display: what happened, who participated, what rule applied
  - [ ] "View evidence" link to PoE events
- [ ] Add tests for governance timeline rendering
- [ ] Verify evidence links resolve correctly

### C2. Bounty Timelines 🔄

- [ ] Add Bounty Timeline view to admin dashboard
  - [ ] Bounty → contributions → advisory → rewards
  - [ ] Show "What agents suggested" vs "What protocol decided"
  - [ ] "View evidence" for bounty events
- [ ] Add tests for bounty timeline rendering
- [ ] Verify advisory vs F-layer distinction is clear

### C3. Decision Explanation Panels 🔄

- [ ] Implement "Decision Explanation" component
  - [ ] Governance outcomes
  - [ ] Bounty reward decisions
  - [ ] Dispute resolutions
- [ ] Each explanation provides:
  - [ ] Rule applied (plain language)
  - [ ] Inputs considered
  - [ ] Why this outcome followed
- [ ] "Show record" button to Evidence View
- [ ] Add tests for explanation accuracy

### C4. Dispute Resolution Panel 🔄

- [ ] Implement steward-facing Dispute Resolution panel
  - [ ] Disputed action summary
  - [ ] Evidence chain preview
  - [ ] Steward decision input
  - [ ] Mandatory PoE reference
- [ ] Add tests for dispute lifecycle
- [ ] Verify no action without evidence reference

---

## D. Layer C – Social Surface (User-Facing)

### D1. Conversations & Threads 🔄

- [ ] Wire conversations to governance/bounty events
  - [ ] Inline indicators ("This decision is recorded")
  - [ ] Links to explanation panel
- [ ] Add tests for conversation-event linking
- [ ] Verify evidence links resolve correctly

### D2. Contribution Memory 🔄

- [ ] Implement per-user "Contribution History" view
  - [ ] Items: posts, votes, proposals, contributions, bounties
  - [ ] Plain language summaries
  - [ ] "Show record" button for each item
- [ ] Add tests for contribution history
- [ ] Verify PoE links for all items

### D3. Escalation Flow 🔄

- [ ] Implement "Dispute" action
  - [ ] Clear lifecycle: opened → reviewed → finalized
  - [ ] Outcome visible, evidence link present
- [ ] Add tests for dispute flow
- [ ] Verify guardrails (who can open, cooldowns)

---

## E. Evidence & Replay – Progressive Disclosure

- [ ] Implement three disclosure levels:
  - [ ] Level 1: Summary (human explanation, no hashes)
  - [ ] Level 2: Evidence View (PoE events, timestamps, actors)
  - [ ] Level 3: Replay/Technical (deterministic reconstruction)
- [ ] Add tests for all three levels
- [ ] Verify users can understand at Level 1

---

## F. Governance & Incentives Posture (Guards) ✅

- [x] No new governance mechanisms beyond v17 F-layer
- [x] No token contracts or economics introduced
- [x] Incentives are non-transferable signals only
- [x] Zero-Sim and MOCKQPC unchanged and enforced

**Status:** Guards in place, no violations

---

## G. Documentation (Compression Pass)

- [ ] Update `MAINTAINERS_GUIDE.md` with v17 layers
  - [ ] Governance/bounty F-layer as procedural backend
  - [ ] EvidenceBus as canonical truth
  - [ ] Advisory agents as non-authoritative
- [ ] Create user-facing docs
  - [ ] "ATLAS records, explains, and verifies"
  - [ ] Sections: Conversations, Contribution History, Disputes, Governance & Bounties
- [ ] Add diagrams: Outcome → Explanation → Evidence → Replay

---

## H. v17 Testing & Validation

- [ ] Add end-to-end tests
  - [ ] User action → PoE emitted
  - [ ] Decision displayed with explanation
  - [ ] Explanation has evidence link
  - [ ] Evidence enables replay
- [ ] Integrate v17 tests into CI pipeline
- [ ] Verify Zero-Sim compliance

---

## I. Release & Tagging

- [ ] Open PR: `feat/v17-governance-bounty-f-layer` → `main`
  - [ ] v17 engine (complete)
  - [ ] Admin/steward surfacing
  - [ ] Social surfacing
  - [ ] Docs + tests
- [ ] CI verification
  - [ ] All v17 tests green
  - [ ] Zero-Sim unchanged/strengthened
  - [ ] Evidence coverage preserved
- [ ] Tag: `v17.0.0-beta-governance-bounties`
- [ ] Release summary emphasizing:
  - [ ] No new authority or economics
  - [ ] Trust moved from architecture to visible experience

---

## J. Final Alignment Check (Definition of Done)

- [ ] Manual narrative test for each scenario:
  - [ ] Moderation decision
  - [ ] Governance decision
  - [ ] Bounty reward
  - [ ] Dispute resolution
- [ ] Non-technical reviewer can answer:
  - [ ] "What happened?"
  - [ ] "Why did it happen?"
  - [ ] "Who decided?"
  - [ ] "Can I verify it?"
- [ ] All answers achievable without seeing code/logs/crypto

---

## Progress Summary

**Completed:**

- ✅ Engine implementation (governance + bounties)
- ✅ Engine tests (all passing)
- ✅ Zero-Sim compliance
- ✅ Guards in place

**In Progress:**

- 🔄 UI/UX layer (admin dashboard extensions)
- 🔄 Social surface (user-facing views)
- 🔄 Documentation

**Next Steps:**

1. Extend admin dashboard with governance/bounty timelines
2. Implement decision explanation panels
3. Add user-facing contribution history
4. Create comprehensive documentation
5. End-to-end testing
6. PR and release

---

**Contract:** No new authority, only legibility  
**Foundation:** v16.1.1-pre-v17-ready  
**Target:** v17.0.0-beta-governance-bounties
