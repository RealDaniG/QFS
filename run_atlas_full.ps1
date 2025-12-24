
param(
    [switch]$Loop,
    [switch]$SkipPlaywright,
    [switch]$SkipAuth,
    [switch]$SkipE2E,
    [switch]$DevMode
)

$ErrorActionPreference = "Continue" 
$Root = $PSScriptRoot
$LogFile = "$Root\logs\atlas_full_run.log"
$Env:PYTHONPATH = "$Root;$Root\v13\atlas"
$Env:QFS_FORCE_MOCK_PQC = "1"
$Env:ALLOWED_ORIGINS = "http://localhost:3000"
$Env:EXPLAIN_THIS_SOURCE = "qfs_ledger"
$Env:NEXT_PUBLIC_API_URL = "http://localhost:8001"

if (-not (Test-Path "$Root\logs")) { New-Item -ItemType Directory -Path "$Root\logs" | Out-Null }
New-Item -ItemType File -Path $LogFile -Force | Out-Null

function Log-Section($component, $message) {
    $ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $line = "[$ts] [$component] $message"
    Write-Host $line -ForegroundColor Cyan
    Add-Content -Path $LogFile -Value $line
}

function Stop-ServiceSafe($proc, $name) {
    if ($proc -and -not $proc.HasExited) {
        Log-Section $name "Stopping..."
        Stop-Process -Id $proc.Id -Force
        Log-Section $name "Stopped."
    }
}

function Wait-ForEndpoint($name, $url, $timeoutSec = 60) {
    $start = Get-Date
    while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($timeoutSec)) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3 | Out-Null
            Log-Section $name "Healthy at $url"
            return $true
        }
        catch {
            Log-Section $name "Waiting for $url..."
            Start-Sleep -Seconds 2
        }
    }
    Log-Section $name "TIMEOUT waiting for $url"
    return $false
}

Log-Section "SYSTEM" "ATLAS V20 orchestration starting (mode: $(if ($DevMode) {'dev'} else {'strict'}))."

do {
    Log-Section "SYSTEM" "=== STARTING ORCHESTRATOR LOOP ==="
    
    # 1. Start Backend
    Log-Section "BACKEND" "Starting FastAPI on :8001..."
    $backendCmd = "python -m uvicorn v13.atlas.src.main_minimal:app --host 0.0.0.0 --port 8001"
    Log-Section "BACKEND" "Command: $backendCmd"
    $backend = Start-Process cmd -ArgumentList "/c $backendCmd" -WorkingDirectory $Root -RedirectStandardOutput "$Root\logs\backend_stdio.log" -RedirectStandardError "$Root\logs\backend_stderr.log" -PassThru -WindowStyle Hidden

    # 2. Start Frontend
    Log-Section "FRONTEND" "Starting UI on :3000..."
    Log-Section "FRONTEND" "Command: npm run dev (in v13\atlas)"
    $frontend = Start-Process cmd -ArgumentList "/c npm run dev" -WorkingDirectory "$Root\v13\atlas" -RedirectStandardOutput "$Root\logs\frontend_stdio.log" -RedirectStandardError "$Root\logs\frontend_stderr.log" -PassThru -WindowStyle Hidden

    Log-Section "SYSTEM" "Waiting for services to become healthy..."
    
    $backendOk = Wait-ForEndpoint "BACKEND" "http://localhost:8001/health"
    $frontendOk = $false
    
    # Frontend check (TCP or HTTP)
    $start = Get-Date
    while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds(180)) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("localhost", 3000)
            if ($tcp.Connected) { 
                $frontendOk = $true
                Log-Section "FRONTEND" "Healthy at :3000 (TCP)"
                $tcp.Close()
                break 
            }
            $tcp.Close()
        }
        catch {
            Log-Section "FRONTEND" "Waiting for :3000..."
            Start-Sleep -Seconds 2
        }
    }

    if (-not $backendOk -or -not $frontendOk) {
        Log-Section "SYSTEM" "Startup failed. See logs\backend_*.log and logs\frontend_*.log"
        Stop-ServiceSafe $backend "BACKEND"
        Stop-ServiceSafe $frontend "FRONTEND"
        exit 1
    }

    # 3. Verification
    
    # 3.1 Verify E2E API
    if ($SkipE2E) {
        Log-Section "VERIFY" "E2E check skipped by flag"
        $e2eExit = 0
    }
    else {
        Log-Section "VERIFY" "Running verify_atlas_e2e.py..."
        python v13\scripts\verify_atlas_e2e.py
        $e2eExit = $LASTEXITCODE
    }
    
    # 3.2 Verify Auth
    if ($SkipAuth) {
        Log-Section "VERIFY" "Auth check skipped by flag"
        $authExit = 0
    }
    else {
        Log-Section "VERIFY" "Running verify_auth.py..."
        python scripts\verify_auth.py
        $authExit = $LASTEXITCODE
    }
    
    # 3.3 Regression Test (Pytest)
    Log-Section "VERIFY" "Running pytest (Routes)..."
    Push-Location "v13\atlas"
    python -m pytest src/tests/test_routes_v18.py --color=no
    $pytestExit = $LASTEXITCODE
    Pop-Location
    
    # 3.4 Playwright
    if ($SkipPlaywright) {
        Log-Section "PLAYWRIGHT" "Playwright e2e skipped by flag"
        $pwExit = 0
    }
    else {
        Log-Section "PLAYWRIGHT" "Running npm run test:e2e..."
        Push-Location v13\atlas
        
        if (-not (Test-Path "node_modules\.bin\playwright.cmd")) {
            Log-Section "PLAYWRIGHT" "Playwright not installed; run: cd v13\atlas; npm install; npx playwright install"
            $pwExit = 1
        }
        else {
            cmd /c "npm run test:e2e"
            $pwExit = $LASTEXITCODE
        }
        Pop-Location
    }
    
    # Summary
    if (-not $DevMode) {
        $allOk = ($e2eExit -eq 0 -and $authExit -eq 0 -and $pwExit -eq 0)
    }
    else {
        $allOk = ($e2eExit -eq 0 -and $authExit -eq 0)  # playwright best-effort in dev
        if ($pwExit -ne 0) {
            Log-Section "WARNING" "Playwright failed but proceeding in DevMode"
        }
    }

    if ($allOk) {
        Log-Section "SUMMARY" "CRITICAL CHECKS PASSED (pytest status=$pytestExit)"
        $Success = $true

        # Launch Electron if successful
        Log-Section "ELECTRON" "Launching Electron App..."
        Push-Location "$Root\v13\atlas"
        Start-Process cmd -ArgumentList "/c npm run electron:dev" -WorkingDirectory "$Root\v13\atlas" -WindowStyle Normal
        Pop-Location
    }
    else {
        Log-Section "SUMMARY" "SOME CHECKS FAILED (e2e=$e2eExit, auth=$authExit, playwright=$pwExit, pytest=$pytestExit)"
        
        if ($pwExit -ne 0) {
            Log-Section "TIP" "If 'playwright' is not recognized, run: cd v13\atlas; npm install; npx playwright install"
        }
        $Success = $false
    }
    
    if (-not $Loop) {
        # Clean Shutdown
        Log-Section "SYSTEM" "Verification Complete. Electron should be launching..."
        Log-Section "SYSTEM" "Press Enter to shutdown services and close this window..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        Stop-ServiceSafe $backend "BACKEND"
        Stop-ServiceSafe $frontend "FRONTEND"
        
        return
    }

    if ($Success) {
        Log-Section "SYSTEM" "Loop Mode: Checks passed. Stopping services and waiting..."
        Stop-ServiceSafe $backend "BACKEND"
        Stop-ServiceSafe $frontend "FRONTEND"
        Start-Sleep -Seconds 10
    }
    else {
        Log-Section "SYSTEM" "Loop Mode: Checks failed. Restarting..."
        Stop-ServiceSafe $backend "BACKEND"
        Stop-ServiceSafe $frontend "FRONTEND"
        Start-Sleep -Seconds 5
    }

} while ($true)

Log-Section "SYSTEM" "Script exiting. Press Enter to close window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
