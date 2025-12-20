# UX Polish Backlog (V18)

Issues identified during the "First-Time User" narrative walkthrough. Use this list for the next polish sprint.

## 1. Onboarding & Auth

- [ ] **Wallet Connect**: No visual feedback when "Connecting...". Needs a spinner.
- [ ] **Login State**: After login, the "Login" button briefly flickers before showing Profile.
- [ ] **Logout**: No confirmation modal; strictly immediate logout.

## 2. Governance

- [ ] **Voting**: Clicking "Approve" gives no immediate visual feedback until fetch completes. Needs optimistic UI update.
- [ ] **Empty State**: "No active proposals" is plain text. Needs a "Create Proposal" CTA or illustration.

## 3. Feed

- [ ] **Mock Data Transition**: Loading the Distributed Feed has a layout shift as `mockPosts` are replaced.
- [ ] **Timestamps**: Raw timestamps might be shown if formatting fails. Ensure nice relative time (e.g., "5m ago").

## 4. Wallet

- [ ] **Currency Display**: "FLX" symbol inconsistent (sometimes "FLX", sometimes "Units"). Standardize.
- [ ] **Transaction History**: List view is cramped on mobile.

## 5. Accessibility

- [ ] **Color Contrast**: Dark mode text on cards might be too low contrast.
- [ ] **Keyboard Nav**: Tab order in Governance tabs is confusing.
