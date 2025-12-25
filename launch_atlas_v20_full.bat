@echo off
setlocal enabledelayedexpansion

title ATLAS v20 Full-Stack Launcher
color 0B

echo.
echo ================================================================
echo          QFS x ATLAS v20 - FULL-STACK AUTH LAUNCHER
echo ================================================================
echo.
echo This launcher starts:
echo   - Auth Service (port 8002)
echo   - Backend API (port 8001)
echo   - Frontend (port 3000) with Turbopack
echo.
echo ================================================================
echo.

cd /d "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"

REM ================================================================
REM ENVIRONMENT SETUP
REM ================================================================
set PYTHONPATH=%CD%;%CD%\v13;%CD%\v13\atlas
set QFS_FORCE_MOCKPQC=1
set ALLOWED_ORIGINS=http://localhost:3000
set AUTH_SERVICE_URL=http://localhost:8002
set EVIDENCEBUS_ENABLED=true
set SESSION_SECRET=dev_node_001_deterministic
set ENV=dev
set MOCKQPC_ENABLED=true
set CI=false

echo [%time%] Environment configured for v20 auth


REM ================================================================
REM STEP 1: CLEANUP
REM ================================================================
echo.
echo [STEP 1/6] Cleaning up existing processes...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM electron.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo [%time%] ✅ Cleanup complete


REM ================================================================
REM STEP 2: START AUTH SERVICE
REM ================================================================
echo.
echo [STEP 2/6] Starting Auth Service on port 8002...
start "QFS v20 Auth Service" cmd /k "python -m v15.services.auth_service --port 8002"
echo [%time%] Auth service starting...

REM Wait for auth service
set AUTH_READY=0
for /L %%i in (1,1,10) do (
    timeout /t 1 /nobreak >nul
    curl -s http://localhost:8002/health >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set AUTH_READY=1
        goto :auth_ready
    )
)
:auth_ready

if !AUTH_READY! EQU 1 (
    echo [%time%] ✅ Auth Service healthy
) else (
    echo [%time%] ❌ Auth Service failed - check logs
    echo.
    pause
    exit /b 1
)


REM ================================================================
REM STEP 3: START BACKEND API
REM ================================================================
echo.
echo [STEP 3/6] Starting Backend API on port 8001...
start "QFS Backend API" cmd /k "python -m uvicorn v13.atlas.src.main_minimal:app --host 0.0.0.0 --port 8001"
echo [%time%] Backend starting...

REM Wait for backend
set BACKEND_READY=0
for /L %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    curl -s http://localhost:8001/health >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set BACKEND_READY=1
        goto :backend_ready
    )
)
:backend_ready

if !BACKEND_READY! EQU 1 (
    echo [%time%] ✅ Backend API healthy
) else (
    echo [%time%] ❌ Backend failed - check logs
    echo.
    pause
    exit /b 1
)


REM ================================================================
REM STEP 4: START FRONTEND (TURBOPACK)
REM ================================================================
echo.
echo [STEP 4/6] Starting Frontend on port 3000 (Turbopack)...
cd v13
start "ATLAS v20 Frontend" cmd /k "npm run dev:fast"
cd ..
echo [%time%] Frontend starting...

REM Wait for frontend
set FRONTEND_READY=0
for /L %%i in (1,1,20) do (
    timeout /t 1 /nobreak >nul
    curl -s http://localhost:3000 >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set FRONTEND_READY=1
        goto :frontend_ready
    )
)
:frontend_ready

if !FRONTEND_READY! EQU 1 (
    echo [%time%] ✅ Frontend healthy
) else (
    echo [%time%] ⚠️  Frontend may still be compiling...
)


REM ================================================================
REM STEP 5: RUN AUTH VERIFICATION
REM ================================================================
echo.
echo [STEP 5/6] Running Auth Verification...
python scripts/verify_auth.py
if %ERRORLEVEL% NEQ 0 (
    echo [%time%] ❌ Auth verification failed!
    echo.
    pause
    exit /b 1
)

echo [%time%] ✅ Auth verification passed


REM ================================================================
REM STEP 6: READY
REM ================================================================
echo.
echo ============================================================
echo ATLAS v20 FULL-STACK READY
echo ============================================================
echo.
echo Auth Service:  http://localhost:8002
echo Backend API:   http://localhost:8001
echo Frontend:      http://localhost:3000
echo.
echo ✅ v20 Auth features enabled
echo    - Wallet login
echo    - Session management
echo    - Device binding
echo    - EvidenceBus logging
echo.
echo ============================================================
echo.
pause
