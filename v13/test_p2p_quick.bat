@echo off
echo ================================================
echo   ATLAS v19 P2P Quick Test
echo ================================================
echo.

echo [1/2] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo [2/2] Running P2P test suite...
echo.

cd backend
python run_p2p_tests.py

echo.
echo ================================================
if errorlevel 0 (
    echo   ✅ ALL TESTS PASSED
) else (
    echo   ❌ SOME TESTS FAILED
)
echo ================================================
pause
