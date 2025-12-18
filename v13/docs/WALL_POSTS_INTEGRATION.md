# ATLAS Wall Posts Integration

**Version**: 13.9
**Status**: Implemented
**Module**: `v13.atlas.spaces`

## Overview

The Wall Posts module enables persistent, space-linked content within the ATLAS ecosystem. It allows users to create posts attached to specific Spaces (live or ended), enabling asynchronous engagement that complements the real-time nature of Spaces.

## Architecture

### Data Structures

#### WallPost

- **post_id**: Deterministic ID derived from `space_id:author:timestamp:content_head`.
- **space_id**: Link to the parent Space.
- **author_wallet**: Creator of the post.
- **content**: Post content (text).
- **timestamp**: Creation time (QFS time).
- **likes**: Dictionary of `wallet -> timestamp`.
- **replies**: List of child `post_id`s.

### Components

#### WallPostManager (`v13/atlas/spaces/wall_posts.py`)

- **`create_post`**: Generates deterministic ID, creates `WallPost`, links to Space.
- **`like_post`**: Records engagement (idempotent).
- **`reply_to_post`**: Creates a new `WallPost` and links it to the parent.

#### WallPostEvents (`v13/atlas/spaces/wall_posts_events.py`)

- Handles `EconomicEvent` emission for integration with the QFS Ledger.

## Economic Model

Wall Posts mirror the "User as Value" verification model used in Spaces.

| Action | Token | Amount | Recipient |
| :--- | :--- | :--- | :--- |
| **Create Post** | FLX | 0.5 | Author |
| **Reply to Post** | FLX | 0.5 | Replier (for creation) |
| **Receive Reply** | CHR | 0.005 | Parent Author |
| **Receive Like** | CHR | 0.001 | Post Author |

*All amounts are represented as `BigNum128` fixed-point integers.*

## Zero-Sim Compliance

- **Determinism**: All `post_id`s and `event_id`s are generated using strictly deterministic hashing of input parameters.
- **Math**: All economic calculations use `CertifiedMath` (imul, etc.) to ensure precision and safety.
- **Logging**: All state changes emit structured logs compatible with the `log_list` pattern for replay verification.

## Integration

Posts are linked to spaces via `space_id`. The system supports posting to both `ACTIVE` and `ENDED` spaces, creating a permanent record ("Wall") for the event.

## Implementation Notes & Critical Constraints

### BigNum128 & CertifiedMath Interaction

During implementation Phase V, strict typing requirements were enforced in the math core:

1. **`CertifiedMath` Ops**: All inputs to methods like `mul`, `imul`, `div` must be properly typed. `imul` specifically requires `(int, BigNum128)` order.
2. **`BigNum128` Scaling**: `BigNum128.mul` now delegates raw integer multiplication to `CertifiedMath` without redundant division-by-scale, as `CertifiedMath` handles fixed-point adjustments. This prevents value collapse.

### Testing Requirements

- **Real Math Only**: Unit tests (`v13/tests/test_wall_posts.py`) must use real `CertifiedMath` instances, not mocks, to verify economic correctness.
- **Deep Determinism**: Tests enforce that re-running a post creation with identical inputs results in a physically identical `EconomicEvent` object (same ID, same metadata, same amount).
