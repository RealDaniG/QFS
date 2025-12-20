# ATLAS v18.9 Integration Roadmap

> **Status:** Frontend Ready, Backend Wiring Needed  
> **Date:** 2025-12-20  
> **Goal:** Connect ATLAS UI to v18 distributed backend

## Current Achievement Summary

### ✅ Completed (P0 Blockers Resolved)

**v18.6 Auth Sync:**

- Stateless Ascon session tokens implemented
- Multi-node validation working (12/12 tests passing)
- Session manager refactored for zero server-side state
- atlasFetch utility with auth headers ready

**v18.7 ClusterAdapter:**

- Full implementation with leader discovery
- Retry logic and error handling
- 15/15 tests passing on first run
- PoE logging for all cluster operations

**Frontend Scaffold:**

- ATLAS UI running on localhost:3000
- 10 library files created (utils, ledger, governance, content, etc.)
- `.env.local` configured for backend URLs
- Beautiful UI with Tailwind + Next.js 15

**Documentation:**

- 7 comprehensive docs (Auth Sync, ClusterAdapter Spec, Launch Guide)
- Updated CHANGELOG, README, task tracker
- All code committed and pushed to GitHub

---

## Next Phase: Backend Integration

### Step 1: Start Backend API Server

**Option A: FastAPI Server (v13/atlas/src/main.py)**

```bash
cd v13/atlas
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

**Option B: v18 Cluster Mode (future)**

```bash
# Once cluster nodes are implemented
python -m v18.consensus.state_machine --node-id=node-a --port=8001
```

**Verify:**

```bash
curl http://localhost:8001/health
curl http://localhost:8001/api/docs  # Swagger UI
```

### Step 2: Wire Backend Endpoints

**Required API Endpoints:**

**Auth:**

- `POST /api/auth/login` - EIP-191 wallet login → Ascon session token
- `POST /api/auth/logout` - Session invalidation
- `GET /api/auth/me` - Current user info

**Governance:**

- `GET /api/governance/proposals` - List proposals
- `POST /api/governance/proposals` - Create proposal (via ClusterAdapter)
- `POST /api/governance/votes` - Cast vote (via ClusterAdapter)

**Ledger:**

- `GET /api/ledger/timeline` - Global activity feed
- `GET /api/ledger/user/{wallet}` - User transaction history
- `GET /api/ledger/balance/{wallet}` - Token balances

**Chat/Content:**

- `POST /api/content/publish` - Publish message/post
- `GET /api/content/feed` - Get content feed

### Step 3: Update Frontend Library Files

**Priority Order:**

**1. `lib/api.ts`** (✅ Done)

- Base URL resolution from env vars
- Auth header attachment
- 401 handling

**2. `hooks/useWalletAuth.ts`** (Needs Update)

```typescript
// Call real backend for login
const login = async () => {
  const response = await atlasFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ wallet, signature }),
  });
  
  const { session_token } = await response.json();
  localStorage.setItem(SESSION_KEY, JSON.stringify({ session_token, wallet }));
};
```

**3. `lib/governance/service.ts`** (Needs Update)

```typescript
async createProposal(title: string, description: string, creator: string): Promise<string> {
  const response = await atlasFetch('/api/governance/proposals', {
    method: 'POST',
    body: JSON.stringify({ title, description, creator }),
  });
  
  const result = await response.json();
  return result.proposal_id;
}
```

**4. `lib/ledger/real-ledger.ts`** (Needs Update)

```typescript
async getBalance(wallet: string): Promise<number> {
  const response = await atlasFetch(`/api/ledger/balance/${wallet}`);
  const data = await response.json();
  return data.balance;
}
```

**5. `lib/content/publisher.ts`** (Needs Update)

```typescript
async publish(content: string, author: string, options: PublishOptions): Promise<PublishResult> {
  const response = await atlasFetch('/api/content/publish', {
    method: 'POST',
    body: JSON.stringify({ content, author, ...options }),
  });
  
  return await response.json();
}
```

### Step 4: Backend Implementation (Python)

**Create API Routes (if not exist):**

**`v13/atlas/src/api/routes/auth.py`:**

```python
from fastapi import APIRouter, HTTPException
from v15.auth.session_manager import session_manager

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(wallet: str, signature: str):
    # Verify EIP-191 signature
    # Create Ascon session
    session_token = session_manager.create_session(
        wallet_address=wallet,
        scopes=["read", "write"],
        ttl_seconds=3600
    )
    
    return {"session_token": session_token}
```

**`v13/atlas/src/api/routes/governance.py`:**

```python
from fastapi import APIRouter, Depends
from v18.cluster import V18ClusterAdapter, GovernanceCommand

router = APIRouter(prefix="/api/governance", tags=["governance"])
cluster = V18ClusterAdapter(node_endpoints=["http://localhost:8001"])

@router.post("/proposals")
async def create_proposal(title: str, description: str, creator: str):
    cmd = GovernanceCommand(
        action_type="create_proposal",
        wallet_address=creator,
        proposal_data={"title": title, "description": description}
    )
    
    result = cluster.submit_governance_action(cmd)
    
    if not result.committed:
        raise HTTPException(500, result.error_message)
    
    return {
        "proposal_id": result.evidence_event_ids[0],
        "committed": True,
        "event_ids": result.evidence_event_ids
    }
```

---

## Testing Checklist

### Backend Tests

- [ ] `pytest v18/tests/test_ascon_sessions.py` - All green
- [ ] `pytest v18/tests/test_cluster_adapter.py` - All green
- [ ] `curl http://localhost:8001/health` - Responds 200
- [ ] `curl http://localhost:8001/api/auth/login -X POST` - Returns session token

### Frontend Tests

- [ ] Navigate to `http://localhost:3000` - Page loads
- [ ] Click "Connect Wallet" - MetaMask prompts
- [ ] Sign EIP-191 message - Session token received
- [ ] Create proposal - Appears in governance list
- [ ] Post message - Persists after refresh
- [ ] Check DevTools → Network - Auth headers present

### Integration Tests

- [ ] Login flow: Wallet → Signature → Ascon token → Stored
- [ ] Write flow: Create proposal → ClusterAdapter → EvidenceBus event
- [ ] Read flow: Query ledger → Real data from projections
- [ ] Auth expiry: 401 response → Clear session → Prompt reconnect

---

## File-Level Action Plan

### Backend Files to Create/Update

1. **`v13/atlas/src/api/routes/auth.py`** - Auth endpoints with Ascon
2. **`v13/atlas/src/api/routes/governance.py`** - Governance with ClusterAdapter
3. **`v13/atlas/src/api/routes/ledger.py`** - Ledger query endpoints
4. **`v13/atlas/src/api/routes/content.py`** - Content publishing
5. **`v13/atlas/src/api/dependencies.py`** - Update to use V18ClusterAdapter
6. **`v13/atlas/src/main.py`** - Include new routers

### Frontend Files to Update

1. **`v13/atlas/src/hooks/useWalletAuth.ts`** ⭐ (Priority 1)
   - Call `/api/auth/login` with real signature
   - Store Ascon token correctly

2. **`v13/atlas/src/lib/governance/service.ts`** ⭐ (Priority 2)
   - Replace stubs with atlasFetch calls

3. **`v13/atlas/src/lib/ledger/real-ledger.ts`** (Priority 3)
   - Implement real API calls for balance/history

4. **`v13/atlas/src/lib/content/publisher.ts`** (Priority 4)
   - Wire to `/api/content/publish`

5. **`v13/atlas/src/app/providers.tsx`** (Create if needed)
   - Add QueryClientProvider for React Query
   - Add auth expiry listener

---

## Quick Start Commands

### Terminal 1: Backend

```bash
cd d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Terminal 2: Frontend

```bash
cd d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas
npm run dev
```

### Terminal 3: Tests

```bash
cd d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13
pytest v18/tests/ -v
```

---

## Success Criteria

**Minimum Viable Integration:**
✅ User can connect wallet in UI
✅ User can create a proposal
✅ Proposal appears in governance list
✅ Proposal persists across page refresh
✅ All data flows through v18 backend (no mocks)

**Full Integration:**
✅ Auth: EIP-191 → Ascon token → Authenticated requests
✅ Writes: Governance/bounty/chat → ClusterAdapter → EvidenceBus
✅ Reads: Ledger queries → Projections → UI display
✅ PoE: All operations logged and traceable
✅ Tests: E2E wallet flow fully automated

---

## Current Gaps

1. **Backend API Routes:** Need to create governance/ledger/content routers
2. **ClusterAdapter Wiring:** Backend needs to instantiate V18ClusterAdapter
3. **Frontend Hooks:** useWalletAuth needs real API integration
4. **Session Provider:** QueryClientProvider for React Query
5. **E2E Tests:** Automated wallet→proposal→verify flow

---

**Next Immediate Action:** Start backend server and begin wiring authentication endpoints.

**Estimated Time to Working Integration:** 2-4 hours of focused development.

---

**Maintained by:** QFS × ATLAS Core Team  
**Last Updated:** 2025-12-20
