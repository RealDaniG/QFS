# ATLAS Launch Guide (v18.7)

> **Version:** 2.0.0  
> **Date:** 2025-12-20  
> **For:** v18.9 App Alpha with Ascon Auth + ClusterAdapter

## Quick Start

### Default Launch (Cluster Mode)

```cmd
atlas_launch.bat
```

This will:

1. ✅ Validate environment (Python, pip, venv)
2. ✅ Install dependencies
3. ✅ Run v18.6 Auth tests (12 tests)
4. ✅ Run v18.7 ClusterAdapter tests (15 tests)
5. ✅ Start 3-node Raft cluster
6. ✅ Start ATLAS UI (Next.js)

### Single-Node Mode

```cmd
MODE=single atlas_launch.bat
```

Use for lightweight development without cluster overhead.

---

## What's New in v2.0.0

### v18 Support ✅

- **Ascon Stateless Auth**: Validates 12 auth tests before launch
- **ClusterAdapter**: Validates 15 cluster write tests before launch
- **Multi-Node Cluster**: Spins up 3 Raft consensus nodes
- **Test-Driven Launch**: Won't start if critical tests fail

### Improved Error Handling

- **Reusable command runner**: `:run_cmd` function with automatic error detection
- **Non-zero exit codes**: Immediate failure on critical errors
- **Detailed logging**: Every command output captured in `logs/atlas_launch_*.log`
- **Concise summaries**: Clear success/failure for each phase

### Phase Structure

| Phase | Description | Blocking? |
|-------|-------------|-----------|
| 1 | Environment Validation | Yes |
| 2 | Dependency Installation | Yes |
| 3 | Core Tests (v18.6 + v18.7) | Yes |
| 4 | Backend/Cluster Startup | No |
| 5 | ATLAS UI Startup | No |
| 6 | Health Check | No |

---

## Launch Modes

### Cluster Mode (Default)

**When to use:** Full distributed testing, multi-node consensus  
**Ports:** 8001-8003 (cluster nodes), 3000 (UI)  
**Requirements:** v18 consensus module

```cmd
atlas_launch.bat
```

**Expected output:**

```
[SUCCESS] v18.6 Ascon auth tests passed (12/12)
[SUCCESS] v18.7 ClusterAdapter tests passed (15/15)
[SUCCESS] v18 cluster nodes started (3 nodes)
[INFO] Node A (Leader): http://localhost:8001
[INFO] Node B: http://localhost:8002
[INFO] Node C: http://localhost:8003
```

### Single-Node Mode

**When to use:** Quick iteration, UI development, lightweight testing  
**Ports:** 8000 (backend), 3000 (UI)  
**Requirements:** v13 server module

```cmd
MODE=single atlas_launch.bat
```

**Expected output:**

```
[SUCCESS] v18.6 Ascon auth tests passed (12/12)
[SUCCESS] v18.7 ClusterAdapter tests passed (15/15)
[SUCCESS] Single-node backend started
```

---

## Test Requirements

### Critical Tests (Must Pass)

**v18.6 Ascon Auth (12 tests):**

- Token creation and validation
- Multi-node session validation
- Expiry and revocation
- PoE event logging
- Deterministic behavior

**v18.7 ClusterAdapter (15 tests):**

- Leader discovery
- Governance/bounty/chat submissions
- Error handling (NOT_LEADER, timeouts)
- Retry logic
- PoE event logging

**Failure behavior:** Launch aborts with error message pointing to log file.

### Optional Tests (Non-Blocking)

**v14 Social Layer:**

- Spaces, Wall, Chat
- Runs after critical tests
- Warnings logged, launch continues

---

## Troubleshooting

### Launch Fails at Phase 1: Environment

**Error:** `Python not found in PATH`

**Solution:**

```cmd
# Install Python 3.9+ from python.org
# Add to PATH during installation
# Or manually add: C:\Python39\Scripts; to PATH
```

**Error:** `Failed to create virtual environment`

**Solution:**

```cmd
# Manually create venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Launch Fails at Phase 2: Dependencies

**Error:** `Failed to install dependencies`

**Solution:**

```cmd
# Check internet connection
# Update pip
python -m pip install --upgrade pip

# Install manually
pip install pytest requests fastapi uvicorn pydantic cryptography
```

### Launch Fails at Phase 3: Core Tests

**Error:** `v18.6 Ascon session tests failed`

**Check:**

1. Run tests manually: `pytest v18\tests\test_ascon_sessions.py -v`
2. Review output for specific failure
3. Common issues:
   - Missing `v15.evidence.bus` module
   - Import path errors
   - Missing test fixtures

**Error:** `v18.7 ClusterAdapter tests failed`

**Check:**

1. Run tests manually: `pytest v18\tests\test_cluster_adapter.py -v`
2. Review output
3. Common issues:
   - Missing `requests` library
   - Missing `v18.cluster` module
   - Mock setup issues

### Launch Succeeds but Backend Doesn't Start

**Cluster Mode:**

- Check if ports 8001-8003 are available: `netstat -ano | findstr "8001"`
- Verify `v18\consensus\state_machine.py` exists
- Look for backend window errors

**Single Mode:**

- Check if port 8000 is available
- Verify `v13\server.py` exists
- Check backend window for errors

### UI Doesn't Start

**Check:**

1. Verify `v13\atlas\src\package.json` exists
2. Ensure Node.js is installed: `node --version`
3. Check port 3000 availability
4. Look for UI window errors
5. Try manual start:

   ```cmd
   cd v13\atlas\src
   npm install
   npm run dev
   ```

---

## Log Files

### Location

```
logs/atlas_launch_YYYYMMDD_HHMMSS.log
```

### What's Logged

- All command outputs (stdout + stderr)
- Timestamps for each operation
- Success/error markers
- Test results (verbose)
- Backend/UI startup messages

### Reading Logs

**Find last error:**

```cmd
findstr /C:"[ERROR]" logs\atlas_launch_*.log | more
```

**View last launch:**

```cmd
# PowerShell
Get-Content (Get-ChildItem logs\atlas_launch_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

---

##

 Manual Testing Workflow

### 1. Environment Only

```cmd
atlas_launch.bat
# Stop at Phase 1
```

### 2. Tests Only

```cmd
# Skip to tests
cd v18\tests
pytest test_ascon_sessions.py -v
pytest test_cluster_adapter.py -v
```

### 3. Backend Only (Cluster)

```cmd
# Terminal 1: Node A
python -m v18.consensus.state_machine --node-id=node-a --port=8001

# Terminal 2: Node B
python -m v18.consensus.state_machine --node-id=node-b --port=8002

# Terminal 3: Node C
python -m v18.consensus.state_machine --node-id=node-c --port=8003
```

### 4. UI Only

```cmd
cd v13\atlas\src
npm install
npm run dev
```

---

## Configuration

### Environment Variables

```cmd
# Set before running
set MODE=single          # or cluster (default)
set PYTHONPATH=%CD%     # auto-set by launcher
```

### Ports

| Service | Port | Configurable? |
|---------|------|---------------|
| Node A (Leader) | 8001 | Yes (CLI arg) |
| Node B | 8002 | Yes (CLI arg) |
| Node C | 8003 | Yes (CLI arg) |
| ATLAS UI | 3000 | Yes (package.json) |

### Customization

Edit `atlas_launch.bat`:

- Line 17: Change log directory
- Line 19: Change launch mode default
- Lines 186-196: Adjust cluster startup
- Lines 214-227: Adjust UI startup

---

## Expected Behavior

### Successful Launch

```
========================================================================
QFS × ATLAS Platform Launcher v2.0.0 (v18.7)
========================================================================
[INFO] Root Directory: D:\...\QFS\V13\
[INFO] Log File: logs\atlas_launch_20251220_115500.log
[INFO] Launch Mode: cluster

========================================================================
PHASE 1: Environment Validation
========================================================================
[SUCCESS] Found: Python 3.13.7
[SUCCESS] Checking pip installation completed
[SUCCESS] Virtual environment found

========================================================================
PHASE 2: Dependency Installation
========================================================================
[SUCCESS] Installing dependencies completed

========================================================================
PHASE 3: Core Tests (v18 Auth + ClusterAdapter)
========================================================================
[SUCCESS] v18.6 Ascon auth tests passed (12/12)
[SUCCESS] v18.7 ClusterAdapter tests passed (15/15)

========================================================================
PHASE 4: Backend / Cluster Startup (Mode: cluster)
========================================================================
[SUCCESS] v18 cluster nodes started (3 nodes)
[INFO] Node A (Leader): http://localhost:8001
[INFO] Node B: http://localhost:8002
[INFO] Node C: http://localhost:8003

========================================================================
PHASE 5: ATLAS App / UI Startup
========================================================================
[SUCCESS] ATLAS UI dev server starting...
[INFO] UI will be available at: http://localhost:3000

========================================================================
PHASE 6: Post-Launch Health Check
========================================================================
[SUCCESS] Node A is responding

========================================================================
ATLAS PLATFORM LAUNCH SUCCESSFUL ✓
========================================================================

[SUCCESS] All systems operational and validated.

Summary:
  ✓ Environment validated
  ✓ Dependencies installed
  ✓ v18.6 Auth tests passed (12/12)
  ✓ v18.7 ClusterAdapter tests passed (15/15)
  ✓ Backend started (mode: cluster)
  ✓ ATLAS UI starting

Access ATLAS at: http://localhost:3000
```

### Failed Launch

```
========================================================================
PHASE 3: Core Tests (v18 Auth + ClusterAdapter)
========================================================================
[ERROR] v18.6 Ascon session tests failed
[ERROR] Auth layer is broken - cannot proceed
[ERROR] See log file for details: logs\atlas_launch_20251220_115500.log

========================================================================
ATLAS PLATFORM LAUNCH FAILED ✗
========================================================================

[ERROR] Launch aborted due to an error.
[ERROR] See log file for details:
   logs\atlas_launch_20251220_115500.log

Common issues:
  - Python dependencies missing (run: pip install -r requirements.txt)
  - v18 test failures (check test output in log)
  - Port conflicts (8001-8003 for cluster, 3000 for UI)
```

---

## Next Steps After Launch

1. **Access ATLAS UI:** <http://localhost:3000>
2. **Test Wallet Connect:** Click "Connect Wallet" in UI
3. **Verify Ascon Session:** Check DevTools → Network → Authorization header
4. **Submit Governance Action:** Create a proposal, verify cluster commit
5. **Check Logs:** Review `logs/atlas_launch_*.log` for any warnings

---

## References

- [Auth Sync Migration](./docs/AUTH_SYNC_V18_MIGRATION.md)
- [ClusterAdapter Spec](./docs/V18_CLUSTER_ADAPTER_SPEC.md)
- [ATLAS v18 Gap Report](./docs/ATLAS_V18_GAP_REPORT.md)
- [Task Tracker](./task.md)

---

**Maintained by:** QFS × ATLAS Core Team  
**Last Updated:** 2025-12-20
