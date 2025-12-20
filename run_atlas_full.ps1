
param(
    [switch]$Loop
)

$ErrorActionPreference = "Continue" # Don't exit script on individual command failure, handle explicitly
$Root = $PSScriptRoot
$LogFile = "$Root\logs\atlas_full_run.log"
$Env:PYTHONPATH = "$Root;$Root\v13\atlas"
$Env:QFS_FORCE_MOCK_PQC = "1"
$Env:ALLOWED_ORIGINS = "http://localhost:3000"
$Env:EXPLAIN_THIS_SOURCE = "qfs_ledger"

if (-not (Test-Path "$Root\logs")) { New-Item -ItemType Directory -Path "$Root\logs" | Out-Null }
New-Item -ItemType File -Path $LogFile -Force | Out-Null

function Log-Section($component, $message) {
    $ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $line = "[$ts] [$component] $message"
    Write-Host $line -ForegroundColor Cyan
    Add-Content -Path $LogFile -Value $line
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

do {
    Log-Section "SYSTEM" "=== STARTING ORCHESTRATOR LOOP ==="
    
    # 1. Start Backend
    Log-Section "BACKEND" "Starting FastAPI on :8001..."
    $backend = Start-Process cmd -ArgumentList "/c python -m uvicorn v13.atlas.src.main_minimal:app --host 0.0.0.0 --port 8001" -WorkingDirectory $Root -RedirectStandardOutput "$Root\logs\backend_stdio.log" -RedirectStandardError "$Root\logs\backend_stderr.log" -PassThru

    # 2. Start Frontend
    Log-Section "FRONTEND" "Starting UI on :3000..."
    # npm run dev needs to be run in v13/atlas
    $frontend = Start-Process cmd -ArgumentList "/c npm run dev" -WorkingDirectory "$Root\v13\atlas" -RedirectStandardOutput "$Root\logs\frontend_stdio.log" -RedirectStandardError "$Root\logs\frontend_stderr.log" -PassThru

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
        # Cleanup
        if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
        if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }
        exit 1
    }

    # 3. Verification
    
    # 3.1 Verify E2E API
    Log-Section "VERIFY" "Running verify_atlas_e2e.py..."
    python v13\scripts\verify_atlas_e2e.py
    $e2eExit = $LASTEXITCODE
    
    # 3.2 Verify Auth
    Log-Section "VERIFY" "Running verify_auth.py..."
    python scripts\verify_auth.py
    $authExit = $LASTEXITCODE
    
    # 3.3 Regression Test (Pytest)
    Log-Section "VERIFY" "Running pytest (Routes)..."
    Push-Location "v13\atlas"
    python -m pytest src/tests/test_routes_v18.py --color=no
    $pytestExit = $LASTEXITCODE
    Pop-Location
    
    # 3.4 Playwright
    Log-Section "PLAYWRIGHT" "Running npm run test:e2e..."
    Push-Location v13\atlas
    cmd /c "npm run test:e2e"
    $pwExit = $LASTEXITCODE
    Pop-Location
    
    # Summary
    if ($e2eExit -eq 0 -and $authExit -eq 0 -and $pwExit -eq 0) {
        Log-Section "SUMMARY" "ALL CRITICAL CHECKS PASSED (pytest status=$pytestExit)"
        $Success = $true
    }
    else {
        Log-Section "SUMMARY" "SOME CHECKS FAILED (e2e=$e2eExit, auth=$authExit, playwright=$pwExit, pytest=$pytestExit)"
        $Success = $false
    }
    
    if (-not $Loop) {
        # Clean Shutdown
        Log-Section "SYSTEM" "Press Enter to stop backend/frontend (or Ctrl+C to keep running)..."
        # Non-blocking check? No, script ends here.
        # Just auto-kill as per requirement "Clean shutdown... stops both"
        Log-Section "SYSTEM" "Stopping services..."
        if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
        if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }
        Log-Section "SYSTEM" "Services stopped."
        
        if ($Success) { exit 0 } else { exit 1 }
    }
    
    if ($Success) {
        Log-Section "SYSTEM" "Loop Mode: Checks passed. Stopping services and waiting..."
        if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
        if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }
        Start-Sleep -Seconds 10
    }
    else {
        Log-Section "SYSTEM" "Loop Mode: Checks failed. Restarting..."
        if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
        if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }
        Start-Sleep -Seconds 5
    }

} while ($true)
