@echo off
setlocal enabledelayedexpansion

echo ========================================
echo ATLAS v14 v2 - Deterministic Launcher
echo ========================================
echo.

echo [1/3] Cleaning up existing ATLAS processes...
powershell -Command "Stop-Process -Name node, python, electron, 'ATLAS v18 Beta' -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo [OK] Cleanup complete.
echo.

REM 1. Check Prerequisites
echo [2/3] Checking environment prerequisites...
powershell -ExecutionPolicy Bypass -File scripts\check_prerequisites.ps1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Prerequisites check failed. Please resolve above issues and try again.
    pause
    exit /b %errorlevel%
)

echo [OK] Prerequisites validated.
echo.

REM 2. Run Full Launch Orchestration
echo [3/3] Launching ATLAS (Backend, Proxy, Electron)...
powershell -ExecutionPolicy Bypass -File scripts\run_atlas_full.ps1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Launch sequence failed. 
    echo Please check logs in the 'logs' directory.
    pause
    exit /b %errorlevel%
)

exit /b 0
