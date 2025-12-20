@echo off
:: ATLAS Complete Stack Launcher
:: Starts both backend and frontend, then opens dashboards

set "ROOTDIR=%~dp0"
set "PYTHONPATH=%ROOTDIR%"

echo ============================================================
echo ATLAS v18.9 Complete Stack Launcher
echo ============================================================
echo.

:: Start Backend
echo [1/3] Starting Backend API Server (Port 8001)...
start "ATLAS Backend" cmd /c "cd /d %ROOTDIR%v13\atlas && set PYTHONPATH=%ROOTDIR% && python -m uvicorn src.main_minimal:app --host 0.0.0.0 --port 8001"

:: Wait for backend
timeout /t 5 /nobreak >nul

:: Start Frontend  
echo [2/3] Starting Frontend UI (Port 3000)...
start "ATLAS Frontend" cmd /c "cd /d %ROOTDIR%v13\atlas && npm run dev"

:: Wait for frontend
echo [3/3] Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ============================================================
echo Opening ATLAS Dashboards...
echo ============================================================
echo.

:: Open Backend API Docs
echo Opening Backend API Documentation...
start http://localhost:8001/api/docs

:: Wait a moment
timeout /t 2 /nobreak >nul

:: Open Frontend UI
echo Opening ATLAS Dashboard UI...
start http://localhost:3000

echo.
echo ============================================================
echo ATLAS Stack is Running!
echo ============================================================
echo.
echo  Backend API:  http://localhost:8001
echo  API Docs:     http://localhost:8001/api/docs
echo  Frontend UI:  http://localhost:3000
echo.
echo Press any key to view server status...
pause >nul

:: Show running processes
tasklist | findstr /i "python node"

echo.
echo To stop services, close the terminal windows.
pause
