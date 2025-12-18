# v14 Regression Hash & Replay Verification

**Version**: v14.0-social-layer  
**Date**: 2025-12-18  
**Status**: Production Hardening

## Regression Hash

The v14 regression hash is a deterministic fingerprint of the entire social layer state after running a canonical scenario. This hash MUST remain stable across replays to guarantee Zero-Sim compliance.

### Current Regression Hash

```
SHA-256: [TO BE GENERATED]
```

**Scenario**: `v14_social_full_scenario`  
**Modules**: Spaces, Wall Posts, Chat  
**Events**: 11 types across 3 modules

### How to Generate

```bash
# Run canonical scenario
python v13/tests/regression/phase_v14_social_full.py > v14_trace.log

# Generate hash
sha256sum v14_trace.log > v14_regression_hash.txt

# Display hash
cat v14_regression_hash.txt
```

### Expected Output Format

```
<hash>  v14_trace.log
```

## Replay Verification

### Command

```bash
qfs verify-replay --scenario-id v14_social_full
```

### Verification Steps

1. **Load Scenario**: Read canonical event sequence from `v14_trace.log`
2. **Fresh State**: Initialize clean state (no prior data)
3. **Replay Events**: Process each event deterministically
4. **Compare State**: Verify final state matches expected
5. **Hash Check**: Confirm regression hash matches

### Success Criteria

- ✅ Final state root matches
- ✅ Per-module checksums match
- ✅ Event counts match (11 types)
- ✅ Token balances match (CHR/FLX)
- ✅ No divergence in emitted events
- ✅ Regression hash identical

### Failure Modes

| Error | Cause | Fix |
|-------|-------|-----|
| Hash mismatch | Non-deterministic code | Fix Zero-Sim violation |
| Event count mismatch | Missing/extra events | Check event emission logic |
| State divergence | Incorrect state update | Review StateTransitionEngine |
| Balance mismatch | Economic calculation error | Audit BigNum128 usage |

## Canonical Scenario: v14_social_full

### Setup

```python
# Initialize
cm = CertifiedMath()
spaces = SpacesManager(cm)
wall = WallService(cm)
chat = ChatService(cm)

# Wallets
alice = "wallet_alice"
bob = "wallet_bob"
charlie = "wallet_charlie"
```

### Event Sequence

1. **Space Created** (t=1000000)
   - Host: Alice
   - Title: "Tech Talk"
   - Expected: 0.5 CHR to Alice

2. **Space Joined** (t=1000100)
   - Participant: Bob
   - Expected: 0.2 CHR to Bob

3. **Space Spoke** (t=1000200)
   - Speaker: Bob
   - Expected: 0.1 CHR to Bob

4. **Post Created** (t=1000300)
   - Author: Alice
   - Content: "Hello ATLAS!"
   - Expected: 0.5 CHR to Alice

5. **Post Quoted** (t=1000400)
   - Quoter: Bob
   - Original: Alice's post
   - Expected: 0.3 CHR to Bob

6. **Post Pinned** (t=1000500)
   - Pinner: Alice (host)
   - Expected: 0.2 CHR to Alice

7. **Post Reacted** (t=1000600)
   - Reactor: Charlie
   - Emoji: 👍
   - Expected: 0.01 FLX to Charlie

8. **Conversation Created** (t=1000700)
   - Creator: Alice
   - Participants: [Alice, Bob]
   - Type: ONE_ON_ONE
   - Expected: 0.3 CHR to Alice

9. **Message Sent** (t=1000800)
   - Sender: Alice
   - Content CID: Qm123abc
   - Expected: 0.1 CHR to Alice

10. **Message Read** (t=1000900)
    - Reader: Bob
    - Expected: 0.01 FLX to Bob

11. **Space Ended** (t=1001000)
    - Host: Alice
    - Expected: 0.3 CHR to Alice

### Expected Final State

**Alice**:

- CHR: 1.9 (0.5 + 0.5 + 0.2 + 0.3 + 0.1 + 0.3)
- FLX: 0.0

**Bob**:

- CHR: 0.6 (0.2 + 0.1 + 0.3)
- FLX: 0.01

**Charlie**:

- CHR: 0.0
- FLX: 0.01

**Total Emitted**:

- CHR: 2.5
- FLX: 0.02

## CI Integration

### Pre-Release Workflow

Add to `.github/workflows/pre-release.yml`:

```yaml
name: Pre-Release Verification

on:
  push:
    tags:
      - 'v*'

jobs:
  verify-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run regression scenario
        run: |
          python v13/tests/regression/phase_v14_social_full.py > v14_trace.log
          sha256sum v14_trace.log > v14_regression_hash_new.txt
      
      - name: Verify regression hash
        run: |
          diff v14_regression_hash.txt v14_regression_hash_new.txt
          if [ $? -ne 0 ]; then
            echo "❌ Regression hash mismatch!"
            exit 1
          fi
          echo "✅ Regression hash verified"
      
      - name: Verify replay
        run: |
          qfs verify-replay --scenario-id v14_social_full
```

## Invariants

### Zero-Sim Invariants

1. **Deterministic IDs**: All entity IDs generated via `DeterministicID.from_string()`
2. **Sorted Iterations**: All loops over collections use `sorted()`
3. **BigNum128 Economics**: All token amounts use `BigNum128`
4. **No Randomness**: No `random`, `time.time()`, or `datetime.now()`
5. **PQC Logging**: All operations logged with PQC metadata

### Economic Invariants

1. **Conservation**: Total CHR/FLX emitted = sum of all event rewards
2. **Non-Negative**: No wallet can have negative balance
3. **Event Uniqueness**: Each event ID is unique
4. **Reward Determinism**: Same event → same reward amount

### Social Invariants

1. **Space Lifecycle**: Created → Active → Ended
2. **Participant Limits**: Max 100 participants per space/chat
3. **Host Authority**: Only host can end space or pin posts
4. **Message Ordering**: Messages sorted by (timestamp, message_id)

## Maintenance

### When to Update Hash

- ✅ Bug fixes that change economic calculations
- ✅ New features that add events
- ✅ Optimization that changes execution order
- ❌ Documentation changes
- ❌ Test-only changes
- ❌ CI configuration changes

### Update Procedure

1. Run scenario and generate new hash
2. Review diff in state/events
3. Document reason for change in git commit
4. Update this file with new hash
5. Commit both hash and documentation

---

**Status**: Hash generation pending  
**Next**: Run `phase_v14_social_full.py` and capture hash
