# QFS v15 Testnet Status

> **Public Testnet Phase** - External Validation & Attack Surface Discovery  
> **Version:** v15.0.0  
> **Status:** ACTIVE - Ready for Testing  
> **Last Updated:** December 19, 2025

## 🎯 What Is This?

QFS v15.3 introduces **Structural Verifiability** - a fully deterministic system where every governance execution produces a cryptographically signed Proof-of-Execution (PoE) artifact.

**This is a PUBLIC TESTNET.** The goal is external validation of the v15.3 PoE assurance layer.

## ✅ What Can I Verify Myself?

### 1. Run the Full Test Suite

```bash
git clone https://github.com/RealDaniG/QFS.git
cd QFS
git checkout v15.0.0
python v15/tests/autonomous/test_full_audit_suite.py
```

**You will see:**

- 23/23 tests passing
- 13/13 invariants verified
- Complete audit trail generated

### 2. Verify PoE Artifacts

```bash
python v15/tools/verify_poe.py --artifact_id <ID>
```

**You will see:**

- Cryptographic signature valid
- Artifact hash matches on-chain record
- Execution trace integrity confirmed

### 3. Verify Deterministic Replay

```bash
python v15/tools/replay_gov_cycle.py --artifact_id <ID>
```

**You will see:**

- Same inputs → identical outputs
- Zero drift across replays
- Matching PoE hashes

### 3. Check Testnet Nodes

```bash
curl http://testnet.qfs.example.com:3000/api/v1/health
```

**You will see:**

- AEGIS Status: COHERENT
- All health checks: GREEN
- PoE artifacts being generated

### 4. Read the Audit Results

- [AUDIT_PLAN.md](AUDIT_PLAN.md) - What was tested
- [AUDIT_RESULTS_SUMMARY.md](AUDIT_RESULTS_SUMMARY.md) - Test results
- [TEST_INVENTORY.md](TEST_INVENTORY.md) - Complete test coverage

## 🧪 How to Participate

### As a Tester

1. Follow [FIRST_TESTNET_DEPLOYMENT.md](FIRST_TESTNET_DEPLOYMENT.md)
2. Initialize your testnet node
3. Create and vote on proposals
4. Verify PoE artifacts

### As an Auditor

1. Follow [HOW_TO_AUDIT_QFS_V15.md](HOW_TO_AUDIT_QFS_V15.md)
2. Run the audit suite locally
3. Verify deterministic replay
4. Submit security findings

### As a NOD Operator

1. Follow [NOD_OPERATOR_GUIDE.md](NOD_OPERATOR_GUIDE.md)
2. Join the testnet
3. Participate in governance
4. Monitor health and PoE

## 📊 Current Testnet Stats

**Governance:**

- Active Proposals: [Live count]
- Total Votes Cast: [Live count]
- Parameters Changed: [Live count]
- AEGIS Status: COHERENT ✅

**Testing:**

- Total Tests Run: 23
- Pass Rate: 100%
- Invariants Verified: 13/13
| **PoE Assurance** | ✅ Live | Schema v1.0 | External-Grade |count]

**Participation:**

- Active Testers: [Live count]
- NOD Operators: [Live count]
- External Auditors: [Live count]

## 🔒 Security & Transparency

**What We Guarantee:**

- ✅ All governance operations are deterministic
- ✅ All PoE artifacts are cryptographically verifiable
- ✅ All tests are open source and reproducible
- ✅ All audit results are publicly available

**What We Don't Guarantee:**

- ❌ Testnet tokens have NO value
- ❌ Testnet state may be reset
- ❌ This is NOT mainnet
- ❌ No financial speculation

## 🎓 Educational Resources

**Documentation:**

- [V15_OVERVIEW.md](docs/V15_OVERVIEW.md) - System architecture
- [PROPOSAL_ENGINE_SPEC.md](docs/GOVERNANCE/PROPOSAL_ENGINE_SPEC.md) - Governance spec
- [RELEASE_NOTES_v15.0.0.md](RELEASE_NOTES_v15.0.0.md) - Release details

**Tutorials:**

- [First Testnet Deployment](FIRST_TESTNET_DEPLOYMENT.md)
- [How to Audit QFS v15](HOW_TO_AUDIT_QFS_V15.md)
- [Governance Dry-Run Scenarios](scenarios/README.md)

## 🐛 Found a Bug?

**Security Issues:**

- Email: <security@qfs.example.com>
- Encrypted: [PGP Key]

**General Issues:**

- GitHub: <https://github.com/RealDaniG/QFS/issues>
- Label: `testnet` + `v15`

## 📅 Roadmap

**Current Phase: Public Testnet (Weeks 1-4)**

- External validation
- Security review
- Community governance dry-runs

**Next Phase: v15.2 (Weeks 5-8)**

- Enhanced testing framework
- Performance optimizations
- Additional governance features

**Future Phase: Mainnet Preparation (Post-Review)**

- Final security audit
- Mainnet deployment plan
- Community governance activation

## ❓ FAQ

**Q: Are testnet tokens worth anything?**
A: No. Testnet tokens have ZERO value and are for testing only.

**Q: Can I lose real money?**
A: No. This is a testnet with fake tokens.

**Q: What happens to my testnet data?**
A: Testnet state may be reset at any time.

**Q: How do I verify the system is secure?**
A: Run the audit suite, verify PoE artifacts, and review the code.

**Q: Can I trust the testnet nodes?**
A: You can run your own node and verify everything independently.

## 🤝 Contributing

We welcome:

- Security audits
- Bug reports
- Documentation improvements
- Test coverage enhancements

We do NOT welcome:

- Price speculation
- Financial advice
- Mainnet deployment pressure

## 📞 Contact

- **GitHub:** <https://github.com/RealDaniG/QFS>
- **Discussions:** <https://github.com/RealDaniG/QFS/discussions>
- **Security:** <security@qfs.example.com>

---

**Remember:** This is a PUBLIC TESTNET for EXTERNAL VALIDATION. The goal is to find bugs and verify security, not to speculate on price or value.

**Verify everything yourself. Trust nothing. Test everything.**
