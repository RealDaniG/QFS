# Security Debt (V18 Minimal)

This document tracks intentional security trade-offs made to achieve the V18 Minimum Viable Integration. These must be addressed before public production release.

## High Criticality

- [ ] **CORS Configuration**:
  - **Current**: `allow_origins=["*"]` in `src/main_minimal.py`.
  - **Risk**: Allows any site to make requests to the API.
  - **Fix**: Restrict to specific frontend domains (e.g., `https://atlas.qfs.network`).
- [ ] **Auth Token Storage**:
  - **Current**: `localStorage` (via `api.ts`).
  - **Risk**: Vulnerable to XSS attacks.
  - **Fix**: Switch to `SameSite=Strict` HttpOnly cookies for session tokens.
- [ ] **JWT Signing Key**:
  - **Current**: Likely hardcoded or default in dev env.
  - **Risk**: Token forgery.
  - **Fix**: Rotate keys and load from secure Vault/Env.

## Medium Criticality

- [ ] **PQC Signatures**:
  - **Current**: `QFS_FORCE_MOCK_PQC=1` uses mock crypto.
  - **Risk**: No quantum resistance; signatures are fake.
  - **Fix**: Enable `liboqs` bindings in production build.
- [ ] **Rate Limiting**:
  - **Current**: None implemented in minimal backend.
  - **Risk**: DoS vulnerability.
  - **Fix**: Implement Redis-backed rate limiter on API Gateway.
- [ ] **Input Validation**:
  - **Current**: Basic Pydantic validation.
  - **Risk**: Potential data integrity issues.
  - **Fix**: Audit all user inputs (governance proposals, content) for sanitization.
