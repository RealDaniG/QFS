@echo off
echo Starting V18 Staging Backend (Production Mode)...
set ALLOWED_ORIGINS=http://localhost:3000

:: Set defaults if env vars not present (B104 mitigation)
if "%QFS_HOST%"=="" set QFS_HOST=127.0.0.1
if "%QFS_PORT%"=="" set QFS_PORT=8001
if "%QFS_FORCE_MOCK_PQC%"=="" set QFS_FORCE_MOCK_PQC=1
if "%QFS_ENV%"=="" set QFS_ENV=staging

echo Environment: %QFS_ENV%
echo Host: %QFS_HOST%
echo Port: %QFS_PORT%
echo PQC Mock: %QFS_FORCE_MOCK_PQC%

set PYTHONPATH=%~dp0..;%~dp0..\v13\atlas
cd %~dp0..

echo Running Uvicorn with 2 workers...
python -m uvicorn v13.atlas.src.main_minimal:app --host %QFS_HOST% --port %QFS_PORT% --workers 1 --log-level info
