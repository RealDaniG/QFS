@echo off
echo === Checking Prerequisites ===
powershell -ExecutionPolicy Bypass -File scripts\check_prerequisites.ps1
if errorlevel 1 (
    echo Prerequisites check failed. Fix issues above.
    pause
    exit /b 1
)
echo.
echo === Ensuring Electron App Dependencies ===
cd v13\atlas\desktop
call npm install --silent
cd ..\..\..
echo.
echo === Starting ATLAS v20 (Orchestrator) ===
echo Note: Backend + Frontend + Playwright + Electron
echo GitHub Integration & Retro Rewards enabled.
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1 -DevMode

