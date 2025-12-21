Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ATLAS v18 PERFORMANCE MONITOR" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:3000"

# Warm up
Write-Host "Warming up..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 60 | Out-Null
}
catch {
    Write-Host "Warm up failed. Server might be down." -ForegroundColor Red
}

Write-Host "Running performance tests..." -ForegroundColor Yellow
Write-Host ""

# Test 5 requests
$times = @()
for ($i = 1; $i -le 5; $i++) {
    $start = Get-Date
    try {
        Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 10 | Out-Null
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $times += $duration
        Write-Host "Request $i : " -NoNewline
        Write-Host "$([math]::Round($duration, 2))ms" -ForegroundColor Green
    }
    catch {
        Write-Host "Request $i : FAILED" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
if ($times.Count -gt 0) {
    $avg = ($times | Measure-Object -Average).Average
    Write-Host "Average Response Time: $([math]::Round($avg, 2))ms" -ForegroundColor $(if ($avg -lt 200) { 'Green' } else { 'Yellow' })
}
Write-Host "Target: <200ms for optimal performance" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
