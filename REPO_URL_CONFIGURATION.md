# IMPORTANT: Repository URL Configuration Required

**Before executing Phase 2 deployment, you MUST update the repository URL.**

## Files Requiring Update

### 1. `scripts/deploy_pqc_linux.sh` (Line 17)

**Current:**
```bash
QFS_REPO_URL="https://github.com/<YOUR_ORG>/QFS-V13.5.git"  # UPDATE THIS
```

**Update to one of:**

#### Option A: GitHub (Recommended)
```bash
QFS_REPO_URL="https://github.com/YourUsername/QFS-V13.5.git"
```

#### Option B: GitLab
```bash
QFS_REPO_URL="https://gitlab.com/YourUsername/QFS-V13.5.git"
```

#### Option C: Bitbucket
```bash
QFS_REPO_URL="https://bitbucket.org/YourUsername/QFS-V13.5.git"
```

#### Option D: Local Transfer (No Git Clone)

If you don't have a remote repository, comment out the git clone and use multipass transfer:

**Modify `deploy_pqc_linux.sh` line 88-95:**
```bash
# Clone QFS V13.5 repository
# if [ ! -d ~/qfs-v13.5 ]; then
#     log_info "Cloning QFS V13.5 repository..."
#     git clone "$QFS_REPO_URL" ~/qfs-v13.5
# else
#     log_warn "QFS V13.5 repository already exists, skipping clone"
# fi

# Replace with manual transfer instructions
log_info "Repository will be transferred via multipass..."
log_info "Run from Windows: multipass transfer -r . qfs-pqc-build:/home/ubuntu/qfs-v13.5"
log_info "Waiting for transfer to complete..."
while [ ! -d ~/qfs-v13.5 ]; do sleep 5; done
log_info "Repository detected, proceeding..."
```

**Then from Windows PowerShell:**
```powershell
cd "d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"
multipass transfer -r . qfs-pqc-build:/home/ubuntu/qfs-v13.5
```

---

## Alternative: Pre-Transfer Workspace

Instead of git clone, transfer the entire Windows workspace:

```powershell
# From Windows
cd "d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"
multipass transfer -r . qfs-pqc-build:/home/ubuntu/qfs-v13.5
```

Then skip the git clone step in the deployment script.

---

## Verification

After updating, verify the URL:

```bash
grep "QFS_REPO_URL" ~/deploy_pqc_linux.sh
```

Expected output (example):
```
QFS_REPO_URL="https://github.com/MyOrg/QFS-V13.5.git"
```

---

**Status:** ⚠️ Configuration required before Phase 2 execution  
**Action Required:** Update repository URL or use manual transfer method
