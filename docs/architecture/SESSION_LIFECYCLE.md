# Session Lifecycle

## 1. Creation

- **Trigger:** Wallet login with valid signature.
- **Action:** `AuthService.createSession()`.
- **Event:** `SESSION_CREATED`.
- **Artifacts:** Access Token (JWT/PASETO), Refresh Token (Opaque/Hashed).

## 2. Refresh

- **Trigger:** `refreshSession` call with valid Refresh Token + Device Hash.
- **Check:** `device_id` match (Level 2 check).
- **Event:** `SESSION_REFRESHED`.

## 3. Revocation

- **Trigger:** Logout, Security Event, or TTL expiry.
- **Event:** `SESSION_REVOKED`.

## 4. EvidenceBus Integration

All state changes are replayable from the event stream. The `SessionStore` is merely a projection of the EvidenceBus.
