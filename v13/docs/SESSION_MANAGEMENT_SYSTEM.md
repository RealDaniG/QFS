# QFS Session Management System

## Overview

The QFS Session Management System provides a deterministic, ledger-replayable session layer for QFS × ATLAS with full Explain-This integration. This system implements challenge-response authentication, deterministic session lifecycle management, and cryptographic proof generation for all session-related operations.

## Key Features

### Deterministic Design
- **Pure Python Implementation**: No external dependencies that could introduce non-determinism
- **SHA-256 Only**: All ID derivation uses SHA-256 cryptographic hashing
- **Zero-Simulation Compliant**: No randomness, time, os, sys.exit, or network calls in consensus surfaces
- **Canonical JSON**: All ledger events use canonical JSON formatting
- **Deterministic Iteration**: All iterations use sorted collections to ensure reproducibility

### Session Lifecycle Management
- **Create**: Generate new sessions with deterministic IDs
- **Rotate**: Rotate existing sessions for enhanced security
- **Revoke**: Revoke sessions with reason tracking
- **Validate**: Check session activity status at specific block heights

### Challenge-Response Authentication
- **Deterministic Challenges**: Cryptographically secure challenge generation
- **Device Binding**: Strong device identity verification
- **Block-Based Expiry**: Time-based expiration using ledger blocks

### Ledger Replay Capability
- **Event-Driven State**: All session state derived from ledger events
- **Complete Reconstruction**: Full session state rebuildable from event log
- **Deterministic Replay**: Bit-exact state reproduction across all nodes

### Explain-This Integration
- **Proof Generation**: Cryptographic proofs for all session operations
- **Era Classification**: Distinguishes pre-device-binding vs device-bound sessions
- **Full Context**: Wallet, device, and session identifiers in all proofs

## Architecture

### Core Components

#### Session Manager (`session_manager.py`)
The SessionManager class provides the core session lifecycle operations:

```python
class SessionManager:
    def create_session(self, wallet_id, device_id, scope, current_block, ttl_blocks)
    def rotate_session(self, old_token, current_block)
    def revoke_session(self, token, reason, current_block)
    def is_session_active(self, token, current_block)
```

#### Session Challenge (`session_challenge.py`)
Handles challenge-response authentication flow:

```python
def compute_challenge(wallet_id, device_id, block, nonce)
def post_session_challenge(wallet_id, device_id, current_block)
def post_session_establish(wallet_id, device_id, challenge_response, current_block, session_manager)
```

#### Replay Helper (`replay_helper.py`)
Enables ledger-based session state reconstruction:

```python
def replay_sessions(events)
def get_active_sessions_at_block(sessions, block_number)
```

#### Explain Helper (`explain_helper.py`)
Generates cryptographic proofs for Explain-This system:

```python
def build_session_proof(action_event, session_events, era_cutoff_block=1000)
```

### Data Structures

#### SessionToken
```python
@dataclass
class SessionToken:
    session_id: str
    wallet_id: str
    device_id: str
    issued_at_block: int
    ttl_blocks: int
    scope: List[str]
```

## Deterministic ID Derivation

All identifiers in the session system are derived using SHA-256 hashing with explicit inputs:

### Device ID
```python
def compute_device_id(os_type: str, hardware_id: str, label: str = "") -> str:
    return sha256(f"{os_type}||{hardware_id}||{label}")
```

### Session ID
```python
def _session_id(wallet_id, device_id, issued_at_block, scope) -> str:
    payload = {
        "wallet_id": wallet_id,
        "device_id": device_id,
        "issued_at_block": issued_at_block,
        "scope": sorted(scope),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)
```

### Challenge
```python
def compute_challenge(wallet_id: str, device_id: str, block: int, nonce: str) -> str:
    challenge_input = f"{wallet_id}||{device_id}||{block}||{nonce}"
    return sha256(challenge_input)
```

## Ledger Events

The session system emits deterministic ledger events for all operations:

### SESSION_STARTED
Emitted when a new session is created:
```json
{
  "event_type": "SESSION_STARTED",
  "data": {
    "session_id": "string",
    "wallet_id": "string",
    "device_id": "string",
    "issued_at_block": "integer",
    "ttl_blocks": "integer",
    "scope": ["string"]
  }
}
```

### SESSION_ROTATED
Emitted when a session is rotated:
```json
{
  "event_type": "SESSION_ROTATED",
  "data": {
    "old_session_id": "string",
    "new_session_id": "string",
    "block": "integer",
    "wallet_id": "string",
    "device_id": "string",
    "scope": ["string"],
    "ttl_blocks": "integer"
  }
}
```

### SESSION_REVOKED
Emitted when a session is revoked:
```json
{
  "event_type": "SESSION_REVOKED",
  "data": {
    "session_id": "string",
    "reason": "string",
    "block": "integer"
  }
}
```

## Replay Mechanism

The session system can fully reconstruct its state from ledger events:

```python
# Reconstruct all session state from events
session_states = replay_sessions(ledger_events)

# Filter to active sessions at a specific block
active_sessions = get_active_sessions_at_block(session_states, block_number)
```

## Explain-This Integration

Session operations integrate with the Explain-This system to provide cryptographic proofs:

```python
proof = build_session_proof(
    action_event=action_event,
    session_events=session_events,
    era_cutoff_block=1000
)
```

The proof includes:
- `wallet_id`: User's wallet identifier
- `device_id`: Device identifier
- `session_id`: Session identifier
- `authorized_at_block`: Block when session was authorized
- `active`: Whether session was active at time of action
- `era`: Classification as "pre-device-binding" or "device-bound"

## Security Considerations

### Zero-Simulation Compliance
- No external randomness sources
- No wall-clock time dependencies
- No floating-point arithmetic
- No network or OS calls in consensus paths
- Deterministic iteration of all collections

### Cryptographic Security
- SHA-256 for all hashing operations
- Deterministic nonce generation
- Block-based time tracking (no real-time dependencies)
- Canonical JSON for all ledger representations

### Session Security
- Time-based expiration (TTL in blocks)
- Session rotation capability
- Revocation with reason tracking
- Scope-based authorization

## Testing

The session system includes comprehensive test coverage:

### Test Suites
1. **Session Lifecycle & Replay** - Basic session operations and replay
2. **Session Cutover Boundary** - Edge cases in session transitions
3. **Session Rotation Ordering** - Session rotation behavior
4. **Session Challenge Reuse** - Challenge-response authentication
5. **Session Explainability Mixed Eras** - Explain-This integration

### Test Features
- FakeLedger implementation for isolated testing
- Deterministic block numbers (no wall-clock time)
- Comprehensive state verification
- Replay functionality validation
- Explain-This proof generation testing

## Integration

### Directory Structure
```
v13/
└── services/
    └── sessions/
        ├── session_manager.py
        ├── session_challenge.py
        ├── replay_helper.py
        └── explain_helper.py
```

### Test Structure
```
v13/
└── tests/
    └── sessions/
        ├── test_session_lifecycle_replay.py
        ├── test_session_cutover_boundary.py
        ├── test_session_rotation_ordering.py
        ├── test_session_challenge_reuse.py
        └── test_session_explainability_mixed_eras.py
```

### CI/CD Integration
- Added to Zero-Sim test suite
- AST/Zero-Sim scanner compliance
- Automated testing in CI pipeline

## Usage Examples

### Creating a Session
```python
# Create session manager with ledger
session_manager = SessionManager(ledger)

# Create new session
token = session_manager.create_session(
    wallet_id="wallet_123",
    device_id="device_456",
    scope=["read", "write"],
    current_block=100,
    ttl_blocks=1000
)
```

### Challenge-Response Authentication
```python
# Generate challenge
challenge, nonce, expiry_block = post_session_challenge(
    wallet_id="wallet_123",
    device_id="device_456",
    current_block=100
)

# Client responds to challenge (in real implementation, this would involve signing)
# Establish session with response
result = post_session_establish(
    wallet_id="wallet_123",
    device_id="device_456",
    challenge_response=challenge,  # In real implementation, this would be a signature
    current_block=100,
    session_manager=session_manager
)
```

### Session Validation
```python
# Check if session is active
is_active = session_manager.is_session_active(token, current_block=150)
```

### Session Rotation
```python
# Rotate session for security
new_token = session_manager.rotate_session(token, current_block=200)
```

### Session Revocation
```python
# Revoke session
session_manager.revoke_session(token, reason="user_logout", current_block=300)
```

### Replay Session State
```python
# Reconstruct session state from ledger events
session_states = replay_sessions(ledger_events)
```

### Generate Explain-This Proof
```python
# Generate proof for an action
proof = build_session_proof(
    action_event=action_event,
    session_events=session_events
)
```

## Compliance

### Zero-Simulation Contract
The session system complies with the QFS Zero-Simulation Contract v1.3:
- No randomness in consensus paths
- No wall-clock time dependencies
- No floating-point economics
- No external I/O in consensus
- PQC signatures required for ledger writes

### Deterministic Requirements
- All IDs derived from explicit inputs only
- No hidden or internal state
- All iteration deterministic (sorted collections)
- Canonical JSON for ledger events
- Pure functions with no side effects

## Performance

### Time Complexity
- Session creation: O(1)
- Session rotation: O(1)
- Session revocation: O(1)
- Session validation: O(1)
- Replay reconstruction: O(n) where n is number of session events
- Active session filtering: O(m) where m is number of sessions

### Space Complexity
- Session storage: O(1) per session
- Replay state: O(n) where n is number of active sessions
- Proof generation: O(1)

## Future Enhancements

### Planned Features
- Enhanced device fingerprinting
- Session analytics and monitoring
- Advanced authorization scopes
- Integration with governance workflows
- Performance optimizations for high-scale deployments

### Scalability Considerations
- Efficient session lookup mechanisms
- Distributed session state management
- Caching strategies for active sessions
- Sharding for large-scale deployments

## Troubleshooting

### Common Issues
1. **Session Not Found**: Verify ledger events are properly emitted and indexed
2. **Challenge Mismatch**: Check deterministic inputs match between client and server
3. **Replay Inconsistencies**: Ensure all session events are processed in correct order
4. **Proof Generation Failures**: Verify session events contain required metadata

### Debugging Tips
- Use FakeLedger for isolated testing
- Enable detailed logging for session operations
- Validate deterministic inputs match expectations
- Check block numbering consistency

## Related Documentation

- [Zero-Sim Contract v1.3](ZERO_SIM_QFS_ATLAS_CONTRACT.md)
- [Explain-This System](EXPLANATION_AUDIT_SPEC.md)
- [PQC Provider Interface](pqc_provider.py)
- [Device Binding Specification](DEVICE_BINDING.md) *(forthcoming)*