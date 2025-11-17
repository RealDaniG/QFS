@echo off
REM QFS V13 Local CI/CD Check Script (Windows)

echo Running Local CI/CD Checks...

REM Run Zero-Simulation compliance check
echo 1. Running Zero-Simulation Compliance Check...
python src/libs/AST_ZeroSimChecker.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Zero-Simulation Compliance Check FAILED
    exit /b 1
)
echo ✅ Zero-Simulation Compliance Check PASSED

REM Run deterministic hash check
echo 2. Running Deterministic Hash Check...
python tools/deterministic_hash_check.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deterministic Hash Check FAILED
    exit /b 1
)
echo ✅ Deterministic Hash Check PASSED

REM Run PQC integrity check
echo 3. Running PQC Integrity Check...
python tools/validate_pqc_integrity.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PQC Integrity Check FAILED
    exit /b 1
)
echo ✅ PQC Integrity Check PASSED

REM Run unit tests
echo 4. Running Unit Tests...
python -m pytest tests/unit/ -x
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Unit Tests FAILED
    exit /b 1
)
echo ✅ Unit Tests PASSED

REM Run fast integration tests
echo 5. Running Fast Integration Tests...
python -m pytest tests/integration/ -x -k "not slow"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Fast Integration Tests FAILED
    exit /b 1
)
echo ✅ Fast Integration Tests PASSED

echo 🎉 All Local CI/CD Checks PASSED!