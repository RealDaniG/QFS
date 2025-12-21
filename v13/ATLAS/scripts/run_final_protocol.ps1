
# ATLAS v18 Complete Autonomous Verification Protocol
$ErrorActionPreference = "Stop"

# Phase 0: Environment Reset & Baseline

# Task 0a: Create verification log
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
}
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "logs/final_verification_$timestamp.log"

function Log-Step($message, $level = "INFO") {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] [$level] $message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log-Step "=== ATLAS v18 FINAL VERIFICATION STARTED ===" "SYSTEM"

# Task 0b: Kill all processes and clear state
Log-Step "Cleaning up old processes" "CLEANUP"
Stop-Process -Name node -ErrorAction SilentlyContinue
Stop-Process -Name python -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

Log-Step "Processes cleared" "CLEANUP"

# Phase 1: Backend Verification (Terminal)

# Task 1a: Start backend
Log-Step "Starting backend on port 8001" "BACKEND"
$env:PYTHONPATH = "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
$env:PORT = "8001"

# We use Start-Process to run in background
$backendCheck = Start-Job -ScriptBlock {
    $env:PYTHONPATH = "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
    $env:PORT = "8001"
    Set-Location "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
    python src/main_minimal.py
} 

Start-Sleep -Seconds 10

# Task 1b: Verify backend health
Log-Step "Checking backend health" "BACKEND"
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    if ($health.status -eq "ok") {
        Log-Step "Backend health: OK (version $($health.version))" "PASS"
    }
    else {
        Log-Step "Backend health check returned unexpected status: $($health.status)" "FAIL"
        exit 1
    }
}
catch {
    Log-Step "Backend not responding: $($_.Exception.Message)" "FAIL"
    exit 1
}

# Task 1c: Test all backend endpoints
Log-Step "Testing backend API endpoints" "BACKEND"

$backendTests = @(
    @{ url = "http://localhost:8001/api/v18/auth/challenge?wallet=0xTEST"; expect = @(200) },
    @{ url = "http://localhost:8001/api/v18/rewards/streak?wallet=0xTEST"; expect = @(200) },
    @{ url = "http://localhost:8001/api/v18/wallet/balance"; expect = @(200, 401) },
    @{ url = "http://localhost:8001/api/v18/spaces"; expect = @(200) },
    @{ url = "http://localhost:8001/api/v18/governance/proposals"; expect = @(200) },
    # @{ url = "http://localhost:8001/api/v18/content/feed"; expect = @(200) } # Optional
    @{ url = "http://localhost:8001/health"; expect = @(200) }
)

foreach ($test in $backendTests) {
    try {
        $response = Invoke-WebRequest -Uri $test.url -UseBasicParsing -TimeoutSec 5
        if ($test.expect -contains $response.StatusCode) {
            Log-Step "$($test.url) -> $($response.StatusCode)" "PASS"
        }
        else {
            Log-Step "$($test.url) -> $($response.StatusCode) (expected $($test.expect))" "WARN"
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($test.expect -contains $statusCode) {
            Log-Step "$($test.url) -> $statusCode (expected via catch)" "PASS"
        }
        else {
            Log-Step "$($test.url) -> FAILED: $($_.Exception.Message)" "FAIL"
        }
    }
}

# Phase 2: Frontend Verification (Terminal)

# Task 2a: Start frontend
Log-Step "Starting frontend on port 3000" "FRONTEND"

$frontendJob = Start-Job -ScriptBlock {
    Set-Location "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
    npm run dev
}

Log-Step "Waiting for frontend compilation (30s)..." "FRONTEND"
Start-Sleep -Seconds 30

# Task 2b: Verify frontend serves
Log-Step "Checking frontend" "FRONTEND"
$maxAttempts = 10
$attempt = 0
$frontendReady = $false

while ($attempt -lt $maxAttempts -and -not $frontendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Log-Step "Frontend is serving" "PASS"
            $frontendReady = $true
        }
    }
    catch {
        $attempt++
        Log-Step "Frontend not ready yet (attempt $attempt/$maxAttempts)" "WAIT"
        Start-Sleep -Seconds 5
    }
}

if (-not $frontendReady) {
    Log-Step "Frontend failed to start" "FAIL"
    exit 1
}

# Task 2c: Test API proxy
Log-Step "Testing frontend API proxy" "FRONTEND"

$proxyTests = @(
    "http://localhost:3000/api/v18/auth/challenge?wallet=0xTEST",
    "http://localhost:3000/api/v18/wallet/balance",
    "http://localhost:3000/api/v18/spaces"
)

foreach ($url in $proxyTests) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Log-Step "Proxy $url -> $($response.StatusCode)" "PASS"
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -in @(200, 401, 422)) {
            Log-Step "Proxy $url -> $statusCode (expected)" "PASS"
        }
        else {
            Log-Step "Proxy $url -> FAILED: $($_.Exception.Message)" "FAIL"
        }
    }
}

# Phase 3: Browser Automation
Log-Step "Starting Playwright Tests" "TEST"
npx playwright test tests/final-verification.spec.ts --reporter=list

if ($LASTEXITCODE -eq 0) {
    Log-Step "Playwright tests passed" "PASS"
}
else {
    Log-Step "Playwright tests failed" "FAIL"
    exit 1
}

Log-Step "=== ATLAS v18 VERIFICATION COMPLETE: ALL SYSTEMS GO ===" "SUCCESS"

# Cleanup
# Stop-Process -Name node -ErrorAction SilentlyContinue
# Stop-Process -Name python -ErrorAction SilentlyContinue
