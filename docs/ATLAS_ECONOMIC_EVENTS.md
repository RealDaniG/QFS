# ATLAS Economic Events (v14)

Every state change in ATLAS that affects value flow produces an **EconomicEvent** in the immutable log.

## Event Types

### Space Events

| Event Type | Token | Direction | Purpose |
| :--- | :--- | :--- | :--- |
| `space_created` | CHR | Cost (Burn/Treasury) | Anti-Spam, Resource Usage |
| `space_joined` | FLX | Cost (Burn/Treasury) | Ticket/Entry Fee |
| `space_ended` | CHR | Reward (Mint) | Host Time Reward |
| `space_spoke` | CHR | Reward (Mint) | Speaker Proof-of-Work |

### Wall Events

| Event Type | Token | Direction | Purpose |
| :--- | :--- | :--- | :--- |
| `wall_post_created` | FLX | Reward (Mint) | Content Mining Reward |
| `wall_post_liked` | CHR | Reward (Mint) | Author Engagement Reward |
| `wall_reply_created`| FLX | Reward (Mint) | Reply Content Reward |

### Chat Events

| Event Type | Token | Direction | Purpose |
| :--- | :--- | :--- | :--- |
| `chat_session_created` | CHR | Cost | Session Initialization |
| `chat_message_sent` | FLX | Cost | Message Transport Fee |

## Determinism

All events include a `metadata` payload with deterministic IDs (`space_id`, `post_id`) allowing full replay of the economic state.

## Neutral Actions (Logic Only)

The following actions are **Explicitly Neutral** (0 cost, 0 reward):

* `space_role_changed` (Promote/Demote)
* `space_member_kicked`
* `space_member_muted`
* `wall_post_pinned` / `unpinned`
