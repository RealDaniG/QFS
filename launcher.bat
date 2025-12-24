@echo off
echo === Checking Prerequisites ===
powershell -ExecutionPolicy Bypass -File scripts\check_prerequisites.ps1
if errorlevel 1 (
    echo Prerequisites check failed. Fix issues above.
    pause
    exit /b 1
)
echo.
echo === Starting ATLAS v19 (Orchestrator) ===
echo Note: Backend + Frontend + Playwright + Electron
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1 -DevMode
