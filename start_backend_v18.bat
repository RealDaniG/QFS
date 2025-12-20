@echo off
echo Starting ATLAS v18 Backend...
set PYTHONPATH=d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13
set QFS_FORCE_MOCK_PQC=1
set EXPLAIN_THIS_SOURCE=qfs_ledger

cd v13\atlas
python -m uvicorn src.main_minimal:app --reload --port 8001
pause
