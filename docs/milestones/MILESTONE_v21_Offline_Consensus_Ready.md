# Milestone: Offline Consensus Ready (v21)

**Objective:** Add deterministic offline semantics and a replication-ready `SessionStore`.

## Features

- **Offline Counters:** Lamport-style local sequence numbers.
- **Offline Queue:** Client-side signed action queue.
- **Replicated SessionStore:** Append-only log with Raft-ready API.

## Verification

- [ ] Reconnected offline log replays deterministically.
- [ ] Session mutations correlate 1:1 with PoE events.
