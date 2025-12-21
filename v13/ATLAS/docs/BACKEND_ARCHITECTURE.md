
# ATLAS v18 Backend Architecture

## Overview

The ATLAS v18 backend has been refactored into a modular, production-ready architecture using FastAPI. It separates concerns between configuration, API routes, and core business logic, ensuring testability and scalability.

## Directory Structure

```
src/
├── main_minimal.py       # Application Entry Point
├── config.py             # Environment Configuration (Pydantic)
├── api/
│   ├── dependencies.py   # Auth Middleware & Session Management
│   ├── models.py         # Pydantic Schemas for Requests/Responses
│   └── routes/           # REST API Endpoints
│       ├── auth.py       # Challenge-Response Authentication
│       ├── rewards.py    # Daily Reward Logic
│       ├── wallet.py     # Wallet Balance & History
│       ├── spaces.py     # Social Spaces
│       ├── chat.py       # Secure Messaging
│       ├── governance.py # Proposals & Voting
│       ├── content.py    # Feed & Discovery
│       ├── ledger.py     # Immutable Ledger Events
│       └── general.py    # Discovery & Bounties
└── lib/
    ├── cycles.py         # Pure Domain Logic for Rewards
    └── storage.py        # Persistence Layer Abstraction
```

## Key Patterns

1. **Dependency Injection**: Auth and database sessions are injected via `Depends` (see `src/api/dependencies.py`).
2. **Configuration**: All environment variables are managed in `src/config.py` using `pydantic-settings`.
3. **Pure Logic**: Business logic (e.g., reward calculation in `cycles.py`) is separated from IO, making it unit-testable.
4. **Structured Logging**: Production logs are output in JSON format for observability.

## Deployment

### Docker

```bash
docker build -t atlas-backend:v18 .
docker run -p 8000:8000 --env-file .env atlas-backend:v18
```

### Systemd

Copy `atlas-v18.service` to `/etc/systemd/system/`, reload daemon, and start service.

```bash
sudo cp atlas-v18.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now atlas-v18
```

## Testing

Run the test suite using `pytest`:

```bash
python -m pytest tests/
```
