
# C-004 Inbox Implementation Plan

## Backend (`api/chat.py`)

Add `GET /v1/chat/threads` endpoint.
Logic:

1. Replay `GenesisLedger` events of type `MESSAGE`.
2. Filter where `sender == current_user` OR `recipient == current_user`.
3. Group by "Other Party".
4. Return list of `{ peer_wallet, last_message_ts, last_message_preview_encrypted }`.

## Frontend (`Inbox.tsx`)

1. Fetch threads on mount.
2. Render list of conversations.
3. On Click -> Open `ChatWindow` for that peer.

## Zero-Sim Note

This relies on replaying the ledger (O(N) unless indexed). For V1 MVP this is acceptable. V2 would use a dedicated SQL/Redis projection.
