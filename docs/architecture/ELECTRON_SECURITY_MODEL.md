# Electron Security Model

## Principles

1. **Renderer is Untrusted:** Treat the UI like a remote web client.
2. **Secrets Stay in Main:** Private keys, refresh tokens never leave the main process.
3. **IPC is the API:** Minimal, schema-validated message passing.

## Configuration

- **contextIsolation:** `true` (Mandatory).
- **nodeIntegration:** `false` (Mandatory).
- **remote:** `disabled`.

## Secure IPC Contract

- `auth:getSession` -> Returns metadata/access token.
- `auth:refresh` -> Triggers internal refresh, returns new access token.
- `auth:biometricUnlock` -> Triggers OS prompt, decrypts secrets in memory.

## Storage

- **Tokens:** OS Keychain (safeStorage).
- **Session:** In-memory (Main process).
