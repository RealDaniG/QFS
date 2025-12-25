@echo off
setlocal

:: ==========================================
:: STORAGE AND LOGGING SETUP
:: ==========================================
set LOG_FILE=production_backend.log

:: ==========================================
:: PRODUCTION CONFIGURATION
:: ==========================================
:: B104 Mitigation: Bind to specific interface or localhost
if "%QFS_HOST%"=="" set QFS_HOST=127.0.0.1
if "%QFS_PORT%"=="" set QFS_PORT=8000
if "%QFS_ENV%"=="" set QFS_ENV=production

:: Production should strive for Native PQC, but we keep mock if native libs missing
:: unless explicitly overridden. Here we default to MOCK for safety in this env.
if "%QFS_FORCE_MOCK_PQC%"=="" set QFS_FORCE_MOCK_PQC=1

echo ========================================
echo STARTING PRODUCTION BACKEND (V15/V17/V18)
echo ========================================
echo Environment: %QFS_ENV%
echo Host: %QFS_HOST%
echo Port: %QFS_PORT%
echo PQC Mock: %QFS_FORCE_MOCK_PQC%

:: ==========================================
:: PATH CONFIGURATION
:: ==========================================
:: Ensure v13/atlas is in PYTHONPATH (critical fix from staging)
set PYTHONPATH=%~dp0..;%~dp0..\v13\atlas
cd %~dp0..

echo Running Uvicorn in PRODUCTION mode (Single Worker for Windows)...
python -m uvicorn v13.atlas.src.main_minimal:app --host %QFS_HOST% --port %QFS_PORT% --workers 1 --log-level info
