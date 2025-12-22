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

Write-Host "=== ATLAS v14-v2 Prerequisites Check ===" -ForegroundColor Cyan
Write-Host ""

# 1. Node.js check
Write-Host "Checking Node.js..." -ForegroundColor White
try {
    $node = node --version
    Write-Host "[OK] Node.js $node" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Node.js not found. Install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# 2. Python check
Write-Host "Checking Python..." -ForegroundColor White
try {
    $py = python --version
    Write-Host "[OK] $py" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

# 3. npm packages check
Write-Host "Checking frontend dependencies..." -ForegroundColor White
if (Test-Path "node_modules\@rainbow-me\rainbowkit") {
    Write-Host "[OK] @rainbow-me/rainbowkit installed" -ForegroundColor Green
}
else {
    Write-Host "[WARN] RainbowKit not found. Run: npm install" -ForegroundColor Yellow
}

# 4. Backend dependencies check
Write-Host "Checking backend dependencies..." -ForegroundColor White
try {
    $uvicorn = python -c "import uvicorn; print('ok')" 2>&1
    if ($uvicorn -eq "ok") {
        Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Backend deps may be missing. Run: pip install -r requirements.txt" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[WARN] Could not verify backend dependencies" -ForegroundColor Yellow
}

# 5. Port Checks
Write-Host "Checking port availability..." -ForegroundColor White
if (-not (Check-Port 8001)) { exit 1 }
if (-not (Check-Port 3000)) { exit 1 }
Write-Host "[OK] Ports 8001 and 3000 are available" -ForegroundColor Green

Write-Host ""
Write-Host "=== All Prerequisites OK ===" -ForegroundColor Green
exit 0
