# Full ATLAS v18 Verification Script
$ErrorActionPreference = "Stop"

Write-Host "=== ATLAS v18 Full System Verification ===" -ForegroundColor Cyan

# 1. Kill old processes
Write-Host "`nCleaning up old processes..." -ForegroundColor Yellow
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. Start backend
Write-Host "`nStarting backend on port 8001..." -ForegroundColor Yellow

$env:PYTHONPATH = "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"
Start-Process python -ArgumentList "src/main_minimal.py" -WorkingDirectory (Get-Location) -WindowStyle Hidden
Start-Sleep -Seconds 5

# 3. Verify backend
Write-Host "Checking backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health"
    if ($health.status -eq "ok") {
        Write-Host "✅ Backend healthy" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Backend not responding" -ForegroundColor Red
    # Don't exit, just warn for now to see if frontend works
}

# 4. Start frontend
Write-Host "`nStarting frontend on port 3000..." -ForegroundColor Yellow
Start-Process npm -ArgumentList "run dev" -WorkingDirectory (Get-Location) -WindowStyle Hidden
Start-Sleep -Seconds 20

# 5. Verify frontend
Write-Host "Checking frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($frontend.StatusCode -eq 200) {
        Write-Host "✅ Frontend serving" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Frontend not reachable" -ForegroundColor Red
    exit 1
}

# 6. Test API endpoints (via proxy)
Write-Host "`nTesting API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    "/api/v18/auth/challenge?wallet=0xTEST",
    "/api/v18/wallet/balance"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000$endpoint" -UseBasicParsing
        Write-Host "✅ $endpoint" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $endpoint FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== Servers Running ===" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8001" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "`nNow test manually in browser:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3000" -ForegroundColor White
Write-Host "2. Click 'Connect Wallet'" -ForegroundColor White
Write-Host "3. Connect MetaMask" -ForegroundColor White
Write-Host "4. Click 'Sign to Continue' (Manual Auth Trigger)" -ForegroundColor White
Write-Host "5. Sign message" -ForegroundColor White
Write-Host "6. Dashboard should unlock" -ForegroundColor White
Write-Host "`nPress Enter to stop servers..." -ForegroundColor Yellow
Read-Host

# Cleanup
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue
