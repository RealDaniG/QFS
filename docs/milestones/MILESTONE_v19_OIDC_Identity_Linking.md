# Milestone: OIDC Identity Linking (v19)

**Objective:** Add optional OIDC identities and unify subjects while keeping wallet as the only authority.

## Features

- **OIDC Plumbing:** GitHub OIDC integration.
- **Identity Binding:** Bind OIDC to Wallet via signed message.
- **Unified Subjects:** Session supports multiple subjects.

## Verification

- [ ] Unbound OIDC accounts have zero authority.
- [ ] Replay tests reconstruct bindings from EvidenceBus.
