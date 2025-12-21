@echo off
echo ========================================
echo ATLAS v19 / v14 v2 Launcher
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "backend\main.py" (
    echo ERROR: backend\main.py not found!
    echo Please run this script from the ATLAS root directory.
    pause
    exit /b 1
)

if not exist "desktop\main.js" (
    echo ERROR: desktop\main.js not found!
    echo Please run this script from the ATLAS root directory.
    pause
    exit /b 1
)

echo [1/3] Starting Python Backend...
echo.
start "ATLAS Backend" cmd /k "cd /d %~dp0 && set PYTHONPATH=%~dp0..\..;%~dp0;%PYTHONPATH% && python -m src.main_minimal"

REM Wait for backend to initialize
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Checking Backend Health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend is running!
) else (
    echo WARNING: Backend health check failed. Continuing anyway...
)

echo.
echo [3/3] Starting Desktop App...
echo.
cd desktop
start "ATLAS Desktop" cmd /k "set SKIP_BACKEND=true && npm run dev"
cd ..

echo.
echo ========================================
echo ATLAS Launched Successfully!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Desktop: Electron window should open
echo.
echo Press any key to exit this launcher...
pause >nul
