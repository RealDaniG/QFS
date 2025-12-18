# v15 Governance + HSMF Roadmap

**Version**: v15.0  
**Focus**: Governance State Machines + HSMF Integration  
**Status**: Planning  
**Prerequisites**: v14 Social Layer merged and stable

## Executive Summary

v15 introduces formal governance state machines and deep HSMF integration across QFS. Building on v14's social layer (Spaces, Wall, Chat), v15 formalizes proposal lifecycles, guard states, and HSMF-validated social actions while maintaining strict Zero-Sim compliance and backward compatibility.

## Non-Goals (Protected Areas)

To protect v14 stability, v15 explicitly **DOES NOT**:

- ❌ Modify `CertifiedMath` or `BigNum128` core
- ❌ Change v14 social semantics (Spaces, Wall, Chat)
- ❌ Alter economic event structures without contract update
- ❌ Break Zero-Sim v1.4 compliance
- ❌ Modify StateTransitionEngine atomic guarantees
- ❌ Change deterministic ID generation

**Contract Boundary**: All v15 changes must be additive or opt-in. v14 modules remain functional without v15 features.

## Milestone 1: GovernanceStateMachine (4-6 weeks)

### Goal

Formalize infrastructure governance with deterministic state machines for proposals, voting, and enactment.

### Deliverables

#### 1.1 Core State Machine (`v13/libs/governance/GovernanceStateMachine.py`)

**States**:

```python
class ProposalState(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    VOTING = "voting"
    VOTE_PASSED = "vote_passed"
    VOTE_FAILED = "vote_failed"
    ENACTED = "enacted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
```

**Transitions**:

- `DRAFT → UNDER_REVIEW` (submit_proposal)
- `UNDER_REVIEW → VOTING` (approve_for_vote)
- `VOTING → VOTE_PASSED/VOTE_FAILED` (tally_votes)
- `VOTE_PASSED → ENACTED` (execute_proposal)
- `* → CANCELLED` (cancel_proposal, proposer-only)

**HSMF Integration**:

- Validate each transition with `HSMF.validate_action_bundle()`
- Calculate governance-specific `f_atr` based on proposal impact
- Emit economic events for state changes

#### 1.2 PolicyRegistry Integration

**Extend** `v13/policy/PolicyRegistry.py`:

```python
class PolicyRegistry:
    def __init__(self, hsmf: HSMF, governance_sm: GovernanceStateMachine):
        self.hsmf = hsmf
        self.governance_sm = governance_sm
        # existing code...
    
    def apply_governance_decision(
        self,
        proposal_id: str,
        policy_updates: Dict[str, Any],
        token_bundle: TokenStateBundle,
        log_list: List
    ) -> bool:
        """Apply policy changes from enacted proposal"""
        # Validate with HSMF
        # Update policy history
        # Emit policy_updated event
```

#### 1.3 Governance Dashboard (`v13/atlas/src/api/routes/governance.py`)

**New Endpoints**:

- `GET /governance/proposals` - List proposals with state
- `POST /governance/proposals` - Create proposal
- `POST /governance/proposals/{id}/vote` - Cast vote
- `GET /governance/metrics` - HSMF metrics dashboard

**Metrics**:

- Active proposals by state
- C_holo trends over time
- Action cost distributions
- Survival imperative violations

#### 1.4 Tests

**New Test Suite** (`v13/tests/governance/test_governance_state_machine.py`):

- Deterministic state transitions
- HSMF validation at each transition
- Economic event emission
- Policy application
- Replay consistency

**Coverage Target**: >90%

### Success Criteria

- ✅ All state transitions HSMF-validated
- ✅ Zero-Sim compliant (0 violations)
- ✅ Deterministic replay from logs
- ✅ PolicyRegistry integration working
- ✅ Dashboard shows live metrics

## Milestone 2: Guard State Machines (3-4 weeks)

### Goal

Formalize AEGIS, Economics, and Safety guards as hierarchical state machines with HSMF validation.

### Deliverables

#### 2.1 Base Guard State Machine (`v13/libs/guards/GuardStateMachine.py`)

**States**:

```python
class GuardState(Enum):
    UNCHECKED = "unchecked"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    FLAGGED = "flagged"
    PENALIZED = "penalized"
    CLEARED = "cleared"
```

**Transitions**:

- `UNCHECKED → UNDER_REVIEW` (trigger_review)
- `UNDER_REVIEW → APPROVED/FLAGGED` (complete_review)
- `FLAGGED → PENALIZED/CLEARED` (apply_penalty/clear_flag)

#### 2.2 Specialized Guards

**AEGIS Guard** (`v13/libs/guards/AEGISGuardStateMachine.py`):

- Inherits from `GuardStateMachine`
- Adds safety-specific states
- HSMF validation for safety thresholds

**Economics Guard** (`v13/libs/guards/EconomicsGuardStateMachine.py`):

- Inherits from `GuardStateMachine`
- Adds economic-specific states
- HSMF validation for supply deltas

**Coherence Guard** (`v13/libs/guards/CoherenceGuardStateMachine.py`):

- Inherits from `GuardStateMachine`
- Adds coherence-specific states
- HSMF validation for C_holo thresholds

#### 2.3 Integration with Existing Guards

**Wrap existing guards** without breaking them:

```python
class AEGISGuard:
    def __init__(self, cm: CertifiedMath, hsmf: HSMF):
        self.cm = cm
        self.hsmf = hsmf
        self.state_machine = AEGISGuardStateMachine(cm, hsmf)
        # existing code...
    
    def validate_action(self, action, token_bundle, log_list):
        # Existing validation
        result = self._legacy_validate(action)
        
        # NEW: State machine tracking
        if not result.passed:
            self.state_machine.transition(
                GuardState.UNCHECKED,
                GuardState.FLAGGED,
                token_bundle,
                log_list
            )
        
        return result
```

#### 2.4 Tests

**Test Suite** (`v13/tests/guards/test_guard_state_machines.py`):

- State transitions for each guard type
- HSMF validation
- Hierarchical composition
- Backward compatibility with existing guards

### Success Criteria

- ✅ All guards have state machine layer
- ✅ Existing guard behavior unchanged
- ✅ HSMF validation integrated
- ✅ Zero-Sim compliant
- ✅ Tests pass

## Milestone 3: Social HSMF Validation (4-5 weeks)

### Goal

Integrate HSMF validation into v14 social modules for high-impact actions.

### Deliverables

#### 3.1 HSMF-Validated Social Events

**Update Event Emission** (additive, opt-in):

**Spaces** (`v13/atlas/spaces/spaces_events.py`):

```python
def emit_space_created(
    space: Space,
    cm: CertifiedMath,
    hsmf: Optional[HSMF],  # NEW: Optional HSMF
    token_bundle: Optional[TokenStateBundle],  # NEW: Optional bundle
    log_list: List,
    pqc_cid: str = ""
) -> EconomicEvent:
    """Emit space_created event with optional HSMF validation"""
    
    # NEW: HSMF validation if provided
    if hsmf and token_bundle:
        f_atr = BigNum128.from_string("0.1")  # Base ATR for space creation
        hsmf_result = hsmf.validate_action_bundle(
            token_bundle, f_atr, space.created_at, log_list
        )
        
        if not hsmf_result.is_valid:
            raise ValueError(f"HSMF validation failed: {hsmf_result.errors}")
        
        # Scale reward by C_holo
        c_holo = hsmf_result.raw_metrics.get('c_holo')
        base_reward = BigNum128.from_string("500000000000000000")
        final_reward = cm.mul(base_reward, c_holo, log_list, pqc_cid)
    else:
        # Fallback to v14 behavior
        final_reward = BigNum128.from_string("500000000000000000")
    
    # Rest of event emission...
```

**Wall Posts** (`v13/atlas/wall/wall_events.py`):

- Same pattern as Spaces
- Optional HSMF validation
- C_holo-based reward scaling

**Chat** (`v13/atlas/chat/chat_events.py`):

- Same pattern as Spaces
- Optional HSMF validation
- C_holo-based reward scaling

#### 3.2 ATLAS Gateway Integration

**Update** `v13/atlas_api/gateway.py`:

```python
class AtlasAPIGateway:
    def __init__(self, enable_hsmf_validation: bool = False):
        self.cm = CertifiedMath()
        self.hsmf = HSMF(self.cm) if enable_hsmf_validation else None
        # existing code...
    
    def post_interaction(self, interaction_type, request):
        # Get user token bundle (if HSMF enabled)
        token_bundle = None
        if self.hsmf:
            token_bundle = self._get_user_token_bundle(request.user_id)
        
        # Call social module with optional HSMF
        # Modules handle None gracefully (v14 behavior)
```

#### 3.3 Configuration Flag

**Add to** `v13/config/atlas_config.py`:

```python
class AtlasConfig:
    # v14 defaults
    ENABLE_HSMF_SOCIAL_VALIDATION = False  # Opt-in for v15
    HSMF_MIN_C_HOLO = "0.5"  # Minimum C_holo for social actions
    HSMF_MAX_ACTION_COST = "10.0"  # Maximum action cost
```

#### 3.4 Tests

**New Tests** (`v13/tests/atlas/test_hsmf_social_integration.py`):

- HSMF-validated social actions
- C_holo reward scaling
- Fallback to v14 behavior when disabled
- Survival imperative enforcement

**Regression Tests**:

- Verify v14 behavior unchanged when HSMF disabled
- Verify deterministic replay with HSMF enabled

### Success Criteria

- ✅ HSMF validation opt-in for social modules
- ✅ v14 behavior preserved when disabled
- ✅ C_holo-based reward scaling working
- ✅ Zero-Sim compliant
- ✅ Tests pass with both modes

## Timeline

| Milestone | Duration | Dependencies |
|-----------|----------|--------------|
| M1: GovernanceStateMachine | 4-6 weeks | v14 merged |
| M2: Guard State Machines | 3-4 weeks | M1 complete |
| M3: Social HSMF Validation | 4-5 weeks | M1, M2 complete |

**Total**: 11-15 weeks (3-4 months)

## Contract Updates

### v1.5 Contract Additions

**New Invariants**:

1. **Governance Determinism**: All proposal state transitions must be deterministic and replayable
2. **Guard State Tracking**: All guard decisions must be logged with state transitions
3. **HSMF Social Opt-In**: Social HSMF validation is opt-in and backward compatible

**Updated Sections**:

- Add governance state machine specification
- Add guard state machine specification
- Add HSMF social validation rules

## Risk Mitigation

### Backward Compatibility

- All v15 features are additive or opt-in
- v14 modules work without v15 features
- Configuration flags control new behavior

### Zero-Sim Compliance

- All new code follows Zero-Sim v1.4
- Deterministic state transitions
- No randomness, time, or floats
- Sorted iterations

### Testing Strategy

- Unit tests for each milestone
- Integration tests across milestones
- Regression tests for v14 compatibility
- End-to-end replay verification

## Success Metrics

### Technical

- Zero-Sim violations: 0
- Test coverage: >90%
- Regression test pass rate: 100%

### Functional

- Governance proposals: Deterministic lifecycle
- Guard states: Tracked and auditable
- Social HSMF: Opt-in working, v14 preserved

### Performance

- State transition overhead: <10ms
- HSMF validation overhead: <50ms
- No degradation to v14 performance

## Post-v15 Vision

### v16+ Opportunities

- Multi-step reward flows (vesting, staking)
- Dispute resolution state machines
- Node onboarding state machines
- Advanced governance (quadratic voting, delegation)

### Long-Term Goal

HSMF as the formal backbone for all stateful processes in QFS, with:

- Deterministic transitions
- Event-based triggers
- Full audit trails
- Zero-Sim compliance

---

**Status**: Ready for v14 merge, v15 planning complete
