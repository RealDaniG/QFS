@echo off
REM ==========================================================
REM ATLAS Desktop Dev Launcher with Full Error Logging
REM ==========================================================

REM Define log file
set LOG_FILE=%~dp0dev_logs.txt

REM Clear previous logs
if exist "%LOG_FILE%" del "%LOG_FILE%"

echo [INFO] Starting ATLAS desktop dev environment >> "%LOG_FILE%"
echo [%DATE% %TIME%] ========================================== >> "%LOG_FILE%"

REM Kill any existing Python backend (port 8000)
echo [%DATE% %TIME%] [INFO] Checking for existing Python backend... >> "%LOG_FILE%"
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL%==0 (
    echo [%DATE% %TIME%] [INFO] Terminating existing Python processes... >> "%LOG_FILE%"
    taskkill /F /IM python.exe >> "%LOG_FILE%" 2>&1
    echo [%DATE% %TIME%] [INFO] Python backend terminated. >> "%LOG_FILE%"
    timeout /t 2 /nobreak >nul
) else (
    echo [%DATE% %TIME%] [INFO] No existing Python backend found. >> "%LOG_FILE%"
)

REM Launch Python backend and redirect stdout/stderr
echo [%DATE% %TIME%] [INFO] Launching backend from ..\backend\main.py... >> "%LOG_FILE%"
start "" /B cmd /C "python ..\backend\main.py >> "%LOG_FILE%" 2>&1"

REM Wait 3 seconds for backend to initialize
echo [%DATE% %TIME%] [INFO] Waiting for backend to start... >> "%LOG_FILE%"
timeout /t 3 /nobreak >nul

REM Check if backend started successfully
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [%DATE% %TIME%] [SUCCESS] Backend is running on port 8000 >> "%LOG_FILE%"
) else (
    echo [%DATE% %TIME%] [WARNING] Backend health check failed - check logs above >> "%LOG_FILE%"
)

REM Launch Electron frontend and redirect stdout/stderr
echo [%DATE% %TIME%] [INFO] Launching Electron... >> "%LOG_FILE%"
start "" /B cmd /C "electron . >> "%LOG_FILE%" 2>&1"

echo.
echo ========================================================
echo ATLAS Desktop Dev Environment Started
echo ========================================================
echo Backend: http://localhost:8000
echo Logs: %~dp0dev_logs.txt
echo.
echo Press Ctrl+C to stop, or close this window.
echo ========================================================
echo.

REM Keep window open to show status
pause
