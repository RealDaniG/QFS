# Milestone: MFA Hardening Complete (v20)

**Objective:** Enrich sessions with MFA/device trust, lock Electron IPC, and freeze v20 schemas/authority doctrine.

## Features

- **Schema Freeze:** v1 session/event schemas.
- **Device Binding v1:** Deterministic device hash + refresh token binding.
- **MFAService:** TOTP capability and `mfa_level`.
- **IPC Hardening:** Minimal, signed IPC surface.

## Verification

- [ ] Device mismatch emits event.
- [ ] No sensitive data in renderer.
- [ ] Zero-Sim compliance for all auth flows.
