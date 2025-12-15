# Direct Messaging × Open-AGI Integration Specification

**Version:** 1.0
**Status:** DRAFT
**Purpose:** Wire DM through Open-AGI for simulation, guarding, and auditability

## 1. Capability Surface Definition

### 1.1 DM Capability Group

```python
DM_CAPABILITIES = {
    "DM_SEND": {
        "description": "Send a direct message to another user",
        "scope": ["PRODUCTION", "SIMULATION"],
        "requires": ["VERIFIED_IDENTITY", "MIN_COHERENCE_300"]
    },
    "DM_READ_OWN": {
        "description": "Read own message inbox",
        "scope": ["PRODUCTION", "SIMULATION"],
        "requires": ["VERIFIED_IDENTITY"]
    },
    "DM_CREATE_THREAD": {
        "description": "Initiate a new conversation thread",
        "scope": ["PRODUCTION", "SIMULATION"],
        "requires": ["VERIFIED_IDENTITY", "MIN_COHERENCE_300"]
    },
    "DM_ADMIN_SIMULATE": {
        "description": "Simulate DM interactions for testing/demos",
        "scope": ["SIMULATION"],
        "requires": ["OPEN_AGI_SIMULATION_ROLE"]
    }
}
```

### 1.2 Policy Binding

```python
# In v13/policy/authorization.py
CAPABILITY_POLICIES = {
    # Existing capabilities...
    "DM_SEND": {
        "rate_limit": "10_per_day",
        "aegis_pre_check": True,
        "ledger_event": "DM_SIGNAL"
    },
    "DM_READ_OWN": {
        "rate_limit": "1000_per_hour",
        "aegis_pre_check": False
    }
}
```

## 2. Open-AGI Adapter Layer

### 2.1 Tool Definitions

```typescript
// Open-AGI Tool Schema
interface DMTools {
  dm_create_thread: {
    input: { recipient_id: string };
    output: { thread_id: string };
    errors: ["RECIPIENT_NOT_FOUND", "COHERENCE_TOO_LOW", "BLOCKED"];
  };
  
  dm_send_message: {
    input: { 
      thread_id: string;
      content: string;
      storage_uri?: string;
    };
    output: { 
      message_id: string;
      signal_hash: string;
    };
    errors: ["THREAD_NOT_FOUND", "CONTENT_FLAGGED", "RATE_LIMITED"];
  };
  
  dm_list_threads: {
    input: { since?: timestamp };
    output: { threads: Thread[] };
    errors: [];
  };
  
  dm_get_message_history: {
    input: { thread_id: string; limit?: number };
    output: { messages: Message[] };
    errors: ["THREAD_NOT_FOUND", "UNAUTHORIZED"];
  };
}
```

### 2.2 Adapter Implementation Location

- `v13/integrations/openagi_dm_adapter.py`
- Routes through `QFSEventBridge` with `scope: SIMULATION` tag when called by simulation role

## 3. AEGIS Guard Integration

### 3.1 Pre-Send Guard Hooks

```python
def dm_send_with_guards(sender_id: str, recipient_id: str, content: str, scope: str):
    # 1. Content Safety Check
    aegis_result = aegis_guard.check_content(content)
    if aegis_result.flagged:
        return Error("CONTENT_FLAGGED", aegis_result.reason)
    
    # 2. Spam/Sybil Check
    if rate_limiter.is_exceeded(sender_id, "DM_SEND"):
        return Error("RATE_LIMITED")
    
    # 3. Block List Check
    if block_list.is_blocked(sender_id, recipient_id):
        return Error("BLOCKED")
    
    # 4. Proceed with send
    return dm_service.send_message_signal(...)
```

### 3.2 Explainability Integration

Every guard decision must be explainable:

```python
{
  "action": "DM_SEND_BLOCKED",
  "reason": "AEGIS_CONTENT_FLAG",
  "explanation_id": "explain_dm_block_123",
  "policy_version": "v13.8",
  "inputs": [
    {"event_id": "aegis_scan_456", "flag_type": "SAFETY_KEYWORD"}
  ]
}
```

## 4. Event Bridge Integration

### 4.1 Simulated DM Events

```json
{
  "event_type": "DM_SIGNAL",
  "scope": "SIMULATION",
  "sender": "openagi_sim_user_1",
  "recipient": "openagi_sim_user_2",
  "storage_uri": "sim://mock_message_hash",
  "timestamp": "deterministic_sim_time",
  "simulation_session_id": "sim_abc123"
}
```

### 4.2 Replay Guarantee

Simulated events must be:

- **Deterministic**: Same inputs → Same event structure
- **Ledger-shaped**: Would be valid if committed to real ledger
- **Replayable**: Can reconstruct thread state from event stream

## 5. Testing Requirements

### 5.1 Open-AGI + DM Scenarios

```python
# test_openagi_dm_integration.py
def test_simulation_role_dm_flow():
    """OPEN-AGI simulation role performs full DM cycle."""
    sim_role = create_simulation_role()
    
    # Create thread (simulated)
    thread = sim_role.execute("dm_create_thread", recipient="user_b")
    assert thread["scope"] == "SIMULATION"
    
    # Send message
    msg = sim_role.execute("dm_send_message", thread_id=thread["id"], content="Hello")
    assert msg["ledger_event"]["scope"] == "SIMULATION"
    
    # List threads
    threads = sim_role.execute("dm_list_threads")
    assert len(threads) == 1
    
    # Verify no real ledger writes
    assert real_ledger.count() == 0
```

### 5.2  Replay Test

```python
def test_dm_event_stream_replay():
    """Replay simulated DM events to reconstruct state."""
    sim_events = generate_dm_simulation_events()
    
    # Replay through DM service
    dm_service = DirectMessagingService()
    for event in sim_events:
        dm_service.replay_event(event)
    
    # Verify idempotent reconstruction
    threads = dm_service.get_all_threads()
    assert threads == expected_thread_state
```

## 6. Evidence Updates

### 6.1 Required Evidence Additions

`DIRECT_MESSAGING_EVIDENCE.json` must now include:

```json
{
  "openagi_integration": {
    "capabilities_defined": ["DM_SEND", "DM_READ_OWN", "DM_CREATE_THREAD", "DM_ADMIN_SIMULATE"],
    "adapter_location": "v13/integrations/openagi_dm_adapter.py",
    "simulation_role_constraints": "VERIFIED",
    "event_bridge_integration": "COMPLETE"
  },
  "aegis_coverage": {
    "content_safety": true,
    "spam_detection": true,
    "block_list_enforcement": true,
    "guard_explainability": true
  },
  "replay_guarantee": {
    "deterministic_events": true,
    "ledger_shaped": true,
    "state_reconstruction": true
  }
}
```

## 7. Implementation Checklist

- [ ] Add DM capabilities to `v13/policy/authorization.py`
- [ ] Create `v13/integrations/openagi_dm_adapter.py`
- [ ] Wire AEGIS guards into DM send path
- [ ] Extend `test_dm_integration.py` with Open-AGI scenarios
- [ ] Add replay test for simulated DM events
- [ ] Update `DIRECT_MESSAGING_EVIDENCE.json`
- [ ] Create Explain-This resolver for DM notifications
- [ ] Add DM to onboarding tour (simulation demo)
