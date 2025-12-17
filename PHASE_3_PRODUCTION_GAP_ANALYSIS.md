# Phase 3 Production: Gap Analysis & Remediation Plan

**Objective:** Transition from "Simulated PQC with Hash-based Derivation" to "Production HD Wallet with Real PQC & Device Binding".

## 1. key Derivation & HD Wallets (Stage 1)

**Current State (`v13/libs/crypto/derivation.py`):**

- Uses HKDF-SHA256 with string-based contexts (`"QFS::SYSTEM_CREATOR::DEV"`).
- Simulates HD paths by including the path string in the HKDF `info` parameter.
- **Verdict:** Cryptographically deterministic but not BIP-32/44 compliant. Cannot be loaded into standard hardware wallets.

**Gap:**

- Need authentic BIP-32/44 derivation logic (or a library wrapper like `bip_utils` or `hdwallet` if Python-side, or strict HKDF-chaining if following the spec manually).
- `generate_keypair` accepts `seed` but assumes fixed algorithm.

**Remediation:**

- Refactor `derivation.py` to implement (or wrap) standard BIP-32 CKD (Child Key Derivation) functions.
- Define `QFS_COIN_TYPE` (e.g., `m/44'/QFS'/...`).
- Ensure `seed` is sourced from a master secret (simulated in Dev, HSM-bound in Prod).

## 2. PQC Provider Interface (Stage 2)

**Current State (`v13/libs/pqc_provider.py`):**

- Interface: `generate_keypair(seed)` (No algo ID).
- Implementation: `DeterministicMockProvider` (HMAC). `RealProvider` is a stub.

**Gap:**

- Missing `algo_id` parameter in `generate_keypair`, `sign`, `verify`.
- `RealProvider` implementation missing (liboqs bindings).
- No concept of `priv_handle` (currently returns raw bytes).

**Remediation:**

- Update `IPQCProvider` signature: `generate_keypair(seed, algo_id)`.
- Introduce `PrivKeyHandle` type (alias for `bytes` in Mock, potentially an object/ID in Real).
- Implement `RealProvider` using `liboqs-python` (conditional dependency).

## 3. Device-Bound Sessions (Stage 3)

**Current State (`v13/core/DRV_Packet.py`):**

- `DRV_Packet` contains `ttsTimestamp`, `sequence`, `seed`.
- No `device_id` or session binding fields.

**Gap:**

- No "Device ID" concept in the packet structure.
- No session token logic (Session = Wallet Identity currently).

**Remediation:**

- Extend `DRV_Packet` or create `SessionPacket` with `device_id`.
- Implement `v13/services/session` to handle Challenge-Response flows.

## 4. Subsystem Wiring (Stage 4)

**Current State:**

- `System Creator` uses `derivation.py`.
- `DRV_Packet` uses `pqc_provider` directly.

**Gap:**

- Everything assumes the "Current State" derivation logic.
- Rewiring required once `derivation.py` becomes HD-compliant.

## Recommendations for Execution

1. **Step 1:** Update `pqc_provider.py` interface FIRST (add `algo_id`, `priv_handle`). this is low-risk refactoring.
2. **Step 2:** Refactor `derivation.py` to support "Stage 1" HD paths.
3. **Step 3:** Introduce `RealProvider` (can still be mocked on Windows, but functional structure).
4. **Step 4:** Implement `SessionManager` (Stage 3).

## Zero-Sim Impact

- **Positive:** Moving to "Real" PQC libs doesn't break Zero-Sim as long as the *seeding* remains deterministic. Liboqs supports deterministic seeding.
- **Risk:** Hardware binding introduces "External State". We must mock the "Hardware Device" for replay tests.
