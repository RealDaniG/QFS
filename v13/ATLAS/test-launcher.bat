@echo off
echo ========================================
echo ATLAS Quick Test Launcher
echo ========================================
echo.
echo This script will:
echo 1. Run envelope parity tests
echo 2. Start backend
echo 3. Start desktop app
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [Step 1/4] Running Envelope Parity Tests...
echo ========================================
echo.

echo Testing Python envelope generation...
python scripts\verify_envelope_parity.py
if %errorlevel% neq 0 (
    echo ERROR: Python parity test failed!
    pause
    exit /b 1
)

echo.
echo Testing TypeScript envelope verification...
call npx tsx scripts\verify_envelope_parity.ts
if %errorlevel% neq 0 (
    echo ERROR: TypeScript parity test failed!
    pause
    exit /b 1
)

echo.
echo ✅ Parity tests passed!
echo.

echo [Step 2/4] Starting Backend...
echo ========================================
start "ATLAS Backend" cmd /k "python backend\main.py"
timeout /t 5 /nobreak >nul

echo.
echo [Step 3/4] Checking Backend Health...
curl -s http://127.0.0.1:8001/health
echo.

echo.
echo [Step 4/4] Starting Desktop App...
echo ========================================
cd desktop
start "ATLAS Desktop" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo ✅ ATLAS Test Environment Ready!
echo ========================================
echo.
echo Next steps:
echo 1. Test wallet connection and auth
echo 2. Test single-node chat
echo 3. Verify EvidenceBus commits
echo.
pause
