# QFS × ATLAS — Agent Fabric Specification

> **Version:** v18.0.0-alpha  
> **Status:** Draft (Edge Expansion Focus)

This document defines how Layer D agents are managed, updated, and governed in the distributed fabric.

## 1. Model Registry

Tier B nodes (Edge Advisory) will pull model configurations from a deterministic registry governed by the Tier A consensus.

- **Schemas:** `AgentDefinition`, `ModelReference`, `PromptTemplate`.
- **Governed Events:** `AGENT_REGISTERED`, `AGENT_UPDATED`, `AGENT_DEPRECATED`.

## 2. Distributed Model Hosting

- **Tier B:** Runs SLMs (Small Language Models) or connects to local models for low-latency advisory.
- **Tier A:** Can host heavy LLM endpoints for cross-node auditing and complex governance summaries.

## 3. Agent Trust & Abuse

- **Reputation Scoring:** Agents are scored based on how often their advice leads to successful governance outcomes vs disputes.
- **Circuit Breakers:** v17 Governance can disable an agent space-wide if it exhibits biased or malicious patterns.

---

**Policy:** Agents in QFS × ATLAS are strictly advisory. They interpret the EvidenceBus but do not own keys or propose state transitions without human-governed F-layer validation.
