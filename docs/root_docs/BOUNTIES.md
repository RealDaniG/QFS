# QFS × ATLAS — Developer Bounties 💰

Welcome to the **QFS × ATLAS Developer Bounty Program**! Help us build the future of quantum-resistant autonomous finance.

> **Total Available Rewards**: 1400 CHR
> **Status**: ACTIVE 🟢

---

## 🚀 Available Bounties

| ID | Title | Reward | Difficulty | Status |
|----|-------|--------|------------|--------|
| **BNT-20251218-01** | **Implementation of Living Posts Subtasks (Phase 1)**<br>Implement core structures for `LivingPost` and `InteractionEvent`. | **500 CHR** | Hard 🌶️🌶️🌶️ | **OPEN** |
| **BNT-20251218-02** | **CI/CD Pipeline Enhancement**<br>Add Type Safety check job (`mypy`) and Regression Hash verification step to GitHub Actions. | **300 CHR** | Medium 🌶️🌶️ | **OPEN** |
| **BNT-20251218-03** | **Expand Unit Test Coverage**<br>Add tests for `v13/policy` ensuring >90% coverage for Governance logic. | **250 CHR** | Medium 🌶️🌶️ | **OPEN** |
| **BNT-20251218-04** | **Type Safety Hardening**<br>Resolve top 20 `mypy` strict mode errors in `v13/libs` (CertifiedMath/BigNum128). | **200 CHR** | Easy 🌶️ | **OPEN** |
| **BNT-20251218-05** | **Documentation Gap Analysis**<br>Audit and update API documentation for `v13/atlas` module. | **150 CHR** | Easy 🌶️ | **OPEN** |

---

## 📝 Bounty Template

When submitting a Pull Request for a bounty, please copy the template below into your PR description.

```markdown
### 🎯 Bounty Submission

**Bounty ID**: BNT-YYYYMMDD-XX (e.g., BNT-20251218-01)
**Title**: [Bounty Title]

### 🛠️ Implementation Details
- [Brief description of changes]
- [List of files modified]

### ✅ Verification
- [ ] Tests passed: `pytest v13/tests/`
- [ ] Regression verified: `python v13/tests/regression/phase_v14_social_full.py`
- [ ] Type check passed: `mypy v13/libs`

### 👤 Contributor Info
- **Wallet ID (for payout)**: [Your Testnet Wallet Address]
```

## 📜 Rules & Guidelines

1. **First Come, First Served**: Claims are processed on a first-valid-PR basis.
2. **Quality Code**: Follow strict typing (`mypy` compliant) and PEP8 formatting.
3. **Tests Required**: No code without tests.
4. **Zero Regression**: Your changes MUST NOT break existing v14 regression tests.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full setup instructions.
