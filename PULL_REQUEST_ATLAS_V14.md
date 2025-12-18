# PR Title: ATLAS v14 Social Layer – Deterministic Spaces/Wall/Chat + Canonical Contracts

## Summary

- Implements the **ATLAS v14 Social Layer** across Spaces, Wall, and Secure Chat.
- Ensures every economically relevant action emits a deterministic `EconomicEvent`.
- Adds a unified social regression script and canonical Pydantic contracts for external consumers.

## Key Changes

- **Spaces (`v13/atlas/spaces/`)**
  - Roles & moderation: Host, Moderator, Speaker, Listener with `ParticipantStatus` (Active/Muted/Kicked).
  - Economic wiring: `create_space`, `join_space`, `end_space`, and `record_speak_time` now emit CHR/FLX events.
  - Tests: `test_spaces.py`, `test_spaces_moderation.py` updated and passing.

- **Wall (`v13/atlas/spaces/wall_posts.py` + events)**
  - Features: pinned posts, recaps (`is_recap`, `linked_space_id`), quote posts (`quoted_post_id`).
  - Deterministic ordering in `get_posts_by_space` (pinned first, then newest).
  - Economic wiring: `create_post` / recap creation emit FLX rewards.
  - Tests: `test_wall_posts.py`, `test_wall_deepening.py`, `test_economic_wiring.py` passing.

- **Chat (`v13/atlas/chat/`)**
  - Group sessions with `initial_members`.
  - TTL via `ttl_seconds` with enforcement on send.
  - References: `ChatMessage.references` for cross-surface linking.
  - Economic wiring: `chat_session_created` (CHR cost), `chat_message_sent` (FLX cost).
  - Tests: `test_secure_chat.py`, `test_chat_deepening.py` passing.

- **Contracts (`v13/atlas/contracts.py`)**
  - Canonical Pydantic models: `AtlasSpace`, `AtlasWallPost`, `AtlasChatSession`, `AtlasChatMessage`, plus contract enums.
  - Adapters: `space_to_contract`, `post_to_contract`, `message_to_contract`.

- **Determinism & Regression**
  - Math core regression: `test_math_regression_baseline` (hash locked).
  - Unified social prototype: `phase_v14_social_full.py` (trace hash `775e72948e2e...`, 9 EconomicEvents for the full lifecycle).

## Verification

- `pytest` full suite: GREEN (including `test_spaces.py`, `test_spaces_moderation.py`, `test_wall_deepening.py`, `test_economic_wiring.py`, `test_chat_deepening.py`).
- `python v13/phase_v14_social_full.py`: passes; produces stable trace hash and expected event count.
- All circular imports resolved; create/join/end/post/send signatures harmonized with tests and events.

## Review Focus

- Confirm that:
  - Social semantics (moderation, recaps, references, TTL) match the docs.
  - Economic events and amounts are correct and align with `ATLAS_ECONOMIC_EVENTS.md`.
  - Canonical contracts expose everything external clients need without leaking internal details.
