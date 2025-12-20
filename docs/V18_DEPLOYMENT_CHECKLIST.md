# V18 Deployment Checklist

## Pre-Deployment

- [ ] **Environment Variables**:
  - Ensure `QFS_FORCE_MOCK_PQC` is set to `0` (Off) for production (requires real PQC libs).
  - Set `SECRET_KEY` and `JWT_ALGORITHM` securely.
  - Configure `ALLOWED_ORIGINS` for CORS (restrict to production frontend domain).
- [ ] **Database/Ledger**:
  - Verify `RealLedger` connection strings.
  - Ensure persistence layer (e.g., PostgreSQL or File Store) is writable.

## Application Server (FastAPI)

- [ ] **Process Manager**:
  - Switch from `uvicorn --reload` to a production ASGI manager (e.g., `gunicorn` with `uvicorn.workers.UvicornWorker`).
  - Example: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main_minimal:app`
- [ ] **Security**:
  - Enable HTTPS (TLS Termination at Nginx/Load Balancer).
  - Set Secure, HttpOnly, SameSite cookies for sessions if used.
- [ ] **Health Checks**:
  - `/health`: Low-cost liveness probe (Process up?).
  - `/readiness`: Deep check (DB connected? Peers connected?).

## Frontend (Next.js)

- [ ] **Build**:
  - Run `npm run build` to generate optimized production artifacts.
  - Ensure `npm run start` is used instead of `dev`.
- [ ] **Environment**:
  - `NEXT_PUBLIC_API_URL` should point to the production backend.

## Validation

- [ ] **Smoke Test**: Run `npm run test:e2e` against the staging/production URL.
- [ ] **Auth Check**: Verify wallet login on production build.
