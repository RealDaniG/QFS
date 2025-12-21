Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKEND STANDALONE TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Write-Host "Cleaning up existing processes..." -NoNewline
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
Write-Host " ✓" -ForegroundColor Green

# Start backend
Write-Host "Starting backend on port 8000..." -NoNewline
$backendProcess = Start-Process python -ArgumentList "backend/main.py" -PassThru -NoNewWindow
Start-Sleep -Seconds 5

if ($backendProcess.HasExited) {
    Write-Host " ✗ Failed to start" -ForegroundColor Red
    exit 1
}
Write-Host " ✓ PID: $($backendProcess.Id)" -ForegroundColor Green

# Test health endpoint
Write-Host ""
Write-Host "Testing endpoints:" -ForegroundColor Yellow
Write-Host ""

$endpoints = @(
    @{Path = "/health"; Expected = 200; Critical = $true },
    @{Path = "/api/wallet/balance"; Expected = 200; Critical = $false },
    @{Path = "/api/cycles/current"; Expected = 200; Critical = $false },
    @{Path = "/api/rewards/summary"; Expected = 200; Critical = $false }
)

$allPassed = $true

foreach ($endpoint in $endpoints) {
    Write-Host "  Testing $($endpoint.Path)..." -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$($endpoint.Path)" `
            -Method GET `
            -TimeoutSec 5 `
            -UseBasicParsing
        
        if ($response.StatusCode -eq $endpoint.Expected) {
            Write-Host " ✓ $($response.StatusCode)" -ForegroundColor Green
            
            # Show response body for health check
            if ($endpoint.Path -eq "/health") {
                $json = $response.Content | ConvertFrom-Json
                Write-Host "    Status: $($json.status)" -ForegroundColor Cyan
            }
        }
        else {
            Write-Host " ⚠ $($response.StatusCode) (expected $($endpoint.Expected))" -ForegroundColor Yellow
            if ($endpoint.Critical) { $allPassed = $false }
        }
    }
    catch {
        Write-Host " ✗ $($_.Exception.Message)" -ForegroundColor Red
        if ($endpoint.Critical) { $allPassed = $false }
    }
}

Write-Host ""

if ($allPassed) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Backend verification PASSED" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
}
else {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Backend verification FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Backend is running. Press Ctrl+C to stop."
Write-Host ""

# Keep running
# Wait-Process -Id $backendProcess.Id
# Manually stopping for automation flow
Stop-Process -Id $backendProcess.Id -Force
Write-Host "Backend stopped." -ForegroundColor Yellow
