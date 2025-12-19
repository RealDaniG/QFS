# Contributing to QFS × ATLAS

Thank you for your interest in contributing! We are building the future of **quantum-resistant autonomous finance**, and we need developers like you to help us harden the system.

This guide details how to claim bounties, set up your environment, and submit quality Pull Requests (PRs).

---

## 💰 Bounty Workflow

We incentivize contributions through our **Developer Rewards Treasury**. All active tasks are listed in [BOUNTIES.md](BOUNTIES.md).

1. **Browse**: Check [BOUNTIES.md](BOUNTIES.md) for "OPEN" tasks.
2. **Claim**: Comment on the relevant GitHub Issue (or open one if it doesn't exist) stating "I would like to work on this [Bounty ID]".
3. **Fork & Branch**: Fork the repository and create a branch named `bounty/<id>-<short-description>`.
4. **Develop**: Write code, strictly following the [Development Setup](#-development-setup) and [Code Style](#-code-style).
5. **Test**: Ensure all tests pass, including the v14 regression suite.
6. **Submit PR**: Open a Pull Request referencing the Bounty ID in the description using the [template provided in BOUNTIES.md](BOUNTIES.md#%F0%9F%93%9D-bounty-template).
7. **Review & Reward**: Once merged, the reward (CHR/FLX) will be processed to your wallet.

### 🗺️ The Contributor Journey

We track every contribution on-chain via EvidenceBus. Here is the lifecycle of a rewarded contribution:

1. **Wallet & Scopes**: Connect your wallet to ATLAS to generate a deterministic UserID and obtain `bounty:read` scope.
2. **Contribution**: Pick an issue, claim it, and submit a PR linking your GitHub account (via dual-proof in Phase V+).
3. **Evidence**: The system emits a `bounty_event` and `github_link_event` to the EvidenceBus, hash-chaining your work.
4. **Reward**: Upon merge, the specific Token Reward (CHR/FLX) is allocated to your wallet via the Treasury.
5. **Explainability**: Use the "Explain-This" tool to see exactly *why* you earned that amount, tracing back to the original rule.

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Git

### Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-org/qfs-atlas.git
    cd qfs-atlas
    ```

2. **Create Virtual Environment**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Install Pre-commit Hooks**

    ```bash
    pre-commit install
    ```

---

## 🎨 Code Style

We enforce strict quality standards to maintain **Zero-Simulation Compliance**.

- **Formatting**: Black (line length 100).
- **Type Hints**: Mandatory for all new functions. Use `mypy` strict settings.
- **Docstrings**: Google-style docstrings required for all public modules, classes, and functions.
- **Imports**: Absolute imports preferred (e.g., `from v13.libs.BigNum128 import BigNum128`).

---

## 🛡️ Role: Maintainer?

See the [Maintainer's Guide](docs/MAINTAINERS_GUIDE.md) for triage, labeling, and release procedures.

---

## ✅ Pull Request Requirements

Your PR **will be rejected** if it fails any of these checks:

1. **Tests Passing**: `pytest v13/tests/` must be 100% green.
2. **Regression Verified**: `python v13/tests/regression/phase_v14_social_full.py` must complete successfully.
3. **Core Invariants**: PR description must include the [Core Invariant Checklist](docs/PR_TEMPLATE_v15.5.md).
4. **Type Safety**: No new `mypy` errors introduced.
4. **Deterministic**: No non-deterministic code (e.g., `random.random()`, `time.time()` outside of controlled contexts).

---

## \ud83d\udd2c Cost-Efficiency & MOCKQPC Requirements

All contributions must follow **cost-efficiency principles** and **MOCKQPC-first architecture**:

### MOCKQPC-First Development

- **All dev/beta work uses MOCKQPC** (zero PQC cost)
- **Environment tagging**: Events must include `env=dev|beta|mainnet`
- **Crypto abstraction**: Use `sign_poe(hash, env)` and `verify_poe(hash, sig, env)`
- **No real PQC** until mainnet activation

### Batched PoE

- **Hash-chain all events** (moderation, admin, agent outputs)
- **Batch signatures**: 100-1,000 events per batch
- **Cost target**: <0.01 PQC calls per decision

### Agent Advisory

- **Stateless services**: Horizontally scalable
- **Sampling**: 10-20% of content (configurable)
- **Advisory only**: Outputs feed deterministic `F`, never decide directly
- **Cost target**: <0.2 agent calls per decision

### EvidenceBus Integration

All PoE-worthy events must use **EvidenceBus**:

```python
from v13.evidence_bus import EvidenceBus

bus = EvidenceBus(env='dev')
bus.emit_event({
    'type': 'moderation_decision',
    'content_id': 'POST_12345',
    'action': 'remove',
    'moderator_id': 'wallet:0xABC...',
    'timestamp': '2025-12-19T15:00:00Z'
})
```

### Cost-Efficiency Checklist

Before submitting PR, verify:

- [ ] MOCKQPC-first (dev/beta environments)
- [ ] Batched PoE (hash-chained events, batch signatures)
- [ ] Crypto abstraction (`sign_poe`/`verify_poe` with `env`)
- [ ] Agent advisory (outputs feed `F`, never decide)
- [ ] Deterministic core (pure functions + rules)

See [DEV_GUIDE.md](./DEV_GUIDE.md) for setup instructions.
See [FAQ - MOCKQPC & Agents](docs/FAQ_MOCKQPC_AND_AGENTS.md) for background.

---

**Q: My regression hash doesn't match.**
A: Ensure you haven't modified any core v14 logic variables. Bounties usually target v15 layers or infrastructure.

**Q: Treasury limits?**
A: Check `v13/policy/treasury/dev_rewards_treasury.py` for current reserve levels.

---

**Happy Coding!** 🚀
