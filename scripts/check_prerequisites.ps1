# check_prerequisites.ps1
$ErrorActionPreference = "Stop"

Write-Host "=== ATLAS v18 Prerequisite Check ===" -ForegroundColor Cyan

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "❌ Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
$npmVersion = npm --version 2>$null
if (-not $npmVersion) {
    Write-Host "❌ npm not found." -ForegroundColor Red
    exit 1
}
Write-Host "✅ npm: $npmVersion" -ForegroundColor Green

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "❌ Python not found. Install from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green

# Frontend dependencies check
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
$atlasDir = Join-Path $PSScriptRoot "v13\atlas"
if (-not (Test-Path $atlasDir)) {
    # Fallback to current dir if script is run from project root and structure is different
    $atlasDir = "v13\atlas"
}
cd $atlasDir

if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  node_modules missing. Running npm install..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}
else {
    Write-Host "✅ node_modules present" -ForegroundColor Green
}

# Check for wagmi, viem, rainbowkit
$packageJson = Get-Content package.json | ConvertFrom-Json
$requiredPackages = @("wagmi", "viem", "@rainbow-me/rainbowkit")
foreach ($pkg in $requiredPackages) {
    if (-not $packageJson.dependencies.$pkg) {
        Write-Host "⚠️  $pkg missing. Installing..." -ForegroundColor Yellow
        npm install $pkg --legacy-peer-deps
    }
    else {
        Write-Host "✅ $pkg installed" -ForegroundColor Green
    }
}

# Backend dependencies check
Write-Host "Checking backend dependencies..." -ForegroundColor Yellow
cd ..\..
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
}

Write-Host "`n=== All Prerequisites OK ===" -ForegroundColor Cyan
