@echo off
echo === Checking Prerequisites ===
powershell -ExecutionPolicy Bypass -File scripts\check_prerequisites.ps1
if errorlevel 1 (
    echo Prerequisites check failed. Fix issues above.
    pause
    exit /b 1
)
echo.
echo 5 - v20 Auth Full - Run v20 Full Stack (New)

set /p mode="Select mode (1-5, default=1): "
if "%mode%"=="" set mode=1

if "%mode%"=="1" goto normal
if "%mode%"=="2" goto testonly
if "%mode%"=="3" goto cleanup
if "%mode%"=="4" goto diagnose
if "%mode%"=="5" goto v20full
goto normal

:v20full
echo.
echo === Starting v20 Full Stack (with Auth) ===
call launch_atlas_v20_full.bat
exit /b 0

:normal
echo === Ensuring Electron App Dependencies ===
cd v13\atlas\desktop
call npm install --silent
cd ..\..\..
echo.
echo === Starting ATLAS v20 (Orchestrator) ===
echo Note: Backend + Frontend + Playwright + Electron
echo GitHub Integration + Retro Rewards enabled.
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1 -DevMode

