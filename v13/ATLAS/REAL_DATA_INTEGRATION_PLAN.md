# ATLAS v18 - Real Data Integration Plan

**Date:** December 20, 2025  
**Status:** IMPLEMENTATION ROADMAP  
**Priority:** P1 - POST-ALPHA ENHANCEMENT

---

## 🎯 OBJECTIVE

Replace all mock/placeholder data with real backend-connected data across the entire ATLAS v18 Dashboard.

---

## 📋 CURRENT STATE ASSESSMENT

### ✅ Already Connected (Working)

1. **Wallet Authentication** - Real MetaMask connection (via mock API routes)
2. **Session Management** - Real localStorage persistence
3. **Auth State** - Real Zustand store

### ⏳ Using Mock Data (Needs Backend)

1. **System Health** - Hardcoded values
2. **QFS Node Network** - Static node list
3. **Feed Content** - Mock posts
4. **Notifications** - Static notifications
5. **Bounties** - Placeholder text
6. **Wallet Balance** - Mock FLX amount
7. **Transaction History** - No data
8. **Messaging** - Mock conversations
9. **Discovery/Communities** - Mock data
10. **Reward Explanations** - Mock calculations
11. **Profile/Settings** - No persistence

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Backend API Routes (Priority: HIGH)

**Goal:** Create all required API endpoints

#### 1.1 Notifications API

**File:** `src/app/api/v18/notifications/route.ts`

```typescript
export async function GET(request: Request) {
  // Get user from session
  const session = await getSession(request);
  
  // Fetch from backend or database
  const notifications = await fetchNotifications(session.wallet_address);
  
  return NextResponse.json(notifications);
}

export async function POST(request: Request) {
  // Mark notifications as read
  const { notificationIds } = await request.json();
  await markAsRead(notificationIds);
  return NextResponse.json({ success: true });
}
```

#### 1.2 Feed API

**File:** `src/app/api/v18/content/feed/route.ts`

```typescript
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = searchParams.get('limit') || '20';
  
  // Fetch real feed from backend
  const feed = await fetchFeedFromBackend(limit);
  
  return NextResponse.json(feed);
}
```

#### 1.3 System Health API

**File:** `src/app/api/v18/system/health/route.ts`

```typescript
export async function GET() {
  const health = {
    qfsStatus: await checkQFSStatus(),
    coherenceRanking: await getCoherenceStatus(),
    guardSystem: await getGuardSystemStatus(),
    ledgerSync: await getLedgerSyncStatus(),
    nodeHealth: await getNodeHealthPercentage()
  };
  
  return NextResponse.json(health);
}
```

#### 1.4 Wallet Balance API

**File:** `src/app/api/v18/wallet/balance/route.ts`

```typescript
export async function GET(request: Request) {
  const session = await getSession(request);
  const balance = await fetchBalanceFromBackend(session.wallet_address);
  
  return NextResponse.json({
    balance: balance.total,
    rewards: balance.rewards,
    staked: balance.staked
  });
}
```

#### 1.5 Bounties API

**File:** `src/app/api/v18/bounties/route.ts`

```typescript
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filter = searchParams.get('filter'); // 'all' or 'mine'
  
  const session = await getSession(request);
  const bounties = await fetchBounties(filter, session?.wallet_address);
  
  return NextResponse.json(bounties);
}
```

---

### Phase 2: Update Frontend Components (Priority: HIGH)

**Goal:** Replace mock data with API calls

#### 2.1 Notifications

**File:** `src/components/NotificationPanel.tsx`

**Current:**

```typescript
const MOCK_NOTIFICATIONS: Notification[] = [...]
const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);
```

**Updated:**

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

export function NotificationPanel() {
  const { data: notifications = [], refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await fetch('/api/v18/notifications');
      return res.json();
    },
    refetchInterval: 30000 // Poll every 30 seconds
  });
  
  const markReadMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      await fetch('/api/v18/notifications', {
        method: 'POST',
        body: JSON.stringify({ notificationIds: ids })
      });
    },
    onSuccess: () => refetch()
  });
  
  // ... rest of component
}
```

#### 2.2 System Health

**File:** `src/app/page.tsx`

**Current:**

```typescript
const systemHealth = {
  qfsStatus: 'Operational',
  // ... hardcoded values
};
```

**Updated:**

```typescript
const { data: systemHealth } = useQuery({
  queryKey: ['systemHealth'],
  queryFn: async () => {
    const res = await fetch('/api/v18/system/health');
    return res.json();
  },
  refetchInterval: 10000, // Poll every 10 seconds
  initialData: {
    qfsStatus: 'Loading...',
    coherenceRanking: 'Loading...',
    guardSystem: 'Loading...',
    ledgerSync: 'Loading...',
    nodeHealth: '—'
  }
});
```

#### 2.3 Feed Content

**File:** `src/hooks/useQFSFeed.ts`

Already has API call structure, just needs backend to respond with real data.

#### 2.4 Wallet Balance

**File:** `src/hooks/useTreasury.ts`

Already structured correctly, just needs real backend endpoint.

---

### Phase 3: Settings & Profile Persistence (Priority: MEDIUM)

**Goal:** Save user preferences and profile data

#### 3.1 Profile API

**File:** `src/app/api/v18/profile/route.ts`

```typescript
export async function GET(request: Request) {
  const session = await getSession(request);
  const profile = await fetchProfile(session.wallet_address);
  return NextResponse.json(profile);
}

export async function PUT(request: Request) {
  const session = await getSession(request);
  const updates = await request.json();
  await updateProfile(session.wallet_address, updates);
  return NextResponse.json({ success: true });
}
```

#### 3.2 Guards Configuration API

**File:** `src/app/api/v18/guards/route.ts`

```typescript
export async function GET(request: Request) {
  const session = await getSession(request);
  const guards = await fetchGuards(session.wallet_address);
  return NextResponse.json(guards);
}

export async function POST(request: Request) {
  const session = await getSession(request);
  const { guardConfig } = await request.json();
  await updateGuards(session.wallet_address, guardConfig);
  return NextResponse.json({ success: true });
}
```

---

### Phase 4: Messaging & Discovery (Priority: MEDIUM)

**Goal:** Real-time messaging and community discovery

#### 4.1 Messages API

**File:** `src/app/api/v18/messages/route.ts`

```typescript
export async function GET(request: Request) {
  const session = await getSession(request);
  const messages = await fetchMessages(session.wallet_address);
  return NextResponse.json(messages);
}

export async function POST(request: Request) {
  const session = await getSession(request);
  const { recipient, content } = await request.json();
  const message = await sendMessage(session.wallet_address, recipient, content);
  return NextResponse.json(message);
}
```

#### 4.2 Communities API

**File:** `src/app/api/v18/communities/route.ts`

```typescript
export async function GET() {
  const communities = await fetchCommunities();
  return NextResponse.json(communities);
}

export async function POST(request: Request) {
  const session = await getSession(request);
  const { communityId, action } = await request.json();
  
  if (action === 'join') {
    await joinCommunity(session.wallet_address, communityId);
  }
  
  return NextResponse.json({ success: true });
}
```

---

### Phase 5: Content Publishing (Priority: HIGH)

**Goal:** Real content creation and publishing

#### 5.1 Publish API

**File:** `src/app/api/v18/content/publish/route.ts`

```typescript
export async function POST(request: Request) {
  const session = await getSession(request);
  const { content, tags, visibility } = await request.json();
  
  // Create content on backend
  const result = await publishContent({
    author: session.wallet_address,
    content,
    tags,
    visibility
  });
  
  return NextResponse.json(result);
}
```

#### 5.2 Update ContentComposer

**File:** `src/hooks/useContentPublisher.ts`

Already structured correctly, just needs real backend endpoint.

---

## 🔄 IMPLEMENTATION SEQUENCE

### Week 1: Core Functionality

- [ ] Day 1: Create all API route files
- [ ] Day 2: Implement notifications API + update component
- [ ] Day 3: Implement system health API + update component
- [ ] Day 4: Implement feed API (already mostly done)
- [ ] Day 5: Implement wallet balance API + update component

### Week 2: User Features

- [ ] Day 1: Implement profile API + update settings
- [ ] Day 2: Implement guards API + update settings
- [ ] Day 3: Implement bounties API + update component
- [ ] Day 4: Implement messaging API + update component
- [ ] Day 5: Implement communities API + update discovery

### Week 3: Content & Polish

- [ ] Day 1: Implement publish API + test flow
- [ ] Day 2: Add loading states everywhere
- [ ] Day 3: Add error handling everywhere
- [ ] Day 4: Add optimistic updates
- [ ] Day 5: Testing & bug fixes

---

## 🛠️ HELPER UTILITIES NEEDED

### Session Management

**File:** `src/lib/session.ts`

```typescript
export async function getSession(request: Request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader) return null;
  
  const token = authHeader.replace('Bearer ', '');
  // Validate token and return session data
  return validateToken(token);
}
```

### Backend Proxy

**File:** `src/lib/backendProxy.ts`

```typescript
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function proxyToBackend(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${BACKEND_URL}${endpoint}`, options);
  return response.json();
}
```

---

## 📊 PROGRESS TRACKING

### API Endpoints Created

- [x] `/api/v18/auth/nonce` - Mock (working)
- [x] `/api/v18/auth/verify` - Mock (working)
- [ ] `/api/v18/notifications` - TODO
- [ ] `/api/v18/system/health` - TODO
- [ ] `/api/v18/content/feed` - Exists but needs backend
- [ ] `/api/v18/wallet/balance` - TODO
- [ ] `/api/v18/bounties` - TODO
- [ ] `/api/v18/profile` - TODO
- [ ] `/api/v18/guards` - TODO
- [ ] `/api/v18/messages` - TODO
- [ ] `/api/v18/communities` - TODO
- [ ] `/api/v18/content/publish` - TODO

### Components Updated

- [ ] NotificationPanel - TODO
- [ ] SystemHealth (page.tsx) - TODO
- [ ] DistributedFeed - Partial (has API call structure)
- [ ] WalletInterface - Partial (has API call structure)
- [ ] BountyDashboard - TODO
- [ ] ProfileEditor - TODO
- [ ] GuardsList - TODO
- [ ] MessagingInterface - TODO
- [ ] DiscoveryInterface - TODO
- [ ] ContentComposer - Partial (has publish logic)

---

## 🎯 SUCCESS CRITERIA

### Must Have (Alpha Release)

- [x] Wallet connection works
- [ ] Notifications load from backend
- [ ] System health shows real status
- [ ] Feed shows real content
- [ ] Wallet shows real balance
- [ ] Publishing creates real content

### Should Have (Beta Release)

- [ ] Bounties load from database
- [ ] Profile saves to backend
- [ ] Guards configuration persists
- [ ] Messaging works end-to-end
- [ ] Communities are discoverable

### Nice to Have (v1.0 Release)

- [ ] Real-time updates via WebSocket
- [ ] Optimistic UI updates
- [ ] Offline support
- [ ] Advanced caching strategies

---

## 🚀 QUICK START

To begin implementation:

1. **Start with Notifications** (easiest, high impact)

   ```bash
   # Create the API route
   mkdir -p src/app/api/v18/notifications
   # Implement GET and POST handlers
   # Update NotificationPanel component
   # Test in browser
   ```

2. **Then System Health** (visible, important)

   ```bash
   # Create the API route
   mkdir -p src/app/api/v18/system
   # Implement health check
   # Update page.tsx
   # See real-time status
   ```

3. **Then Feed & Publishing** (core functionality)

   ```bash
   # Feed API already exists, just needs backend
   # Create publish API
   # Test full content creation flow
   ```

---

**Status:** Ready to begin implementation. All components identified, plan documented, sequence defined.

**Next Step:** Create notification API route and update NotificationPanel component.
