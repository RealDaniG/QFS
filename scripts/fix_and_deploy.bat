@echo off
echo ========================================
echo AUTOMATED FIX AND DEPLOY
echo ========================================

echo.
echo [1/5] Creating missing __init__.py files...
type nul > v15\__init__.py
type nul > v15\auth\__init__.py
type nul > v15\api\__init__.py
type nul > v15\services\__init__.py
type nul > v15\tests\__init__.py
type nul > v15\tests\api\__init__.py
type nul > v15\tests\integration\__init__.py

echo.
echo [2/5] Checking requirements.txt...
if not exist v15\requirements.txt (
    echo Creating v15\requirements.txt...
    (
        echo fastapi==0.104.1
        echo uvicorn==0.24.0
        echo pydantic==2.5.0
        echo python-multipart==0.0.6
        echo httpx==0.25.1
        echo pytest==7.4.3
    ) > v15\requirements.txt
)

echo.
echo [3/5] Running pre-push validation...
python scripts\pre_push_validation.py
if errorlevel 1 (
    echo.
    echo ❌ Validation failed. Manual review required.
    pause
    exit /b 1
)

echo.
echo [4/5] Committing fixes...
git add .
git commit -m "fix(ci): Add missing __init__.py and requirements.txt for v15 modules"

echo.
echo [5/5] Pushing to main...
git push origin main

echo.
echo ========================================
echo ✅ FIXES DEPLOYED
echo ========================================
echo.
echo Monitoring pipeline...
timeout /t 10 /nobreak
gh run list --workflow=v20_auth_pipeline.yml --limit=1

pause
