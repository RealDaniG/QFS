# Changelog

All notable changes to QFS × ATLAS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned (v15 Protocol Layer)

- Living Posts Layer (HSMF-validated engagement rewards)
- Developer Rewards Layer (bounties + ATR boosts)
- Governance automation (GovernanceStateMachine)
- Zero-Sim Contract v1.5

## [v14.0-social-layer] - 2025-12-18

### Added

- **v14 Social Layer** - Three production-ready modules:
  - Spaces (audio rooms with capacity limits)
  - Wall Posts (social feed with reactions and threading)
  - Chat (secure messaging with E2EE metadata)
- **Economic Events** - 11 new event types with CHR/FLX rewards:
  - `space_created`, `space_joined`, `space_left`
  - `post_created`, `post_liked`, `post_quoted`, `post_pinned`
  - `conversation_created`, `message_sent`, `message_read`, `reaction_added`
- **Regression Testing** - Canonical v14 social regression scenario
  - `v13/tests/regression/phase_v14_social_full.py`
  - SHA-256 regression hash: `v14_regression_hash.txt`
  - CI-gated verification (pre-release workflow)
- **Zero-Sim Contract v1.4** - Formalized determinism guarantees
  - All social events deterministic and replayable
  - 0 Zero-Sim violations across v14 modules
- **Developer Rewards Foundation** - Bounty system infrastructure:
  - Bounty schema (`Bounty`, `BountySubmission`, `ContributorProfile`)
  - Economic events (`dev_bounty_paid`, `atr_boost_applied`)
  - Dev Rewards Treasury (bounded reserves)

### Changed

- **HSMF** - Fixed CoherenceEngine sort key for deterministic ordering
- **CI Pipeline** - Enhanced with structured logging and fail-fast
  - Pinned GitHub Actions to SHAs (supply chain security)
  - Added minimal permissions to all jobs
  - Implemented violation summaries and step timing

### Security

- **CI Hard Gates** - Blocking checks for main and releases:
  - All tests must pass (60+ tests, 100% pass rate)
  - Zero-Sim analyzer (0 violations required)
  - Regression hash verification (v14 frozen)
- **Pinned Actions** - All GitHub Actions pinned to specific SHAs
- **Minimal Permissions** - Tightened permissions on all CI jobs
- **Depletion Alerts** - Treasury monitoring at 20% (low) and 10% (critical)

### Documentation

- **v14 Evidence Deck** - Audit-ready compliance documentation
- **v14 Release Notes** - Complete feature and change documentation
- **Security Notes** - Trust assumptions and limitations
- **CI Improvements** - Phase 1 improvements and roadmap
- **Repository Structure** - Canonical organization guide
- **v15 Protocol Spec** - Timeless execution plan (additive layer)

### Fixed

- CoherenceEngine deterministic event ordering
- Zero-Sim violations in HSMF (0 violations achieved)
- Root directory cleanup (32 → 18 files, 44% reduction)

## [v13.9] - 2025-12-15

### Added

- HSMF integration planning
- Governance roadmap
- Phase 3 Zero-Sim cleanup

### Fixed

- PQC runtime errors
- Gateway explain functionality
- Test collection issues

## [v13.8] - 2025-11-20

### Added

- CertifiedMath HSMF Phase 4 compliance
- StateTransitionEngine integration
- CoherenceEngine deterministic logging

### Fixed

- CertifiedMath structural corruption
- HSMF argument passing issues
- Proof vector coverage

---

## Version Naming Convention

- **v14.x** - Social Layer (frozen baseline)
- **v15.x** - Living Posts + Developer Rewards (parallel layer)
- **v16.x** - NOD Integration (future)

## Migration Notes

### v13.x → v14.0

- No breaking changes to v13 core
- Social modules are additive
- Existing economic events unchanged

### v14.0 → v15.0 (Planned)

- v14 remains frozen and unchanged
- v15 is a parallel, additive layer
- No v14 semantic or economic changes
- v15 can be disabled without affecting v14

---

**Maintained by**: QFS × ATLAS Core Team  
**Last Updated**: 2025-12-18
