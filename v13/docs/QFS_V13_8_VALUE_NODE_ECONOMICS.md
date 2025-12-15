# QFS V13.8 Value-Node Economics Specification

## Overview

The Value-Node Economics slice provides deterministic, replayable explanations for wallet rewards in the QFS system. It builds on the existing value-node model to offer transparent insights into how rewards are calculated, while maintaining strict economic isolation and Zero-Simulation compliance.

## Core Invariants

1. **Pure View/Projection**: Value-node economics provides only view/projection semantics with no direct economic effects
2. **Economic Isolation**: All economic impact flows exclusively through QFS core engines (TreasuryEngine, RewardAllocator)
3. **Zero-Simulation Compliance**: No floating-point operations, random values, wall-clock timestamps, or external I/O
4. **Deterministic Replayability**: Outputs are fully reproducible from ledger events and fixed inputs
5. **No TreasuryEngine Access**: Value-node modules do not import or directly access TreasuryEngine, RealLedger, or TokenStateBundle

## Architecture

### Replay Interface
```
Input:
- events: List[Dict[str, Any]] (ledger-like events)
- initial_state: UserState (initial value-node state)

Output:
- final_state: UserState (deterministic final state after event application)
```

### Explainability Interface
```
Input:
- wallet_id: str (target wallet identifier)
- epoch: int (epoch number)
- base_reward: Dict[str, Any] (base reward information)
- bonuses: List[Dict[str, Any]] (bonus information)
- caps: List[Dict[str, Any]] (cap information)
- guards: List[Dict[str, Any]] (guard results)

Output:
- ValueNodeRewardExplanation with:
  - wallet_id: str
  - total_reward: Dict[str, Any]
  - reason_codes: List[str]
  - explanation_hash: str (SHA256 for verification)
```

## Test Coverage

### Replay Tests
- `test_value_node_replay_is_deterministic` - Core deterministic replay test
- `test_complex_event_trace_deterministic` - Complex event trace deterministic test
- `test_empty_event_trace` - Empty event trace handling
- `test_unknown_event_type_handled` - Unknown event type handling
- `test_negative_amounts_handled` - Negative reward amounts handling
- `test_zero_amounts_handled` - Zero reward amounts handling
- `test_large_event_sequence_performance` - Large event sequence performance
- `test_duplicate_events_idempotent` - Duplicate events handling
- `test_out_of_order_events` - Out-of-order events handling
- `test_malformed_event_data_handling` - Malformed event data handling
- `test_boundary_timestamp_values` - Boundary timestamp values handling

### Explainability Tests
- `test_explain_value_node_reward` - Core reward explanation generation
- `test_explanation_deterministic_hash` - Explanation hash determinism
- `test_explanation_consistency_verification` - Explanation consistency verification
- `test_simplified_explanation` - Simplified explanation generation
- `test_explanation_reason_codes_guard_failures` - Guard failure reason codes
- `test_explanation_reason_codes_various_conditions` - Various condition reason codes
- `test_batch_explain_rewards` - Batch reward explanation
- `test_value_node_signal_pure_functionality` - Pure function verification
- `test_no_network_io_in_value_node_modules` - Network I/O restriction verification
- `test_no_filesystem_io_in_value_node_modules` - Filesystem I/O restriction verification
- `test_no_ledger_adapters_in_value_node_modules` - Ledger adapter restriction verification
- `test_extreme_reward_values` - Extreme reward values handling
- `test_malformed_input_data_handling` - Malformed input data handling
- `test_different_policy_configurations` - Different policy configurations
- `test_explanation_hash_collision_resistance` - Explanation hash collision resistance

## Verification Evidence

See `evidence/value_node/value_node_slice_evidence.json` for comprehensive evidence bundle including:
- All 28 tests passing
- Static analysis confirming no forbidden imports or I/O
- Deterministic replay verification
- Compliance verification