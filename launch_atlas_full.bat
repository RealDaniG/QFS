@echo off
:: ATLAS Complete Stack Launcher
:: robust startup with health checks, logging, and environment isolation
:: Usage: launch_atlas_full.bat [test]

set "ROOTDIR=%~dp0"
set "PYTHONPATH=%ROOTDIR%"
set "QFS_FORCE_MOCK_PQC=1"
set "EXPLAIN_THIS_SOURCE=qfs_ledger"

echo ============================================================
echo ATLAS v18.9 Complete Stack Launcher
echo ============================================================
echo.

:: Ensure log directory exists
if not exist "%ROOTDIR%logs" mkdir "%ROOTDIR%logs"

:: Start Backend
echo [1/3] Starting Backend API Server (Port 8001)...
echo Logs: %ROOTDIR%logs\backend_stdio.log
start "ATLAS Backend" cmd /c "cd /d %ROOTDIR%v13\atlas && set PYTHONPATH=%ROOTDIR% && python -m uvicorn src.main_minimal:app --host 0.0.0.0 --port 8001 > ..\..\logs\backend_stdio.log 2>&1"

:: Wait for Backend Healthy
:wait_backend
echo Waiting for backend health (http://localhost:8001/health)...
powershell -Command "try { Invoke-WebRequest -UseBasicParsing http://localhost:8001/health | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  timeout /t 2 /nobreak >nul
  goto wait_backend
)
echo Backend is UP.

:: Start Frontend
echo [2/3] Starting Frontend UI (Port 3000)...
echo Logs: %ROOTDIR%logs\frontend_dev.log
start "ATLAS Frontend" cmd /c "cd /d %ROOTDIR%v13\atlas && npm run dev > ..\..\logs\frontend_dev.log 2>&1"

:: Wait for Frontend Healthy
:wait_frontend
echo Waiting for frontend (http://localhost:3000)...
powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient; $tcp.Connect('localhost', 3000); $tcp.Close(); exit 0 } catch { exit 1 }"
if errorlevel 1 (
  timeout /t 2 /nobreak >nul
  goto wait_frontend
)
echo Frontend is UP.

echo.
echo ============================================================
echo [3/3] System Verified.
echo ============================================================

:: Optional Test Mode
if /I "%1"=="test" (
  echo Running Backend Verification...
  python v13\scripts\verify_atlas_e2e.py || echo [WARN] verify_atlas_e2e failed
  python scripts\verify_auth.py || echo [WARN] verify_auth failed
  
  echo Running E2E Tests...
  cd v13\atlas
  npm run test:e2e
  cd ..\..
) else (
  :: Standard Launch - Open Dashboards
  start http://localhost:8001/api/docs
  timeout /t 2 /nobreak >nul
  start http://localhost:3000
)

echo.
echo ============================================================
echo ATLAS Stack is Running!
echo ============================================================
echo.
echo  Backend API:  http://localhost:8001
echo  API Docs:     http://localhost:8001/api/docs
echo  Frontend UI:  http://localhost:3000
echo  Logs:         logs\backend_stdio.log, logs\frontend_dev.log
echo.
echo To stop services:
echo - Close the "ATLAS Backend" and "ATLAS Frontend" windows, or
echo - Run: taskkill /FI "WINDOWTITLE eq ATLAS Backend*" /T /F
echo - Run: taskkill /FI "WINDOWTITLE eq ATLAS Frontend*" /T /F
echo.
echo Press any key to view status...
pause >nul
tasklist | findstr /i "python node"
echo.
pause
