# Governance Dashboard API Summary

## Overview
The governance dashboard API provides operators with a read-only summary view of system activity, focusing on AEGIS advisory counts and correlated observations. This endpoint is designed for internal/admin use only and requires appropriate authorization.

## API Endpoint
```
GET /api/v1/governance/dashboard
```

## Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | string | Yes | Operator role (must be SYSTEM or PROPOSER) |
| `start_timestamp` | integer | No | Start timestamp for filtering (inclusive) |
| `end_timestamp` | integer | No | End timestamp for filtering (inclusive) |

## Response Format
```json
{
  "success": true,
  "aegis_advisory_counts": {
    "info": 15,
    "warning": 3,
    "critical": 1
  },
  "total_aegis_observations": 19,
  "top_content_with_observations": {
    "content_id_1": {
      "aegis_observations": [...],
      "agi_observations": [...]
    }
  },
  "timestamp_range": {
    "start": 10000000,
    "end": 20000000
  }
}
```

## Authorization
Only users with SYSTEM or PROPOSER roles can access this endpoint. All other roles will receive an authorization error.

## Implementation Details
- **Deterministic**: Uses deterministic timestamp filtering and ledger aggregation
- **Secure**: Role-based access control via OPEN-AGI authorization
- **Efficient**: Aggregates data directly from the CoherenceLedger without external calls
- **Configurable**: Supports optional time window filtering

## Use Cases
1. **Monitoring**: Track AEGIS advisory volume and severity distribution over time
2. **Troubleshooting**: Identify content with high volumes of correlated observations
3. **Policy Evaluation**: Assess effectiveness of governance policies through advisory trends
4. **Audit Support**: Provide summary statistics for compliance reporting

## Testing
The governance dashboard includes comprehensive tests covering:
- Valid and invalid role authorization
- Timestamp filtering functionality
- Deterministic behavior verification
- Error handling for malformed parameters