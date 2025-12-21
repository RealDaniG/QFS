# ATLAS v18 Alpha Testing Guide

## Prerequisites

- MetaMask (or compatible EVM wallet) installed
- Backend running on `localhost:8001`
- Frontend running on `localhost:3000`

## Test Scenarios

### 1. Wallet Connection & Auth

1. Open `http://localhost:3000`
2. Click "Connect Wallet"
3. Approve MetaMask connection
4. Verify:
   - Address appears in header
   - Sidebar shows reputation
   - Protected views are accessible

### 2. Governance

1. Navigate to Governance view
2. View proposal list
3. Click "Vote For" or "Vote Against"
4. Verify vote tally updates

### 3. Spaces (Discovery)

1. Navigate to Discover view
2. Browse spaces list
3. Click "Join" on a space
4. Verify membership confirmed

### 4. Messaging

1. Navigate to Messages view
2. Select a conversation
3. Type and send a message
4. Verify message appears in thread

### 5. Wallet & Balance

1. Navigate to Wallet view
2. Verify FLX balance matches sidebar and home
3. View transaction history

## Reporting Issues

- Console errors: Take screenshot
- Unexpected behavior: Document steps to reproduce
- API failures: Check Network tab and note endpoint + status code
