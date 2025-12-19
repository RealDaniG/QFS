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

## ✅ Pull Request Requirements

Your PR **will be rejected** if it fails any of these checks:

1. **Tests Passing**: `pytest v13/tests/` must be 100% green.
2. **Regression Verified**: `python v13/tests/regression/phase_v14_social_full.py` must complete successfully.
3. **Type Safety**: No new `mypy` errors introduced.
4. **Deterministic**: No non-deterministic code (e.g., `random.random()`, `time.time()` outside of controlled contexts).

---

## ❓ Troubleshooting

**Q: My regression hash doesn't match.**
A: Ensure you haven't modified any core v14 logic variables. Bounties usually target v15 layers or infrastructure.

**Q: Treasury limits?**
A: Check `v13/policy/treasury/dev_rewards_treasury.py` for current reserve levels.

---

**Happy Coding!** 🚀
