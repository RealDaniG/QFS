@echo off
:: ATLAS Backend Startup Script
:: Sets proper Python path and starts uvicorn

set "ROOTDIR=%~dp0"
set "PYTHONPATH=%ROOTDIR%"

echo ============================================================
echo ATLAS Backend Server Startup
echo ============================================================
echo.
echo Python Path: %PYTHONPATH%
echo Server Port: 8001
echo.

cd "%ROOTDIR%v13\atlas"

echo Starting uvicorn server...
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

pause
