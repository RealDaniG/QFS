# ATLAS Social Layer Overview (v14)

ATLAS provides a Zero-Sim compliant social graph, consisting of three deepened surfaces: **Spaces**, **Wall**, and **Chat**.

## 1. Spaces (Live Rooms)

Ephemeral, synchronous audio/text rooms.

* **Roles**: Host (Creator), Moderator (Appointed), Speaker, Listener.
* **Moderation**:
  * `promote(wallet, role)`: Host can appoint Moderators.
  * `mute(wallet)`: Host/Mod can mute participants.
  * `kick(wallet)`: Host/Mod can ban participants.
* **Economics**:
  * **Creation**: Cost in CHR (e.g. 1 CHR).
  * **Joining**: Cost in FLX (e.g. 0.1 FLX).
  * **Speaking**: Reward in CHR based on duration.

## 2. Wall (Persistent Content)

Posts linked to Spaces or standalone context.

* **Recaps**:
  * Special post type (`is_recap=True`) linked to a specific `space_id`.
  * Serves as the permanent "record" of a live session.
* **Pinning**: Moderators can pin posts to the top of the Space Wall.
* **Quotes**: Users can quote-post other content (`quoted_post_id`).
* **Economics**:
  * **Posting**: Rewards FLX (Content Mining).
  * **Liking**: Micro-reward in CHR to author (Engagement).

## 3. Chat (Secure Context)

E2EE messaging channels.

* **Group Chats**:
  * Support for ad-hoc groups (not just 1:1).
  * Deterministically managed via `ChatSessionState`.
* **TTL**: Messages/Sessions can have a `ttl_seconds` expiry (enforced at logic level).
* **References**:
  * Messages can structurally reference (link) to Spaces, Wall Posts, or Users via `references` list.
* **Economics**:
  * **Messaging**: Cost in FLX (Anti-Spam).

## 4. Cross-Surface Cohesion

The graph is unified:

* Use **Recaps** to bridge Spaces -> Wall.
* Use **References** to bridge Chat -> Wall/Spaces.
* All actions generate a single, deterministic **Event Log**.

## Canonical Schema

External consumers should use the Pydantic models defined in `v13/atlas/contracts.py`:

* `AtlasSpace`
* `AtlasWallPost`
* `AtlasChatMessage`
