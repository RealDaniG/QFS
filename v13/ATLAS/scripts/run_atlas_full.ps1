# ATLAS v14 v2 - Unified Launch Orchestrator
$ErrorActionPreference = "Continue" # Allow cleanup to fail gracefully

$ROOT = "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
$LOG_DIR = "$ROOT\logs"
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null }

function Log($msg, $prefix) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] [$prefix] $msg"
    Write-Host $line
    Add-Content -Path "$LOG_DIR\launcher.log" -Value $line
}

# 1. Verification (Cleanup handled by launcher.bat)
Log "Starting ATLAS v14 v2 Orchestration..." "SYSTEM"
Start-Sleep -Seconds 1

# 2. Start Backend (8001)
Log "Starting Backend on :8001..." "BACKEND"
$env:PYTHONPATH = "$ROOT;D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"
$env:PORT = "8001"
$backendProcess = Start-Process python -ArgumentList "src/main_minimal.py" `
    -WorkingDirectory $ROOT `
    -RedirectStandardOutput "$LOG_DIR\backend_stdout.log" `
    -RedirectStandardError "$LOG_DIR\backend_stderr.log" `
    -PassThru -WindowStyle Hidden

# 3. Wait for Backend Health
$healthy = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:8001/health" -TimeoutSec 2
        if ($health.status -eq "ok") {
            Log "Backend is healthy (v$($health.version))." "BACKEND"
            $healthy = $true
            break
        }
    }
    catch {
        Log "Waiting for backend... ($($i+1)/15)" "BACKEND"
        Start-Sleep -Seconds 2
    }
}

if (-not $healthy) {
    Log "BACKEND ERROR: Backend failed to start. Check $LOG_DIR\backend_stderr.log" "ERROR"
    Write-Host "`n[ERROR] Launch sequence aborted." -ForegroundColor Red
    pause
    exit 1
}

# 4. Start Proxy/Frontend (3000)
Log "Starting Proxy Server on :3000..." "FRONTEND"
$proxyProcess = Start-Process python -ArgumentList "scripts/proxy_server.py" `
    -WorkingDirectory $ROOT `
    -RedirectStandardOutput "$LOG_DIR\proxy_stdout.log" `
    -RedirectStandardError "$LOG_DIR\proxy_stderr.log" `
    -PassThru -WindowStyle Hidden

# Wait for Proxy
$proxyUp = $false
for ($i = 0; $i -lt 5; $i++) {
    try {
        $r = Invoke-WebRequest "http://127.0.0.1:3000" -UseBasicParsing -TimeoutSec 1
        if ($r.StatusCode -eq 200) {
            Log "Proxy server is serving." "FRONTEND"
            $proxyUp = $true
            break
        }
    }
    catch {
        Log "Waiting for proxy... ($($i+1)/5)" "FRONTEND"
        Start-Sleep -Seconds 2
    }
}

# 5. Start Electron
Log "Launching Electron (pointing to :3000)..." "ELECTRON"
$env:SKIP_BACKEND = "true"
$env:NODE_ENV = "development" # Forces load of http://127.0.0.1:3000
Start-Process npm -ArgumentList "run dev:web" `
    -WorkingDirectory "$ROOT\desktop" `
    -RedirectStandardOutput "$LOG_DIR\electron_stdout.log" `
    -RedirectStandardError "$LOG_DIR\electron_stderr.log" `
    -WindowStyle Normal

Log "Launch sequence complete." "SYSTEM"
Log "Final checks: Backend=8001, Proxy=3000" "SYSTEM"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ATLAS v14 v2 is now running." -ForegroundColor Green
Write-Host "Monitoring logs in: $LOG_DIR" -ForegroundColor Gray
Write-Host "Press Ctrl+C in the terminal to stop." -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Monitor Backend/Proxy life
while ($true) {
    if ($backendProcess.HasExited) { 
        Log "BACKEND ERROR: Backend process EXITED prematurely." "ERROR"
        Write-Host "`n[ERROR] Backend crashed. Check logs/backend_stderr.log" -ForegroundColor Red
        pause
        break 
    }
    if ($proxyProcess.HasExited) { 
        Log "FRONTEND ERROR: Proxy process EXITED prematurely." "ERROR"
        Write-Host "`n[ERROR] Proxy crashed. Check logs/proxy_stderr.log" -ForegroundColor Red
        pause
        break 
    }
    Start-Sleep -Seconds 5
}
