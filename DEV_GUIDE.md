# QFS × ATLAS — Cross-Platform Development Guide

> **Version:** v18.0.0-alpha (Distributed Backbone)  
> **Platforms:** Windows, macOS, Linux  
> **Updated:** December 20, 2025

---

## 🎯 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** (for ATLAS frontend)
- **Git**
- **4GB RAM minimum**

---

## 🪟 Windows Setup

### 1. Windows Install Dependencies

```powershell
# Install Python from python.org
# Install Node.js from nodejs.org
# Install Git from git-scm.com

# Verify installations
python --version
node --version
git --version
```

### 2. Windows Clone Repository

```powershell
git clone https://github.com/RealDaniG/QFS.git
cd QFS\v13
```

### 3. Windows Backend Setup

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:ENV="dev"
$env:MOCKQPC_ENABLED="true"
$env:BATCH_SIZE="100"

# Initialize database
python scripts\init_db.py --env=dev

# Start backend
uvicorn atlas.src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Windows Frontend Setup

```powershell
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. Windows MOCKQPC Service

```powershell
# Open new terminal
cd v15\mockqpc
python service.py --port 8001
```

---

## 🍎 macOS Installation

### 1. macOS Install Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Node.js, Git
brew install python@3.11 node git

# Verify installations
python3 --version
node --version
git --version
```

### 2. macOS Clone Repository

```bash
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13
```

### 3. macOS Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENV=dev
export MOCKQPC_ENABLED=true
export BATCH_SIZE=100

# Initialize database
python scripts/init_db.py --env=dev

# Start backend
uvicorn atlas.src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. macOS Frontend Setup

```bash
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. macOS MOCKQPC Service

```bash
# Open new terminal
cd v15/mockqpc
python service.py --port 8001
```

---

## 🐧 Linux Installation

### 1. Linux Install Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm git

# Fedora/RHEL
sudo dnf install python3.11 nodejs npm git

# Arch
sudo pacman -S python nodejs npm git

# Verify installations
python3 --version
node --version
git --version
```

### 2. Linux Clone Repository

```bash
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13
```

### 3. Linux Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENV=dev
export MOCKQPC_ENABLED=true
export BATCH_SIZE=100

# Initialize database
python scripts/init_db.py --env=dev

# Start backend
uvicorn atlas.src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Linux Frontend Setup

```bash
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. Linux MOCKQPC Service

```bash
# Open new terminal
cd v15/mockqpc
python service.py --port 8001
```

---

## 🐳 Docker Setup (All Platforms)

### 1. Windows/Mac/Linux Install Docker

- **Windows**: Docker Desktop from docker.com
- **macOS**: Docker Desktop from docker.com
- **Linux**: `sudo apt install docker.io docker-compose` (or equivalent)

### 2. Docker Build and Run

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Testing

### Run All Tests

```bash
# Windows
$env:PYTHONPATH="."
$env:ENV="dev"
$env:MOCKQPC_ENABLED="true"
pytest v18\\tests\\
pytest v17\\tests\\
pytest v13\\tests\\

# macOS/Linux/GitBash
export PYTHONPATH="."
export ENV="dev"
export MOCKQPC_ENABLED="true"
pytest v18/tests/
pytest v17/tests/
pytest v13/tests/
```

### Verification Checks

```bash
# Zero-Sim Enforcement (Mandatory)
python scripts/check_zero_sim.py --fail-on-critical

# Advisory Smoke Test (Layer D)
python scripts/smoke_test_layer_d.py
```

### Regression Suite

```bash
# Phase v14 Social Regression
pytest v13/tests/
```

## Specific Test Suites

```bash
# Unit tests
pytest v13/tests/unit/

# Integration tests
pytest v13/tests/integration/

# Regression tests
python v13/tests/regression/phase_v14_social_full.py
```

### Verify Determinism

```bash
# Run determinism tests 100 times
python v15/tools/verify_determinism.py --runs=100
```

---

## 🌐 Distributed Fabric (v18)

### Local 3-Node Simulation

To run a deterministic 3-node consensus simulation:

```bash
# Runs the full cluster simulation in-memory
python v18/tests/test_consensus_simulation.py
```

### Inspecting PQC Anchors

Verify that EvidenceBus segments are correctly anchored:

```bash
# Runs the PQC anchor generation and verification suite
python v18/tests/test_pqc_anchors.py
```

### EvidenceBus Replication

Verify that proposals flow through consensus into EvidenceBus:

```bash
# Tests proposal -> commitment -> bus append
python v18/tests/test_consensus_ebus_integration.py
```

---

## 🚀 Deployment

### Local Beta (Single-Node v17)

```bash
# Set environment to beta
export ENV=beta  # Windows: $env:ENV="beta"
export MOCKQPC_ENABLED=true

# Start all services
./start_beta.sh  # Windows: .\start_beta.bat
```

### Tier A Cluster Deployment (v18 Alpha)

See [V18_DESIGN_AND_DEPLOYMENT.md](./docs/V18_DESIGN_AND_DEPLOYMENT.md) for Tier A clustering instructions.

---

## 🛠️ Troubleshooting

### Windows Troubleshooting

**Issue**: `uvicorn: command not found`

```powershell
# Ensure venv is activated
.\\venv\\Scripts\\activate

# Reinstall uvicorn
pip install uvicorn
```

**Issue**: Port already in use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### macOS/Linux Troubleshooting

**Issue**: `Permission denied` when running scripts

```bash
# Make scripts executable
chmod +x scripts/*.py
chmod +x v15/tools/*.py
```

**Issue**: Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### All Platforms Troubleshooting

**Issue**: Database locked

```bash
# Stop all services
# Delete database file
rm qfs_dev.db  # Windows: del qfs_dev.db

# Reinitialize
python scripts/init_db.py --env=dev
```

---

## 📚 Additional Resources

- [MASTER_PROMPT_v15.5.md](./docs/MASTER_PROMPT_v15.5.md) - Authoritative reference
- [BETA_DEPLOYMENT_PLAN.md](./BETA_DEPLOYMENT_PLAN.md) - Deployment strategy
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [HOW_TO_AUDIT_QFS_V15.md](./HOW_TO_AUDIT_QFS_V15.md) - Audit instructions

---

**QFS × ATLAS**: Cross-platform, deterministic, MOCKQPC-tested. 🚀
