# QFS × ATLAS — Cross-Platform Development Guide

> **Version:** v15.5  
> **Platforms:** Windows, macOS, Linux  
> **Updated:** December 19, 2025

---

## 🎯 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** (for ATLAS frontend)
- **Git**
- **4GB RAM minimum**

---

## 🪟 Windows Setup

### 1. Install Dependencies

```powershell
# Install Python from python.org
# Install Node.js from nodejs.org
# Install Git from git-scm.com

# Verify installations
python --version
node --version
git --version
```

### 2. Clone Repository

```powershell
git clone https://github.com/RealDaniG/QFS.git
cd QFS\v13
```

### 3. Backend Setup

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

### 4. Frontend Setup

```powershell
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. MOCKQPC Service

```powershell
# Open new terminal
cd v15\mockqpc
python service.py --port 8001
```

---

## 🍎 macOS Setup

### 1. Install Dependencies

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

### 2. Clone Repository

```bash
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13
```

### 3. Backend Setup

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

### 4. Frontend Setup

```bash
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. MOCKQPC Service

```bash
# Open new terminal
cd v15/mockqpc
python service.py --port 8001
```

---

## 🐧 Linux Setup

### 1. Install Dependencies

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

### 2. Clone Repository

```bash
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13
```

### 3. Backend Setup

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

### 4. Frontend Setup

```bash
# Open new terminal
cd atlas
npm install
npm run dev
```

### 5. MOCKQPC Service

```bash
# Open new terminal
cd v15/mockqpc
python service.py --port 8001
```

---

## 🐳 Docker Setup (All Platforms)

### 1. Install Docker

- **Windows**: Docker Desktop from docker.com
- **macOS**: Docker Desktop from docker.com
- **Linux**: `sudo apt install docker.io docker-compose` (or equivalent)

### 2. Build and Run

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
pytest v17\tests\
pytest v13\tests\

# macOS/Linux/GitBash
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

# macOS/Linux

pytest v13/tests/

```

### Run Specific Test Suites

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

## 🔐 MOCKQPC Verification

### Generate Test Events

```bash
# Windows
python scripts\seed_content.py --count=50 --env=dev

# macOS/Linux
python scripts/seed_content.py --count=50 --env=dev
```

### Verify Hash Chains

```bash
# Windows
python v15\tools\verify_poe.py --env=dev

# macOS/Linux
python v15/tools/verify_poe.py --env=dev
```

### Generate Replay Bundle

```bash
# Windows
python v15\tools\generate_replay_bundle.py --output=replay_bundle.zip

# macOS/Linux
python v15/tools/generate_replay_bundle.py --output=replay_bundle.zip
```

---

## 📊 Cost Metrics

### Track PQC Calls

```bash
# Windows
python scripts\cost_metrics.py --metric=pqc_calls

# macOS/Linux
python scripts/cost_metrics.py --metric=pqc_calls
```

### Track Agent Calls

```bash
# Windows
python scripts\cost_metrics.py --metric=agent_calls

# macOS/Linux
python scripts/cost_metrics.py --metric=agent_calls
```

### Generate Cost Report

```bash
# Windows
python scripts\cost_metrics.py --report --output=cost_report.json

# macOS/Linux
python scripts/cost_metrics.py --report --output=cost_report.json
```

---

## 🚀 Beta Deployment

### Local Beta (Single-Node)

```bash
# Set environment to beta
export ENV=beta  # Windows: $env:ENV="beta"
export MOCKQPC_ENABLED=true

# Start all services
./start_beta.sh  # Windows: .\start_beta.bat
```

### Production Deployment

See [BETA_DEPLOYMENT_PLAN.md](./BETA_DEPLOYMENT_PLAN.md) for complete instructions.

---

## 🛠️ Troubleshooting

### Windows

**Issue**: `uvicorn: command not found`

```powershell
# Ensure venv is activated
.\venv\Scripts\activate

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

### macOS/Linux

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

### All Platforms

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
