@echo off
setlocal enabledelayedexpansion
title ATLAS v14-v2 Launcher
color 0A

echo ================================================
echo   ATLAS v14-v2 x QFS - Unified Launcher
echo ================================================
echo.
echo   [1] Normal    - Start full stack
echo   [2] Test      - Run E2E tests only
echo   [3] Cleanup   - Stop all processes
echo   [4] Diagnose  - Run tests then start
echo.
set /p mode="Select mode [1-4, default=1]: "

if "%mode%"=="" set mode=1
if "%mode%"=="1" goto normal
if "%mode%"=="2" goto test_only
if "%mode%"=="3" goto cleanup
if "%mode%"=="4" goto diagnose
goto normal

:cleanup
echo.
echo [CLEANUP] Stopping all ATLAS processes...
powershell -Command "Stop-Process -Name node, python, electron, 'ATLAS v18 Beta' -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo [OK] Cleanup complete.
echo.
pause
exit /b 0

:test_only
echo.
echo [TEST] Running Playwright E2E tests...
echo.
call npx playwright test --project=chromium
echo.
if %errorlevel% neq 0 (
    echo [WARN] Some tests failed. See above for details.
) else (
    echo [OK] All tests passed!
)
pause
exit /b %errorlevel%

:diagnose
echo.
echo [DIAGNOSE] Running E2E tests first...
echo.
call npx playwright test tests/e2e/smoke.spec.ts --project=chromium --workers=1
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Smoke tests failed. Review issues before launching.
    set /p cont="Continue with launch anyway? [y/N]: "
    if /i not "!cont!"=="y" (
        pause
        exit /b 1
    )
)
echo.
goto normal

:normal
echo.
echo ========================================
echo ATLAS v14 v2 - Deterministic Launcher
echo ========================================
echo.

echo [1/3] Cleaning up existing ATLAS processes...
powershell -Command "Stop-Process -Name node, python, electron, 'ATLAS v18 Beta' -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo [OK] Cleanup complete.
echo.

REM Check Prerequisites
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

REM Run Full Launch Orchestration
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
