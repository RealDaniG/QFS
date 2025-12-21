@echo off
echo Starting V18 Staging Backend (Production Mode)...
set ALLOWED_ORIGINS=http://localhost:3000
set QFS_FORCE_MOCK_PQC=0
set QFS_ENV=staging
set PYTHONPATH=%~dp0..
cd %~dp0..

echo Running Uvicorn with 2 workers...
python -m uvicorn v13.atlas.src.main_minimal:app --host 0.0.0.0 --port 8001 --workers 2 --log-level info
