# ATLAS v18 — Final Autonomous Verification & Fix Protocol
$ErrorActionPreference = "Stop"

# Step 1: Backend Health Check (Terminal)

# Start fresh
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Force -Path "logs" | Out-Null }
$logFile = "logs/final_verification_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

function Log($msg, $level = "INFO") {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] [$level] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log "=== STARTING FINAL VERIFICATION ===" "SYSTEM"

# Kill old processes
Stop-Process -Name node, python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Start backend
Log "Starting backend on :8001" "BACKEND"
$env:PYTHONPATH = "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13;D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
$env:PORT = "8001"

$backend = Start-Process python -ArgumentList "src/main_minimal.py" `
    -WorkingDirectory "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas" `
    -RedirectStandardOutput "logs\backend_std.log" `
    -RedirectStandardError "logs\backend_err.log" `
    -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 10

# Test health
try {
    $health = Invoke-RestMethod "http://localhost:8001/health"
    if ($health.status -eq "ok") {
        Log "Backend healthy (v$($health.version))" "PASS"
    }
}
catch {
    Log "Backend FAILED: $($_.Exception.Message)" "FAIL"
    exit 1
}

# Test all critical endpoints
$endpoints = @(
    "/api/v18/auth/challenge?wallet=0xTEST",
    "/api/v18/rewards/streak?wallet=0xTEST",
    "/api/v18/wallet/balance",
    "/api/v18/spaces",
    "/api/v18/governance/proposals"
)

foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest "http://localhost:8001$ep" -UseBasicParsing -TimeoutSec 5
        Log "$ep -> $($r.StatusCode)" "PASS"
    }
    catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -in @(401, 422)) {
            Log "$ep -> $code (expected without auth)" "PASS"
        }
        else {
            Log "$ep -> FAIL ($($_.Exception.Message))" "FAIL"
        }
    }
}

# Step 2: Frontend & Proxy Check

# Check if port 3000 is occupied
$port3000 = netstat -ano | findstr ":3000"
if ($port3000) {
    try {
        $pidToKill = ($port3000.Trim() -split '\s+')[-1]
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
        Log "Killed existing process on port 3000" "INFO"
    }
    catch {
        Log "Could not kill process on port 3000: $_" "WARN"
    }
}

Log "Starting frontend on :3000 (Visible Window)" "FRONTEND"
Set-Location "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd 'D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas'; npm run start"

Log "Waiting 120 seconds for compilation..." "WAIT"
Start-Sleep -Seconds 120

# Check frontend serves
$attempt = 0
while ($attempt -lt 10) {
    try {
        $r = Invoke-WebRequest "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) {
            Log "Frontend serving" "PASS"
            break
        }
    }
    catch {
        $attempt++
        Log "Waiting for frontend... ($attempt/10)" "WAIT"
        Start-Sleep -Seconds 5
    }
}

if ($attempt -eq 10) {
    Log "Frontend failed to start" "FAIL"
    exit 1
}

# Test proxy
$proxyTests = @(
    "/api/v18/auth/challenge?wallet=0xTEST",
    "/api/v18/spaces"
)

foreach ($ep in $proxyTests) {
    try {
        $r = Invoke-WebRequest "http://localhost:3000$ep" -UseBasicParsing
        Log "Proxy $ep -> $($r.StatusCode)" "PASS"
    }
    catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -in @(401, 422, 200)) {
            Log "Proxy $ep -> $code (expected)" "PASS"
        }
        else {
            Log "Proxy $ep -> FAIL ($($_.Exception.Message))" "FAIL"
        }
    }
}

# Step 3: Browser E2E Verification

Log "Running Playwright E2E tests" "E2E"

try {
    $result = npm run test:e2e 2>&1
    $result | Out-File -Append $logFile
    Log "Playwright execution completed" "INFO"
    
    if ($LASTEXITCODE -eq 0) {
        Log "Playwright tests PASSED" "PASS"
    }
    else {
        Log "Playwright tests FAILED" "FAIL"
        # don't exit, allow for manual check
    }
}
catch {
    Log "Playwright failed to run: $_" "FAIL"
}

Log "=== VERIFICATION COMPLETE ===" "SYSTEM"
Log "Check $logFile for full results" "SYSTEM"
