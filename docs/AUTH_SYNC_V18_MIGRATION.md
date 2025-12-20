# ATLAS Auth Sync: v18.5 Ascon Migration

> **Status:** Phase 1 Complete (Backend + Frontend Integration)  
> **Date:** 2025-12-20  
> **Priority:** P0 (Blocking v18.9 App Alpha)

## Executive Summary

The ATLAS application has been migrated from legacy UUID-based sessions to **Ascon-protected session tokens** (v18.5), enabling secure, deterministic authentication across the distributed v18 backbone.

### What Changed

1. **Backend (Python)**:
   - `v15.auth.session_manager.SessionManager` now issues `ascon1.*` tokens with AEAD encryption.
   - Session data includes `wallet_address`, `scopes`, `created_at`, and `expires_at`.
   - Automatic session cleanup on expiry.
   - All session lifecycle events logged to EvidenceBus.

2. **Frontend (TypeScript/React)**:
   - `useWalletAuth` hook validates Ascon token prefix on login.
   - New `atlasFetch` utility centralizes session token attachment.
   - All authenticated hooks (`useWalletView`, `useTransactions`, `useExplain`) migrated to `atlasFetch`.

3. **API Layer**:
   - `v13/atlas/src/api/routes/auth.py` uses the unified `session_manager` singleton.
   - `v13/atlas/src/api/dependencies.py` provides `get_current_session` for protected routes.

---

## Token Format

### Ascon Session Token Structure

```
ascon1.<session_id>.<ciphertext_hex>.<tag_hex>
```

- **Prefix**: `ascon1` (version identifier)
- **Session ID**: 16-character hex (deterministic hash of wallet + timestamp)
- **Ciphertext**: Encrypted payload containing `wallet_address|scopes|expires_at`
- **Tag**: AEAD authentication tag (128-bit)

### Example

```
ascon1.a3f2c1d4e5b6a7f8.3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d.9e8f7d6c5b4a3f2e1d0c9b8a7f6e5d4c
```

---

## Migration Checklist

### Backend ✅

- [x] Updated `v15.auth.session_manager.SessionManager` with TTL and expiry logic
- [x] Integrated Ascon AEAD encryption via `v18.crypto.wallet_auth_crypto`
- [x] Added `SessionData` TypedDict for type safety
- [x] Implemented `_cleanup()` for expired session removal
- [x] Wired `session_manager` singleton in `dependencies.py`
- [x] Updated `auth.py` routes to use unified session manager

### Frontend ✅

- [x] Created `src/lib/api.ts` with `atlasFetch` utility
- [x] Updated `useWalletAuth` to validate `ascon1.` prefix
- [x] Migrated `useWalletView` to use `atlasFetch`
- [x] Migrated `useTransactions` to use `atlasFetch`
- [x] Migrated `useExplain` to use `atlasFetch` (partial - needs completion)

### Testing 🔄

- [ ] Unit test: `test_ascon_session_creation_and_validation`
- [ ] Integration test: `test_wallet_login_flow_end_to_end`
- [ ] Multi-node test: `test_session_validation_across_nodes`
- [ ] E2E test: Playwright wallet connect → API call → logout

---

## Security Properties

### Determinism ✅

- Session IDs derived from `sha256(wallet_address:count:timestamp)`
- Ascon nonces derived from deterministic context (node_id, channel_id, evidence_seq, key_id)
- All crypto operations use fixed seeds in dev/test environments

### PoE Logging ✅

All session lifecycle events are logged to EvidenceBus:

- `AUTH_LOGIN`: Wallet signature verified, session created
- `ASCON_WALLET_SESSION_ENCRYPT`: Token encrypted
- `ASCON_WALLET_SESSION_DECRYPT`: Token decrypted and validated
- `AUTH_LOGOUT`: Session revoked

### Multi-Node Readiness 🔄

**Current State**: Sessions are stored in-memory on each node.

**v18.9 Requirement**: Sessions must be validated across all Tier A nodes.

**Options**:

1. **Stateless JWT-style tokens**: Embed all session data in the encrypted payload (no server-side storage).
2. **Distributed session store**: Use Raft-replicated state or Redis cluster.
3. **Hybrid**: Short-lived stateless tokens + optional server-side revocation list.

**Recommendation**: Start with stateless tokens for v18.9 App Alpha, add revocation list in v18.10.

---

## Known Issues & Next Steps

### Issues

1. **`useExplain.ts` Migration Incomplete**: Still references undefined `getAuthToken()`. Needs manual fix.
2. **Python Import Lints**: Module-level imports not at top of file in `dependencies.py` (lines 143, 178).
3. **TypeScript Window.ethereum**: Missing type declaration for MetaMask provider.

### Next Steps (P0)

1. **Complete Frontend Migration**:
   - Fix `useExplain.ts` to use `atlasFetch` properly.
   - Add global `atlas-auth-expired` event listener to trigger re-login.

2. **Write Tests**:
   - `v18/tests/test_ascon_sessions.py`: Backend session lifecycle
   - `v13/atlas/src/tests/test_wallet_auth_integration.py`: Full login flow
   - Playwright E2E: Wallet connect → protected API call

3. **Multi-Node Validation**:
   - Implement stateless token validation (no server-side session lookup).
   - Add test: Create session on Node A, validate on Node B.

4. **Documentation**:
   - Update `PQC_SECURITY_PROFILE.md` with Ascon session details.
   - Add "Session Management" section to `ATLAS_V18_GAP_REPORT.md`.

---

## API Reference

### Backend: SessionManager

```python
from v15.auth.session_manager import SessionManager

session_manager = SessionManager(session_ttl_seconds=86400)  # 24 hours

# Create session
token = session_manager.create_session(
    wallet_address="0xABC123...",
    scopes=["bounty:read", "bounty:claim"]
)

# Validate session
session_data = session_manager.validate_session(token)
if session_data:
    print(session_data["wallet_address"])  # "0xABC123..."
    print(session_data["scopes"])          # ["bounty:read", "bounty:claim"]

# Revoke session
session_manager.revoke_session(token)
```

### Frontend: atlasFetch

```typescript
import { atlasFetch } from '@/lib/api';

// Authenticated request (default)
const response = await atlasFetch('/api/v1/wallets/', {
    method: 'GET'
});

// Unauthenticated request
const publicResponse = await atlasFetch('/api/health', {
    method: 'GET',
    auth: false
});

// Listen for session expiry
window.addEventListener('atlas-auth-expired', () => {
    // Redirect to login or show re-auth modal
    console.log('Session expired, please log in again');
});
```

---

## Compliance

### Zero-Sim ✅

- All Ascon operations use deterministic nonces.
- Session IDs include timestamp but are reproducible in test environments.
- No `random.random()` or `time.time()` outside controlled contexts.

### MOCKQPC ✅

- Ascon adapter uses environment-aware key derivation.
- In `dev`/`beta`, uses deterministic test keys.
- In `mainnet`, uses HSM-backed master keys (future).

### AGPL-3.0 ✅

- All code remains open-source.
- Ascon implementation uses public-domain reference code.

---

## References

- [v18.5 Ascon Integration Plan](./ASYNC_CRYPTO_ASCON_ADAPTER.md)
- [ATLAS v18 Gap Report](./ATLAS_V18_GAP_REPORT.md)
- [Platform Evolution Plan](./PLATFORM_EVOLUTION_PLAN.md)
- [Ascon AEAD Specification](https://ascon.iaik.tugraz.at/)

---

**Maintained by**: QFS × ATLAS Core Team  
**Last Updated**: 2025-12-20
