
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$LogFile = "$Root\logs\full_verification.log"
$Env:PYTHONPATH = "$Root;$Root\v13\atlas"
$Env:QFS_FORCE_MOCK_PQC = "1"

if (-not (Test-Path "$Root\logs")) { New-Item -ItemType Directory -Path "$Root\logs" | Out-Null }

function Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $msg"
    Write-Host $line -ForegroundColor Cyan
    Add-Content -Path $LogFile -Value $line
}

Log "=== STARTING FULL VERIFICATION LOOP ==="

# 1. Start Backend
Log "Starting Backend (start_backend_v18.bat)..."
Start-Process "$Root\start_backend_v18.bat" -PassThru

# 2. Start Frontend
Log "Starting Frontend (npm run dev)..."
$FrontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd v13\atlas && npm run dev" -PassThru

# 3. Wait for Services
Log "Waiting for Backend (8001) and Frontend (3000)..."
$BackendReady = $false
$FrontendReady = $false

for ($i = 0; $i -lt 30; $i++) {
    if (-not $BackendReady) {
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) { $BackendReady = $true; Log "Backend is UP." }
        }
        catch {}
    }
    if (-not $FrontendReady) {
        try {
            # Frontend might return 200 or 404 on root, checking port
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("localhost", 3000)
            if ($tcp.Connected) { $FrontendReady = $true; Log "Frontend is UP." }
            $tcp.Close()
        }
        catch {}
    }
    if ($BackendReady -and $FrontendReady) { break }
    Start-Sleep -Seconds 2
}

if (-not $BackendReady) { Log "ERROR: Backend failed to start."; exit 1 }
if (-not $FrontendReady) { Log "ERROR: Frontend failed to start."; exit 1 }

# 4. Run Verification Scripts

# 4.1 E2E API
Log "Running verify_atlas_e2e.py..."
try {
    python v13\scripts\verify_atlas_e2e.py
    if ($LASTEXITCODE -ne 0) { throw "ExitCode $LASTEXITCODE" }
    Log "verify_atlas_e2e.py PASSED"
}
catch {
    Log "ERROR: verify_atlas_e2e.py FAILED"
    exit 1
}

# 4.2 Auth
Log "Running verify_auth.py..."
try {
    python scripts\verify_auth.py
    if ($LASTEXITCODE -ne 0) { throw "ExitCode $LASTEXITCODE" }
    Log "verify_auth.py PASSED"
}
catch {
    Log "ERROR: verify_auth.py FAILED"
    exit 1
}

# 4.3 Regression Test (Pytest)
Log "Running pytest (test_routes_v18.py)..."
try {
    # Ensure color is off for cleaner log
    python -m pytest v13/atlas/src/tests/test_routes_v18.py --color=no
    if ($LASTEXITCODE -ne 0) { throw "ExitCode $LASTEXITCODE" }
    Log "pytest PASSED"
}
catch {
    Log "ERROR: pytest FAILED"
    exit 1
}

# 4.4 Playwright
Log "Running Playwright E2E..."
Push-Location v13\atlas
try {
    npm run test:e2e
    if ($LASTEXITCODE -ne 0) { throw "ExitCode $LASTEXITCODE" }
    Log "Playwright PASSED"
}
catch {
    Log "ERROR: Playwright FAILED"
    Pop-Location
    exit 1
}
Pop-Location

Log "=== VERIFICATION COMPLETE: ALL CHECKS PASSED ==="
Log "[RESULT] pytest=OK, e2e=OK, auth=OK, playwright=OK"
exit 0
