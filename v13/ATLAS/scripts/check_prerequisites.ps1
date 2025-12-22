# ATLAS v14 v2 - Prerequisites Check
$ErrorActionPreference = "Stop"

function Check-Port($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "[ERROR] Port $port is already in use by PID $($conn.OwningProcess)." -ForegroundColor Red
        return $false
    }
    return $true
}

Write-Host "--- Checking Prerequisites ---" -ForegroundColor Cyan

# 1. Node.js check
try {
    $node = node --version
    Write-Host "[OK] Node.js $node found." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Node.js not found." -ForegroundColor Red
    exit 1
}

# 2. Python check
try {
    $py = python --version
    Write-Host "[OK] $py found." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python not found." -ForegroundColor Red
    exit 1
}

# 3. Port Checks (Fail if ports are held by non-ATLAS processes)
# Note: we will kill leftover ATLAS processes in run_atlas_full.ps1, 
# but this check is for general hygiene.
if (-not (Check-Port 8001)) { exit 1 }
if (-not (Check-Port 3000)) { exit 1 }

Write-Host "[OK] All prerequisites met." -ForegroundColor Green
exit 0
