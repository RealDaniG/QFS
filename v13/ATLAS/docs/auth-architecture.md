# auth-architecture.md

## 1. Wallet-Based Auth Model

Authentication in v19 is exclusively wallet-based, tying all session interactions to a verifiable on-chain identity (Public Key).

### Concepts

* **Wallet Connection**: Establishing a link between the UI and the Provider (Metamask, WalletConnect). This proves *possession* of the wallet interface but not *identity*.
* **Authenticated Session**: A cryptographic proof of identity. Established by signing a challenge message with the wallet's private key.
* **Session Token**: A verifiable JWT or opaque token issued by the backend after successful challenge verification. This token is required for all protected API calls.

### Deterministic Token Derivation

**1. Session Tokens**: Derived via legacy **SHA-256** (via `SessionManager`, aligning with existing auth backend).
**2. P2P Envelopes**: Derived via **SHA3-256** (v19 standard).

```python
# Session Token (Classic)
token = sha256(signature || wallet_address || session_nonce)
```

This ensures that the same successful login event always results in the same session identifier (within the nonce window), aiding in auditability.

## 2. Backend Routes

The backend exposes a standard SIWE (Sign-In with Ethereum) style flow, adapted for QFS deterministic requirements.

* `POST /api/auth/challenge`
  * **Input**: `wallet_address`
  * **Output**: `challenge_string` (e.g., "Login to ATLAS v19. Nonce: <random>")
  * **Logic**: Generates or retrieves a pending challenge.

* `POST /api/auth/verify`
  * **Input**: `wallet_address`, `signature` (Hex)
  * **Output**: `session_token`, `user_profile`
  * **Logic**: Verifies `recover(challenge, signature) == wallet_address`. If valid, derives `session_token` via `SessionManager`.

* `GET /api/auth/session`
  * **Header**: `Authorization: Bearer <session_token>`
  * **Output**: `is_valid`, `expires_at`, `permissions`

### P2P Interaction

The Auth system is the gatekeeper for P2P.

* The P2P Node cannot start until a valid `session_token` is present.
* Requests for Session Keys (`/api/p2p/session`) require a valid `session_token`.
* This ensures only authenticated peers can derive the keys necessary to decrypt or encrypt traffic for a specific Space.

## 3. Frontend `useWalletAuth` Hook

The `useWalletAuth` hook is the central manager for authentication state in the React application.

**Responsibilities:**

1. **Challenge Retrieval**: Automatically requests a challenge when a wallet connects.
2. **Signature Request**: Prompts the user to sign the challenge via their wallet provider.
3. **Verification**: Submits the signature to `/api/auth/verify`.
4. **Persistence**: Stores the returned `session_token` (e.g., in `localStorage` or memory, depending on security settings).
5. **Rehydration**: Checks for existing valid sessions on app reload (`/api/auth/session`).
6. **Interceptor Injection**: Provides the `session_token` to the global Fetch/Axios interceptors for use in all subsequent API requests.

## 4. P2P Integration

**"No Auth, No P2P"**

1. **Boot Sequence**:
    * App Launch -> Connect Wallet -> Sign Challenge -> **Auth Success**.
    * **Auth Success** -> Initialize P2P Node -> Request keys for default Space.
2. **Access Control**:
    * The backend refuses to issue P2P Session Keys to unauthenticated requests.
    * Without keys, the P2P node can listen to traffic (encrypted noise) but cannot decrypt it (payloads remain opaque).
