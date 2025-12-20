# ATLAS v18 Backend API - Implementation Complete

**Date:** 2025-12-20  
**Status:** Ready for Testing  
**Objective:** Connect ATLAS UI to v18 distributed backend

---

## ✅ Backend API Routes Implemented

### 1. Auth Routes (`/auth`) - Existing, v18 Compatible

**File:** `v13/atlas/src/api/routes/auth.py`

**Endpoints:**

- `GET /auth/nonce` - Get nonce for EIP-191 signing
- `POST /auth/login` - Verify signature, issue Ascon session token
- `POST /auth/logout` - Revoke session

**Integration:**

- ✅ Uses `SessionManager` (v18.6 stateless Ascon tokens)
- ✅ EIP-191 signature verification
- ✅ Returns session token + wallet address + expiry

### 2. Governance Routes v18 (`/api/v18/governance`) - NEW

**File:** `v13/atlas/src/api/routes/governance_v18.py`

**Endpoints:**

- `POST /api/v18/governance/proposals` - Create proposal (ClusterAdapter)
- `POST /api/v18/governance/proposals/{id}/vote` - Cast vote (ClusterAdapter)
- `GET /api/v18/governance/proposals` - List proposals
- `GET /api/v18/governance/proposals/{id}` - Get proposal details
- `GET /api/v18/governance/cluster/status` - Cluster health

**Integration:**

- ✅ Uses `V18ClusterAdapter` for distributed writes
- ✅ Requires wallet authentication (`get_current_wallet`)
- ✅ Returns `TxResult` with evidence event IDs
- ⏳ Queries return mock data (projections not yet implemented)

### 3. Content Routes v18 (`/api/v18/content`) - NEW

**File:** `v13/atlas/src/api/routes/content_v18.py`

**Endpoints:**

- `POST /api/v18/content/publish` - Publish message/post (ClusterAdapter)
- `GET /api/v18/content/feed` - Get content feed
- `GET /api/v18/content/messages/{id}` - Get specific message
- `POST /api/v18/content/messages/{id}/react` - Add reaction

**Integration:**

- ✅ Uses `V18ClusterAdapter` for chat writes
- ✅ Content hash anchoring (Class A/B separation)
- ✅ Requires wallet authentication
- ⏳ Queries return mock data (projections not yet implemented)

---

## Dependencies & Authentication

### Session Management

**File:** `v13/atlas/src/api/dependencies.py`

**Added:**

- `get_current_wallet(token)` - Extracts wallet from Ascon session

**Existing:**

- `session_manager` - Singleton SessionManager instance
- `get_current_session(token)` - Validates session
- `get_current_user(token)` - Gets user object

### ClusterAdapter Initialization

**In Route Files:**

```python
cluster_adapter = V18ClusterAdapter(
    node_endpoints=[
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003"
    ],
    timeout_seconds=10
)
```

---

## API Package Integration

**File:** `v13/atlas/src/api/__init__.py`

**Updated:**

- Added `governance_v18` router
- Added `content_v18` router
- Both included in `api_routes` list
- Automatically mounted to main FastAPI app

---

## How to Start the Backend

### Option 1: Direct Uvicorn

```bash
cd v13/atlas
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Option 2: Python Module

```bash
python -m v13.atlas.src.main
```

### Option 3: Using Launcher (after backend wiring)

```bash
.\atlas_launch.bat
```

---

## API Documentation

Once running, access:

- **Swagger UI:** <http://localhost:8001/api/docs>
- **ReDoc:** <http://localhost:8001/api/redoc>
- **Health Check:** <http://localhost:8001/health>

---

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8001/health
```

Expected:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "ATLAS Quantum Financial System"
}
```

### 2. Get Nonce

```bash
curl http://localhost:8001/auth/nonce
```

Expected:

```json
{
  "nonce": "abc123..."
}
```

### 3. Login (requires MetaMask signature)

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "nonce": "abc123...",
    "signature": "0x...",
    "wallet_address": "0xABC123..."
  }'
```

Expected:

```json
{
  "session_token": "ascon1.ey...",
  "wallet_address": "0xABC123...",
  "expires_at": 1703005234.5
}
```

### 4. Create Proposal (authenticated)

```bash
curl -X POST http://localhost:8001/api/v18/governance/proposals \
  -H "Authorization: Bearer ascon1.ey..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Proposal",
    "description": "Testing v18 integration",
    "proposal_type": "general"
  }'
```

Expected:

```json
{
  "proposal_id": "evt_...",
  "committed": true,
  "evidence_event_ids": ["evt_..."],
  "leader_term": 1,
  "leader_node_id": "node-a",
  "commit_index": 10
}
```

---

## Frontend Integration Status

### useWalletAuth Hook

**File:** `v13/atlas/src/hooks/useWalletAuth.ts`

**Next Steps:**

1. Update `login()` to call `/auth/nonce` then `/auth/login`
2. Store returned `session_token` in localStorage
3. Test wallet connect flow in UI

### Governance Service  

**File:** `v13/atlas/src/lib/governance/service.ts`

**Next Steps:**

1. Update `createProposal()` to call `/api/v18/governance/proposals`
2. Update `getProposals()` to call `/api/v18/governance/proposals`
3. Test proposal creation in UI

### Content Publisher

**File:** `v13/atlas/src/lib/content/publisher.ts`

**Next Steps:**

1. Update `publish()` to call `/api/v18/content/publish`
2. Update `getFeed()` to call `/api/v18/content/feed`
3. Test message posting in UI

---

## Current Limitations

### Read Path (Projections)

- Governance list/details return mock data
- Content feed returns mock data
- Need to implement projection database queries

### Write Path (Cluster)

- Requires 3-node cluster to be running
- ClusterAdapter will fail if nodes unavailable
- Fallback to mock mode not implemented

### Session Storage

- Frontend currently uses localStorage
- No global auth expiry listener yet
- No automatic token refresh

---

## Next Immediate Actions

1. **Start Backend:** `uvicorn src.main:app --reload --port 8001`
2. **Test Health:** `curl http://localhost:8001/health`
3. **Check Swagger:** <http://localhost:8001/api/docs>
4. **Wire Frontend Hooks:** Update useWalletAuth, governance service
5. **Test E2E:** Login → Create Proposal → Verify in UI

---

## Success Criteria

**Minimum Viable:**

- ✅ Backend starts without errors
- ✅ Auth endpoints respond  
- ✅ v18 routes accessible in Swagger
- ⏳ Frontend can call auth/login
- ⏳ Frontend can create proposal
- ⏳ Proposal shows in UI

**Full Integration:**

- ⏳ 3-node cluster running
- ⏳ ClusterAdapter submits to real Raft
- ⏳ EvidenceBus events logged
- ⏳ Projections query real data
- ⏳ E2E test automated

---

**Status:** Backend API implementation complete. Ready to start server and wire frontend!

**Estimated Time to Working E2E:** 1-2 hours (start backend + wire frontend hooks)
