# QFS V13.7 HumorSignalAddon Specification

## Overview

The HumorSignalAddon is a pure signal provider that evaluates content across 7 humor dimensions and produces deterministic, replayable outputs. It operates as a SignalAddon within the QFS ecosystem, conforming to Zero-Simulation principles and maintaining strict economic isolation.

## Core Invariants

1. **Pure Signal Provider**: HumorSignalAddon produces only signal outputs, with no direct economic effects
2. **Economic Isolation**: All economic impact flows exclusively through PolicyRegistry → TreasuryEngine
3. **Zero-Simulation Compliance**: No floating-point operations, random values, wall-clock timestamps, or external I/O
4. **Deterministic Replayability**: Outputs are fully reproducible from ledger events and fixed inputs
5. **No TreasuryEngine Access**: Humor modules do not import or directly access TreasuryEngine, RealLedger, or TokenStateBundle

## Architecture

### Signal Interface
```
Input:
- content: str (text content to evaluate)
- context: Dict[str, Any] (ledger-derived metrics: views, laughs, saves, replays, author_reputation)

Output:
- SignalResult with:
  - signal: "comedic_value"
  - version: "v1"
  - confidence: float [0,1]
  - metadata: {
      "dimensions": {
        "chronos": float [0,1],
        "lexicon": float [0,1],
        "surreal": float [0,1],
        "empathy": float [0,1],
        "critique": float [0,1],
        "slapstick": float [0,1],
        "meta": float [0,1]
      },
      "ledger_context": Dict[str, Any]
    }
```

### Policy Interface
```
Input:
- dimensions: Dict[str, float] (7-dimensional humor vector)
- confidence: float [0,1]

Output:
- HumorBonusCalculation with:
  - bonus_factor: float [0, max_bonus_ratio]
  - dimensions_used: Dict[str, float]
  - weights_applied: Dict[str, float]
  - cap_applied: Optional[float]
  - policy_version: str
```

## Test Coverage

### Policy Tests
- `test_all_mode_combinations_with_boundary_values` - Covers all policy modes with boundary values
- `test_daily_cap_edge_cases` - Tests exact cap, cap+ε, and multiple user scenarios
- `test_negative_or_malformed_vectors_safely_handled` - Ensures graceful handling of invalid inputs

### Observability Tests
- `test_histogram_realistic_distributions` - Verifies histogram calculation with realistic data distributions
- `test_anomaly_detection_spike_scenarios` - Tests anomaly flagging in crafted spike scenarios
- `test_policy_version_hash_correctness` - Ensures policy version/hash correctness in outputs

### Explainability Tests
- `test_reason_code_combinations` - Tests various reason-code combinations
- `test_explanation_hash_stability` - Verifies explanation hash stability under replay
- `test_api_response_shapes` - Ensures proper API response shapes

### Compliance Tests
- `test_no_ledger_adapters_in_humor_modules` - Verifies no TreasuryEngine/ledger adapter usage
- `test_no_network_io_in_humor_modules` - Ensures no network I/O in humor modules
- `test_no_filesystem_io_in_humor_modules` - Ensures no filesystem I/O in humor modules

## Verification Evidence

See `evidence/humor/humor_slice_evidence.json` for comprehensive evidence bundle including:
- All 47 tests passing
- Static analysis confirming no forbidden imports or I/O
- Deterministic replay verification
- Compliance verification