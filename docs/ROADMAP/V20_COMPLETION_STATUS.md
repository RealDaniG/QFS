# v20 Completion Status (ALPHA V15.5)

**Status:** Active Development
**Target:** Finalize v20 without contaminating replay, making v21 an extension.

## Completed Features

- **AuthService Facade:** Single orchestration boundary established.
- **Session Model:** Deterministic `session_id`, `device_id` placeholders.
- **EvidenceBus Integration:** `SESSION_CREATED`, `SESSION_REFRESHED`, `SESSION_REVOKED` events.

## Remaining v20 Tasks (Prioritized)

### 1. Schema & Authority Freezing (High)

- [ ] Add `session_schema_version = 1`.
- [ ] Add `auth_event_version = 1`.
- [ ] Document authority hierarchy (Levels 0-2).

### 2. Device Binding v1 (High)

- [ ] Implement `computeDeviceHash()` (Deterministic).
- [ ] Bind refresh tokens to device.
- [ ] Emit `DEVICE_MISMATCH` events.

### 3. MOCKPQC Slot Finalization (High)

- [ ] Complete `MockPQCKey` storage.
- [ ] Wire MOCKPQC subject into Session.
- [ ] Implement stub signature generation.

### 4. MFAService Capability (Medium)

- [ ] Implement TOTP secret derivation.
- [ ] Add `mfa_level` to Session.
- [ ] Log MFA events.

### 5. Electron IPC Hardening (High)

- [ ] `contextIsolation: true`, `nodeIntegration: false`.
- [ ] Minimal IPC surface (`auth:getSession`, etc.).
- [ ] Sign sensitive IPC payloads.

### 6. Biometric Unlock (Optional/Low)

- [ ] OS biometric integration.
- [ ] `BIOMETRIC_UNLOCK` event emission.

### 7. Deferred Features Documentation (Medium)

- [ ] Explicit flags to disable offline queue/Raft.
- [ ] Ensure V21 features are not partially active.
