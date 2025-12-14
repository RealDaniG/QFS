# ATLAS API Contracts Specification v1

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** DRAFT

---

## Overview

This document defines the Unified ATLAS API Contracts that serve as the single source of truth for all frontend clients (web, mobile, desktop) to communicate with the QFS backend, ledger, governance, wallet, and infrastructure systems in a consistent, versioned manner.

---

## API Domains

The ATLAS API is organized into 6 distinct domains:

1. **Social API** - Content, interactions, feeds, user profiles
2. **Ledger API** - Event querying, transaction history, state snapshots
3. **Governance API** - Proposals, voting, policy management
4. **Wallet/Reputation API** - Token balances, reputation scores, reward history
5. **Infrastructure API** - Node status, health checks, telemetry
6. **Public Read API** - Rate-limited, read-only access for third parties

---

## Versioning Rules

- **v1**: Additive only - new endpoints, new optional fields
- **v2**: Breaking changes allowed - field renames, endpoint removals, required field changes
- All endpoints must include version in path: `/api/v1/endpoint`
- Response headers include `API-Version: 1.0`

---

## Error Handling

All API endpoints follow a consistent error response format to ensure deterministic and predictable error handling:

### Error Response Format

```json
{
  "error_code": "string",
  "message": "string",
  "details": "string"
}
```

### Common Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `MISSING_PARAMETER` | Required parameter is missing | 400 |
| `INVALID_PARAMETER` | Parameter value is invalid | 400 |
| `UNAUTHORIZED` | Authentication required or failed | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `CONFLICT` | Resource conflict | 409 |
| `INTERNAL_ERROR` | Unexpected server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

### Determinism Guarantees

- All error responses are deterministic - same inputs always produce identical error responses
- Error messages do not leak internal implementation details
- Error handling does not depend on wall-clock time or random values
- All error paths are tested and verified

---

## Endpoint Catalog

### Social API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/feed` | GET | Get coherence-ranked content feed |
| `/api/v1/posts` | POST | Create new post |
| `/api/v1/posts/{id}` | GET | Get post details |
| `/api/v1/posts/{id}` | PUT | Update post |
| `/api/v1/posts/{id}` | DELETE | Delete post |
| `/api/v1/interactions/{type}` | POST | Submit interaction (like, comment, follow, etc.) |
| `/api/v1/users/{id}` | GET | Get user profile |
| `/api/v1/users/{id}/following` | GET | Get user's following list |
| `/api/v1/users/{id}/followers` | GET | Get user's followers list |

### Ledger API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ledger/events` | GET | Query ledger events |
| `/api/v1/ledger/events/{id}` | GET | Get specific ledger event |
| `/api/v1/ledger/state` | GET | Get current state snapshot |
| `/api/v1/ledger/history/{address}` | GET | Get address history |

### Governance API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/governance/proposals` | GET | List proposals |
| `/api/v1/governance/proposals` | POST | Create new proposal |
| `/api/v1/governance/proposals/{id}` | GET | Get proposal details |
| `/api/v1/governance/proposals/{id}/vote` | POST | Cast vote on proposal |
| `/api/v1/governance/policies` | GET | List policies |
| `/api/v1/governance/policies/{id}` | GET | Get policy details |

### Wallet/Reputation API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/wallet/balance` | GET | Get token balances |
| `/api/v1/wallet/transactions` | GET | Get transaction history |
| `/api/v1/wallet/rewards` | GET | Get reward history |
| `/api/v1/reputation/score` | GET | Get reputation score |
| `/api/v1/reputation/history` | GET | Get reputation history |
| `/api/v1/reputation/explain` | GET | Explain reputation calculation |

### Infrastructure API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/infra/nodes` | GET | List nodes |
| `/api/v1/infra/nodes/{id}` | GET | Get node details |
| `/api/v1/infra/health` | GET | Get system health status |
| `/api/v1/infra/telemetry` | GET | Get telemetry data |

### Public Read API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/public/leaderboard` | GET | Get token leaderboard |
| `/api/v1/public/stats` | GET | Get system statistics |
| `/api/v1/public/events` | GET | Get public events (rate-limited) |

---

## SDK Generation

TypeScript and Python SDKs will be generated from this specification using OpenAPI 3.0 definitions.

---