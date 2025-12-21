Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION AUDIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check .env.local exists
Write-Host "[1/5] Checking .env.local..." -NoNewline
if (Test-Path ".env.local") {
    Write-Host " ✓ Found" -ForegroundColor Green
    
    $envContent = Get-Content ".env.local" -Raw
    
    # Check WalletConnect Project ID
    Write-Host "[2/5] Checking WalletConnect Project ID..." -NoNewline
    if ($envContent -match "NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=(.+)") {
        $projectId = $matches[1].Trim()
        if ($projectId -eq "v18-atlas-project-id" -or $projectId -eq "") {
            Write-Host " ✗ Using placeholder/empty" -ForegroundColor Red
            Write-Host "    Action Required: Get real ID from https://cloud.walletconnect.com/"
            Write-Host "    This is causing the 403 Forbidden errors!"
        }
        else {
            Write-Host " ✓ Configured ($projectId)" -ForegroundColor Green
        }
    }
    else {
        Write-Host " ✗ Not found" -ForegroundColor Red
    }
    
    # Check API URL
    Write-Host "[3/5] Checking API URL..." -NoNewline
    if ($envContent -match "NEXT_PUBLIC_API_URL=(.+)") {
        $apiUrl = $matches[1].Trim()
        Write-Host " ✓ $apiUrl" -ForegroundColor Green
    }
    else {
        Write-Host " ⚠ Not set (using default)" -ForegroundColor Yellow
    }
    
}
else {
    Write-Host " ✗ Missing" -ForegroundColor Red
    Write-Host "    Creating template..."
    
    $template = @"
# WalletConnect Configuration
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_project_id_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Chain Configuration
NEXT_PUBLIC_ENABLE_TESTNETS=true
"@
    
    Set-Content -Path ".env.local" -Value $template
    Write-Host "    ✓ Template created. Please update values." -ForegroundColor Green
}

# Check next.config.mjs
Write-Host "[4/5] Checking next.config.mjs..." -NoNewline
if (Test-Path "next.config.mjs") {
    Write-Host " ✓ Found" -ForegroundColor Green
    $configContent = Get-Content "next.config.mjs" -Raw
    
    # Check for rewrites
    if ($configContent -match "rewrites") {
        Write-Host "    ✓ API rewrites configured" -ForegroundColor Green
    }
    else {
        Write-Host "    ⚠ No rewrites found (may cause CORS issues)" -ForegroundColor Yellow
    }
}
else {
    Write-Host " ✗ Missing" -ForegroundColor Red
}

# Check backend config
Write-Host "[5/5] Checking backend/main.py..." -NoNewline
if (Test-Path "backend/main.py") {
    Write-Host " ✓ Found" -ForegroundColor Green
    $backendContent = Get-Content "backend/main.py" -Raw
    
    # Check CORS configuration
    if ($backendContent -match "CORSMiddleware") {
        Write-Host "    ✓ CORS middleware configured" -ForegroundColor Green
    }
    else {
        Write-Host "    ✗ CORS not configured (will cause fetch errors)" -ForegroundColor Red
    }
}
else {
    Write-Host " ✗ Missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
