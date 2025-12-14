# Humor Signal Policy Specification for QFS V13.7+

## Overview

This document specifies the policy framework for humor signals in QFS V13.7+, detailing how 7-dimensional humor vectors from the `HumorSignalAddon` are mapped to economic rewards, observability features, and explainability surfaces.

## 1. Policy Integration

### 1.1 Core Integration Points

The humor signal policy integrates with the existing QFS architecture at three key points:

1. **PolicyRegistry/TreasuryEngine Interface**: Maps 7-dimensional vectors to scalar bonus factors
2. **Observability Layer**: Aggregates and analyzes humor signal outputs over time
3. **Explainability Surface**: Provides detailed breakdowns of humor-derived rewards

### 1.2 Policy Formula

The humor bonus factor is calculated as:

```
Weighted_Sum = Σ(dimensions[i] × weights[i])
Confidence_Factor = confidence
Base_Bonus = Weighted_Sum × Confidence_Factor
Final_Bonus = min(Base_Bonus, MAX_HUMOR_BONUS)
```

Where:
- `dimensions[i]` represents the score for humor dimension i (0.0 to 1.0)
- `weights[i]` represents the policy weight for dimension i
- `confidence` represents the addon's confidence in its assessment (0.0 to 1.0)
- `MAX_HUMOR_BONUS` is the policy cap (default: 0.25 or 25%)

### 1.3 Default Dimension Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| chronos | 0.15 | Timing - perfectly timed posts/responses |
| lexicon | 0.10 | Wordplay - clever puns, double entendres |
| surreal | 0.10 | Absurdity - nonsensical humor, absurdism |
| empathy | 0.20 | Relatability - shared experiences, universal themes |
| critique | 0.15 | Satire - social commentary through humor |
| slapstick | 0.10 | Physical Comedy - visual humor, memes |
| meta | 0.20 | Self-Aware - humor about humor/platform dynamics |

## 2. Safety Toggles and Controls

### 2.1 Policy Switches

The humor policy supports two primary toggles:

1. **`humor_enabled`** (boolean, default: true)
   - When false, all humor bonuses are zero regardless of signal strength
   - Allows immediate disablement of humor rewards without code changes

2. **`humor_recognition_only`** (boolean, default: false)
   - When true, humor signals generate badges/labels but produce zero economic bonus
   - Enables "recognition mode" for community feedback without economic impact

### 2.2 Caps and Limits

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `MAX_HUMOR_BONUS` | 0.25 | Maximum humor bonus (25% of base reward) |
| `DAILY_USER_CAP` | 1.0 | Maximum daily humor bonus per user (100%) |
| `ANOMALY_SPIKE_THRESHOLD` | 2.0 | Multiplier threshold for anomaly detection |

## 3. Observability Features

### 3.1 Signal Aggregation

The observability layer continuously aggregates:

- Total humor signals processed
- Dimension score distributions (histograms)
- Average confidence levels
- Bonus factor distributions
- Anomaly detection events

### 3.2 Statistical Analysis

Key statistical measures include:

- **Dimension Averages**: Mean scores across all dimensions
- **Correlation Analysis**: Relationships between humor dimensions
- **Bonus Statistics**: Mean, median, standard deviation, min/max of bonuses
- **Top Performers**: Highest-scoring content by humor bonus

### 3.3 Anomaly Detection

The system monitors for:

- Sudden spikes in humor-derived bonuses (>2x normal rate)
- Unusual dimension score patterns
- Confidence manipulation attempts
- Rate-limiting violations

## 4. Explainability Surfaces

### 4.1 Detailed Breakdown

Each humor reward includes a detailed explanation containing:

- Input dimensions and scores
- Applied weights and policy version
- Confidence factor and ledger context
- Step-by-step calculation breakdown
- Final bonus with cap information
- Deterministic verification hash

### 4.2 User-Facing Explanation

Simplified explanations for end users include:

- Summary ("Received humor bonus of 15%")
- Reason ("Strong empathy score of 0.9")
- Key metrics (dimensions, confidence, bonus)
- Policy information (version, capping)
- Verification data (hash, consistency)

### 4.3 Operator Debugging

Operators can access:

- Full calculation traceability
- Policy setting snapshots
- Historical context and comparisons
- Batch explanation capabilities
- Export functionality for analysis

## 5. Integration with AEGIS Guard

### 5.1 Anomaly Monitoring

The humor policy integrates with AEGIS advisory systems by:

- Reporting unusual humor bonus patterns
- Flagging potential manipulation attempts
- Providing structured anomaly data for policy review
- Supporting soft advisory (non-blocking) alerts

### 5.2 Advisory Format

Anomalies are reported as structured AEGIS advisories:

```json
{
  "type": "humor_anomaly",
  "severity": "warning",
  "block_suggested": false,
  "details": {
    "spike_ratio": 2.5,
    "duration_minutes": 60,
    "affected_users": 15,
    "policy_version": "v1.0.0"
  }
}
```

## 6. V13.8+ Reusability

### 6.1 Template Pattern

The humor policy implementation serves as a template for other signal types:

1. **SignalAddon Base**: Common interface for all signal providers
2. **Policy Mapping**: Standard approach to mapping vectors to rewards
3. **Observability**: Reusable aggregation and analysis patterns
4. **Explainability**: Consistent explanation generation framework

### 6.2 Extension Points

Other signals can leverage:

- Dimension weighting framework
- Confidence-based bonus modulation
- Cap and limit enforcement
- Statistical analysis tools
- Anomaly detection patterns
- Explanation generation utilities

## 7. Test Coverage

### 7.1 Policy Integration Tests

- Normal bonus calculation with various dimension combinations
- Policy toggle behavior (enabled/disabled, recognition-only)
- Cap enforcement and boundary conditions
- Deterministic behavior verification

### 7.2 Observability Tests

- Signal recording and aggregation
- Statistical calculation accuracy
- Distribution histogram generation
- Correlation analysis correctness
- Anomaly detection sensitivity

### 7.3 Explainability Tests

- Detailed explanation generation
- Simplified user explanation format
- Hash consistency verification
- Batch processing capabilities
- Export functionality validation

## 8. Evidence and Audit Readiness

### 8.1 Artifact Referencing

All humor policy components are referenced in evidence artifacts:

- `test_humor_policy.py` - Policy integration tests
- `test_humor_observatory.py` - Observability tests
- `test_humor_explainability.py` - Explainability tests
- `HUMOR_ADDON_REFACTOR_SUMMARY.md` - Implementation documentation
- `HUMOR_ADDON_ZEROSIM_COMPLIANCE_REPORT.md` - Compliance verification

### 8.2 Deterministic Guarantees

The humor policy maintains deterministic behavior through:

- Pure functional policy calculations
- Immutable policy configurations
- Deterministic statistical analysis
- Stable hashing for verification
- Zero external state dependencies

## Conclusion

The humor signal policy provides a complete framework for integrating humor assessments into QFS reward calculations while maintaining observability, explainability, and safety controls. The implementation is fully deterministic, Zero-Simulation compliant, and ready for production use in QFS V13.7+.