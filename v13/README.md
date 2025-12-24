# ATLAS v19 – Decentralized Intelligence Network

**Status:** ✅ Alpha Release  
**Version:** v19.0.0-alpha  
**Release Date:** December 23, 2025

## 🌟 What's New in v19

### Revolutionary Architecture: 4-Layer Stack

1. **🔐 Trust Layer** – Cryptographic verification via TrustedEnvelope
2. **💾 Storage Layer** – IPFS content-addressed storage
3. **🌐 Network Layer** – P2P mesh with real-time messaging
4. **🤖 Intelligence Layer** – Advisory AI agents (4 agents active)

### Key Features

- ✅ **Decentralized Storage** – All content stored in IPFS (no central database)
- ✅ **Real-Time P2P** – Updates propagate instantly via WebSocket mesh
- ✅ **Cryptographic Trust** – Every piece of content is signed and verified
- ✅ **Advisory AI** – 4 autonomous agents analyze content, detect fraud, validate bounties
- ✅ **Offline-First** – Local IPFS node enables offline operation
- ✅ **Censorship-Resistant** – No single point of control or failure

## 🚀 Quick Start

### Prerequisites

- **Docker** (for IPFS daemon)
- **Python 3.11+** (backend)
- **Node.js 20+** (frontend)
- **MetaMask** (wallet authentication)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13

# 2. Start IPFS daemon
docker-compose up -d ipfs

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Install frontend dependencies
cd ../atlas
npm install

# 5. Launch full stack
cd ..
./launch_atlas_full.bat  # Windows
# or
./launch_atlas_full.sh   # Linux/Mac
```

### Access Points

- **Frontend:** <http://localhost:3000>
- **Backend API:** <http://127.0.0.1:8001>
- **P2P Node:** ws://127.0.0.1:9000/ws
- **IPFS Gateway:** <http://127.0.0.1:8080>

## 📚 Architecture Documentation

See `docs/v19_ARCHITECTURE.md` for complete technical reference.

## 🧪 Verification

All layers can be independently verified:

```bash
cd backend

# Trust Layer
python verify_trust_layer.py

# Storage Layer  
python verify_ipfs_layer.py

# Network Layer
python verify_p2p_layer.py

# Intelligence Layer
python verify_intelligence_layer.py
```

**Expected:** All scripts should output `✅ All Systems Go` or comparable success messages.

## 🖥️ Desktop Application (Electron)

### Launch Desktop App

```bash
cd atlas
npm run electron:dev
```

### Build Distributable

```bash
npm run electron:build
# Output: desktop/dist/win-unpacked/ATLAS v19.exe
```

## 🤖 Intelligence Agents (Advisory)

v19 includes 4 autonomous AI agents:

| Agent | Purpose | Verdict Types |
|-------|---------|---------------|
| **BountyValidator** | Validates bounty claims | PASS / NEEDS_REVIEW / REJECT |
| **FraudDetector** | Detects time-travel, malformed data | INFO / REVIEW / REJECT |
| **ReputationScorer** | Calculates trust scores | Score 0.0-1.0 |
| **GovernanceAnalyzer** | Flags high-risk proposals | PASS / NEEDS_REVIEW |

**Important:** All agent verdicts are **advisory only**. They do not auto-reject content but provide insights for human reviewers.

## 🔐 Security Model

### Wallet = Identity

- Wallets prove cryptographic identity (no passwords)
- Every action requires wallet signature
- Session tokens use ASCON-128 encryption

### TrustedEnvelope Verification

- All content wrapped in signed envelopes
- Signatures verified at ingress
- Invalid envelopes rejected immediately

### P2P Security

- Encrypted WebSocket connections
- Message deduplication prevents replay attacks
- Peer identity binding (wallet ↔ peer_id)

## 📊 Comparison: v18 → v19

| Feature | v18 (Centralized) | v19 (Decentralized) |
|---------|-------------------|---------------------|
| Storage | Backend DB | ✅ IPFS (CIDs) |
| Updates | HTTP polling | ✅ P2P real-time |
| Trust | Basic auth | ✅ Signed envelopes |
| AI | None | ✅ 4 advisory agents |
| Offline | No | ✅ Local IPFS node |
| Censorship | Vulnerable | ✅ P2P mesh resistant |

## 🐛 Known Limitations (v19 Alpha)

### Expected Limitations

- **AGI agents are advisory only** – No auto-enforcement of verdicts
- **IPFS daemon required** – Must run Docker or local Kubo instance
- **P2P node required** – Backend must be running for real-time updates
- **Alpha stability** – Not production-ready; for testing only

### Technical Constraints

- **Browser P2P limitations** – Cannot accept inbound connections (WebSocket client only)
- **Network sync delay** – Initial peer discovery takes 5-10 seconds
- **IPFS pinning costs** – Local storage grows over time

## 📖 Documentation

- `docs/v19_ARCHITECTURE.md` – Complete technical architecture
- `REPAIR_LOG.md` – v18 → v19 migration history
- `KNOWN_ISSUES.md` – Current limitations and workarounds
- `FINAL_VERIFICATION_CHECKLIST.md` – Pre-release testing

## 🤝 Contributing

See main repository for contribution guidelines.

## 📄 License

See LICENSE file in repository root.

## 🙏 Acknowledgments

- **IPFS/libp2p teams** for decentralized infrastructure
- **Open-A.G.I project** for agent framework inspiration
- **ATLAS community** for testing and feedback

---

**Built with:** Python, TypeScript, React, Next.js, IPFS, libp2p, Docker, ASCON-128
