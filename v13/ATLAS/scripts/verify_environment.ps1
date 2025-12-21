Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ATLAS V18 ENVIRONMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/8] Checking Node.js..." -NoNewline
try {
    $nodeVersion = node --version
    if ($nodeVersion -match "v(\d+)\.") {
        $majorVersion = [int]$matches[1]
        if ($majorVersion -ge 18) {
            Write-Host " ✓ $nodeVersion" -ForegroundColor Green
        }
        else {
            Write-Host " ✗ $nodeVersion (Need v18+)" -ForegroundColor Red
            exit 1
        }
    }
}
catch {
    Write-Host " ✗ Not installed" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "[2/8] Checking Python..." -NoNewline
try {
    $pythonVersion = python --version
    if ($pythonVersion -match "3\.(\d+)\.") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 10) {
            Write-Host " ✓ $pythonVersion" -ForegroundColor Green
        }
        else {
            Write-Host " ✗ $pythonVersion (Need 3.10+)" -ForegroundColor Red
            exit 1
        }
    }
}
catch {
    Write-Host " ✗ Not installed" -ForegroundColor Red
    exit 1
}

# Check npm
Write-Host "[3/8] Checking npm..." -NoNewline
try {
    $npmVersion = npm --version
    Write-Host " ✓ v$npmVersion" -ForegroundColor Green
}
catch {
    Write-Host " ✗ Not installed" -ForegroundColor Red
    exit 1
}

# Check ports availability
Write-Host "[4/8] Checking port 3000..." -NoNewline
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host " ✗ In use (PID: $($port3000.OwningProcess))" -ForegroundColor Red
    Write-Host "    Run: taskkill /F /PID $($port3000.OwningProcess)"
}
else {
    Write-Host " ✓ Available" -ForegroundColor Green
}

Write-Host "[5/8] Checking port 8000..." -NoNewline
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host " ✗ In use (PID: $($port8000.OwningProcess))" -ForegroundColor Red
    Write-Host "    Run: taskkill /F /PID $($port8000.OwningProcess)"
}
else {
    Write-Host " ✓ Available" -ForegroundColor Green
}

# Check project directory
Write-Host "[6/8] Checking project structure..." -NoNewline
$requiredDirs = @("src", "backend", "public")
$missing = @()
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missing += $dir
    }
}
if ($missing.Count -gt 0) {
    Write-Host " ✗ Missing: $($missing -join ', ')" -ForegroundColor Red
    exit 1
}
else {
    Write-Host " ✓ Complete" -ForegroundColor Green
}

# Check dependencies installed
Write-Host "[7/8] Checking node_modules..." -NoNewline
if (Test-Path "node_modules") {
    Write-Host " ✓ Installed" -ForegroundColor Green
}
else {
    Write-Host " ✗ Not installed. Run: npm install" -ForegroundColor Red
    exit 1
}

Write-Host "[8/8] Checking Python packages..." -NoNewline
$pipCheck = pip list 2>&1 | Select-String "fastapi|uvicorn|pydantic"
if ($pipCheck) {
    Write-Host " ✓ Installed" -ForegroundColor Green
}
else {
    Write-Host " ✗ Not installed. Run: pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment verification complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
