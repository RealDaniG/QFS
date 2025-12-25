# EvidenceBus Auth Events (v1)

## Core Events

### `SESSION_CREATED`

- **Fields:** `session_id`, `wallet_address`, `device_hash`, `timestamp`, `scopes`.
- **Source:** `AuthService`.

### `SESSION_REFRESHED`

- **Fields:** `session_id`, `new_expires_at`, `refresh_index`.

### `SESSION_REVOKED`

- **Fields:** `session_id`, `reason`.

## Security Events

### `DEVICE_MISMATCH`

- **Fields:** `session_id`, `stored_hash`, `presented_hash`.
- **Severity:** Warning/Error.

### `IDENTITY_BOUND`

- **Fields:** `wallet_address`, `subject_type` (oidc/pqc), `subject_id`, `proof`.

## Versioning

- `auth_event_version: 1` included in all payloads.
