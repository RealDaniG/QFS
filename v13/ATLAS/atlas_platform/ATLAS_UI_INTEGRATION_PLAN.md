# ATLAS UI Integration Plan - P0 Features

**Version:** 1.0  
**Date:** 2025-12-15  
**Priority:** P0 (Highest Leverage)

## Executive Summary

Wire the completed P0 backend (DM, Explain-This, Communities, Appeals, Onboarding) into the ATLAS frontend with progressive disclosure patterns that make governance, explainability, and onboarding **tangible** for users.

---

## Phase 1: Wire P0 APIs into ATLAS Frontend

### 1.1 API Client Layer

**File:** `src/lib/p0-api-client.ts`

Create a unified client for all P0 services:

```typescript
// P0 API Client
export class P0ApiClient {
  constructor(private baseUrl: string, private capabilities: string[]) {}

  // Direct Messaging
  async dm_createThread(recipientId: string): Promise<Thread>
  async dm_sendMessage(threadId: string, content: string): Promise<Message>
  async dm_listThreads(): Promise<Thread[]>
  async dm_getHistory(threadId: string): Promise<Message[]>

  // Explain-This
  async explain(entityType: string, entityId: string): Promise<Explanation>
  async explainBatch(targets: ExplainTarget[]): Promise<Explanation[]>
  async explainTree(entityId: string, depth: number): Promise<ExplanationTree>

  // Communities
  async guild_create(manifest: GuildManifest): Promise<Guild>
  async guild_join(guildId: string): Promise<MembershipResult>
  async guild_list(): Promise<Guild[]>

  // Appeals
  async appeal_submit(targetEventId: string, evidence: string): Promise<Appeal>
  async appeal_status(appealId: string): Promise<AppealStatus>

  // Onboarding
  async tour_start(tourId: string): Promise<TourProgress>
  async tour_completeStep(tourId: string, stepId: string): Promise<TourStepResult>
}
```

**Capability-Aware Calls:**

```typescript
// Before calling, check if user has capability
if (!this.capabilities.includes('DM_SEND')) {
  throw new CapabilityError('Missing DM_SEND capability');
}
```

### 1.2 React Hooks

**File:** `src/hooks/useP0Services.ts`

```typescript
export function useDM() {
  const { api, capabilities } = useAuth();
  return {
    createThread: (recipientId: string) => api.dm_createThread(recipientId),
    sendMessage: (threadId: string, content: string) => api.dm_sendMessage(threadId, content),
    threads: useQuery(['dm-threads'], () => api.dm_listThreads()),
    canSend: capabilities.includes('DM_SEND')
  };
}

export function useExplainThis() {
  const { api } = useAuth();
  return {
    explain: (type: string, id: string) => api.explain(type, id),
    explainTree: (id: string, depth: number) => api.explainTree(id, depth)
  };
}

export function useGuilds() {
  const { api } = useAuth();
  return {
    join: (guildId: string) => api.guild_join(guildId),
    create: (manifest: GuildManifest) => api.guild_create(manifest),
    list: useQuery(['guilds'], () => api.guild_list())
  };
}

export function useOnboarding() {
  const { api } = useAuth();
  return {
    startTour: (tourId: string) => api.tour_start(tourId),
    completeStep: (tourId: string, stepId: string) => api.tour_completeStep(tourId, stepId)
  };
}
```

---

## Phase 2: Build Explain-This Drill-Down UI

### 2.1 Progressive Disclosure Pattern

**Layer 1: Summary Badge/Pill**

```tsx
// src/components/ExplainPill.tsx
export function ExplainPill({ entityType, entityId }: ExplainPillProps) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="explain-pill">
      <button onClick={() => setExpanded(!expanded)}>
        <InfoIcon /> Why?
      </button>
      {expanded && <ExplainPanel entityType={entityType} entityId={entityId} />}
    </div>
  );
}
```

**Layer 2: Detailed Factors Panel**

```tsx
// src/components/ExplainPanel.tsx
export function ExplainPanel({ entityType, entityId }: ExplainPanelProps) {
  const { explain } = useExplainThis();
  const { data: explanation, isLoading } = useQuery(
    ['explain', entityType, entityId],
    () => explain(entityType, entityId)
  );

  if (isLoading) return <Skeleton />;

  return (
    <div className="explain-panel">
      <h3>Why this {entityType}?</h3>
      
      {/* Summary */}
      <div className="explain-summary">
        {explanation.computation.summary}
      </div>

      {/* Factors */}
      <div className="explain-factors">
        {explanation.inputs.map(input => (
          <FactorCard key={input.event_id} factor={input} />
        ))}
      </div>

      {/* Drill down button */}
      <button onClick={() => showRawEvents()}>
        View Raw Events
      </button>
    </div>
  );
}
```

**Layer 3: Raw Events (Auditor View)**

```tsx
// src/components/ExplainRawEvents.tsx
export function ExplainRawEvents({ explanation }: { explanation: Explanation }) {
  return (
    <div className="raw-events">
      <h4>Ledger Events</h4>
      {explanation.inputs.map(input => (
        <EventCard key={input.event_id} eventId={input.event_id} />
      ))}
      
      {/* Proof verification */}
      <div className="proof">
        <code>{explanation.proof_hash}</code>
        <button>Verify Hash</button>
      </div>
    </div>
  );
}
```

### 2.2 Integration Points

**Feed Items:**

```tsx
// src/components/Feed.tsx
<FeedItem item={item}>
  <ExplainPill entityType="ranking" entityId={item.id} />
</FeedItem>
```

**Rewards:**

```tsx
// src/components/RewardNotification.tsx
<div className="reward">
  +{reward.amount} CHR
  <ExplainPill entityType="reward" entityId={reward.id} />
</div>
```

**DM Notifications:**

```tsx
// src/components/DMNotification.tsx
<div className="dm-notification">
  New message from {sender}
  <ExplainPill entityType="dm_notification" entityId={notif.id} />
</div>
```

---

## Phase 3: Implement Onboarding Tour Overlay

### 3.1 Tour Overlay Component

**File:** `src/components/OnboardingTourOverlay.tsx`

```tsx
export function OnboardingTourOverlay() {
  const { tour, currentStep, completedSteps } = useOnboarding();
  const [visible, setVisible] = useState(true);

  if (!tour || !visible) return null;

  return (
    <div className="tour-overlay">
      {/* Progress indicator */}
      <div className="tour-progress">
        Step {completedSteps.length + 1} of {tour.steps.length}
      </div>

      {/* Current step */}
      <TourStepCard step={currentStep} onComplete={handleComplete} />

      {/* Dismiss */}
      <button onClick={() => setVisible(false)}>Skip Tour</button>
    </div>
  );
}
```

### 3.2 Contextual Triggers

```tsx
// src/hooks/useOnboardingTriggers.ts
export function useOnboardingTriggers() {
  const { startTour } = useOnboarding();

  // Trigger on first DM received
  useEffect(() => {
    if (firstDMReceived && !tourCompleted('dm_intro')) {
      startTour('dm_intro');
    }
  }, [firstDMReceived]);

  // Trigger on first governance notification
  useEffect(() => {
    if (firstGovNotif && !tourCompleted('governance_intro')) {
      startTour('governance_intro');
    }
  }, [firstGovNotif]);
}
```

### 3.3 Tour Step Types

**Interactive Task Steps:**

```tsx
// src/components/TourStepCard.tsx
export function TourStepCard({ step }: TourStepCardProps) {
  switch (step.task_type) {
    case 'POST_CONTENT':
      return <TourPostContent onComplete={() => completeStep(step.id)} />;
    
    case 'SEND_DM':
      return <TourSendDM onComplete={() => completeStep(step.id)} />;
    
    case 'USE_EXPLAIN_THIS':
      return <TourExplainThis onComplete={() => completeStep(step.id)} />;
  }
}
```

---

## Phase 4: Create Guild Management Dashboard

### 4.1 Guild Dashboard Component

**File:** `src/components/GuildDashboard.tsx`

```tsx
export function GuildDashboard({ guildId }: GuildDashboardProps) {
  const { data: guild } = useQuery(['guild', guildId], () => api.guild_get(guildId));

  return (
    <div className="guild-dashboard">
      {/* Header */}
      <GuildHeader guild={guild} />

      {/* Metrics with Explanations */}
      <div className="guild-metrics">
        <MetricCard
          label="Coherence Score"
          value={guild.coherence}
          explainType="guild_coherence"
          explainId={guildId}
        />
        <MetricCard
          label="Members"
          value={guild.members_count}
          explainType="guild_growth"
          explainId={guildId}
        />
      </div>

      {/* Moderation & Appeals */}
      <GuildModerationPanel guildId={guildId} />

      {/* Governance Actions */}
      <GuildGovernancePanel guildId={guildId} />
    </div>
  );
}
```

### 4.2 Moderation Panel with Explain-This

```tsx
// src/components/GuildModerationPanel.tsx
export function GuildModerationPanel({ guildId }: { guildId: string }) {
  const { data: actions } = useQuery(['guild-actions', guildId], () => 
    api.guild_getModerationActions(guildId)
  );

  return (
    <div className="moderation-panel">
      <h3>Recent Actions</h3>
      {actions.map(action => (
        <ActionCard key={action.id} action={action}>
          {/* Every action has an explanation */}
          <ExplainPill entityType="moderation_action" entityId={action.id} />
          
          {/* Appeals can be filed */}
          {action.appealable && (
            <button onClick={() => fileAppeal(action.id)}>
              Appeal
            </button>
          )}
        </ActionCard>
      ))}
    </div>
  );
}
```

---

## Phase 5: Open-AGI Agent Visibility

### 5.1 Agent Action Indicator

```tsx
// src/components/AgentActionIndicator.tsx
export function AgentActionIndicator({ action }: { action: Action }) {
  if (action.scope !== 'SIMULATION' && !action.agent_id) return null;

  return (
    <div className="agent-indicator">
      <BotIcon />
      <span>
        {action.scope === 'SIMULATION' ? 'Simulated' : 'Agent'} action
      </span>
      <ExplainPill entityType="agent_action" entityId={action.id} />
    </div>
  );
}
```

### 5.2 Simulation Mode Badge

```tsx
// src/components/SimulationModeBadge.tsx
export function SimulationModeBadge() {
  const { isSimulationMode } = useAuth();

  if (!isSimulationMode) return null;

  return (
    <div className="simulation-badge">
      🧪 Simulation Mode Active
      <TooltipInfo>
        Actions won't affect real ledger
      </TooltipInfo>
    </div>
  );
}
```

---

## Implementation Roadmap

### Week 1: Foundation

- [ ] Create `p0-api-client.ts`
- [ ] Implement P0 React hooks
- [ ] Add capability checks to existing auth flow

### Week 2: Explain-This UI

- [ ] Build `ExplainPill` component
- [ ] Build `ExplainPanel` with 3 layers
- [ ] Integrate into Feed, Rewards, DMs

### Week 3: Onboarding Tours

- [ ] Build `OnboardingTourOverlay`
- [ ] Implement contextual triggers
- [ ] Create default tour flows

### Week 4: Guild Dashboard

- [ ] Build `GuildDashboard` component
- [ ] Add moderation panel with appeals
- [ ] Integrate Explain-This for all metrics

### Week 5: Polish & Testing

- [ ] Open-AGI agent indicators
- [ ] Simulation mode badges
- [ ] E2E tests for all flows

---

## Design Patterns to Follow

### Progressive Disclosure

- Start simple ("Why?") → Expand to details → Show raw data
- Each layer optional, user controls depth

### Capability-Aware UI

- Disable/hide features if user lacks capability
- Clear messaging: "Requires DM_SEND capability (coherence 300+)"

### Explain Everything

- Every state change gets an ExplainPill
- Reuse explanation components across contexts

### Contextual Onboarding

- Trigger tours from real events, not generic "first login"
- Make tutorials feel situational and helpful

---

## Success Metrics

- **Explain-This Usage:** 40%+ of users click "Why?" at least once
- **Tour Completion:** 70%+ of new users complete welcome tour
- **Guild Engagement:** 30%+ of users create/join at least one guild
- **Appeal Rate:** < 5% of moderation actions appealed (good UX = fewer appeals)

---

**Next Step:** Start with Week 1 foundation - wire P0 APIs into ATLAS frontend.
