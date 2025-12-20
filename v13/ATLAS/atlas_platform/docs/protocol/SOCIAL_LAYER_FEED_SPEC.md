# Social Layer Feed Specification (Zero-Simulation)

## Overview

The Social Layer Feed determines the order and visibility of content presented to users. In the Zero-Simulation architecture, this ranking is derived deterministically from QFS Coherence Metrics and is not computed locally by the client.

## Ranking Architecture

### 1. Coherence-Based Ranking

Content is ranked by its `coherence_score`, which is calculated by the QFS `CoherenceEngine` based on:

- **Truthfulness:** Cross-referenced verification (where applicable).
- **Consistency:** Alignment with established ontology.
- **Engagement:** High-quality interactions (not just click-bait).

### 2. Zero-Simulation Policy

- **No Local Sorting:** The client does NOT fetch all posts and sort them locally.
- **API Driven:** The client requests `GET /feed?algo=coherence` from the QFS Backend.
- **Pagination:** The backend handles pagination to ensure consistent views across devices.

## Feed Algorithms

### A. Certified (Default)

- **Criterion:** Highest Coherence Score.
- **Purpose:** Promote high-quality, verified information.
- **Source:** `QFSClient.getFeed({ strategy: 'certified' })`

### B. Recent

- **Criterion:** Reverse Chronological.
- **Purpose:** Real-time visibility.
- **Source:** `QFSClient.getFeed({ strategy: 'recent' })`

### C. Community

- **Criterion:** Staked Support.
- **Purpose:** Governance and community-driven highlighting.
- **Source:** `QFSClient.getFeed({ strategy: 'community' })`

## Data Flow

1. **User** requests feed.
2. **QFSClient** calls `http://localhost:8000/feed`.
3. **QFS Backend** queries `Ledger` for content + `CoherenceEngine` for scores.
4. **QFS Backend** returns sorted list of CIDs.
5. **ATLAS Client** resolves CIDs via IPFS.
