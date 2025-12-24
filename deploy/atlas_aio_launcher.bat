@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: QFS × ATLAS — AUTONOMOUS ALL-IN-ONE LAUNCHER (PRODUCTION EDITION)
:: ============================================================================
:: Version: 2.0.0
:: Features: Self-healing, retry logic, v15 isolation, structured logging
:: Author: QFS Development Team
:: Date: 2025-12-18
:: ============================================================================

:: ============================================================================
:: CONFIGURATION
:: ============================================================================

set "ROOTDIR=%~dp0"
set "LOGDIR=%ROOTDIR%logs"
set "ARTIFACTDIR=%ROOTDIR%artifacts"
set "V14_ARTIFACTS=%ARTIFACTDIR%\v14"
set "V15_ARTIFACTS=%ARTIFACTDIR%\v15"

:: Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%"

set "LOGFILE=%LOGDIR%\atlas_launch_%TIMESTAMP%.log"
set "JSON_LOG=%LOGDIR%\atlas_launch_%TIMESTAMP%.json"
set "PYTHONPATH=%ROOTDIR%"

:: Retry configuration
set MAX_RETRIES=3
set RETRY_DELAY=2

:: Feature flags
set V15_ENABLED=false
set ENABLE_JSON_LOGGING=true
set ENABLE_PARALLEL_TESTS=false
set AUTO_FIX_MODE=true

:: Color codes (Windows 10+ with ANSI support)
set "C_INFO=[94m"
set "C_SUCCESS=[92m"
set "C_WARNING=[93m"
set "C_ERROR=[91m"
set "C_CRITICAL=[95m"
set "C_RESET=[0m"

:: Error tracking
set CRITICAL_ERRORS=0
set WARNING_COUNT=0
set PHASE_FAILURES=0

:: ============================================================================
:: INITIALIZE LOGGING
:: ============================================================================

if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not exist "%ARTIFACTDIR%" mkdir "%ARTIFACTDIR%"
if not exist "%V14_ARTIFACTS%" mkdir "%V14_ARTIFACTS%"
if not exist "%V15_ARTIFACTS%" mkdir "%V15_ARTIFACTS%"

:: Initialize JSON log
if "%ENABLE_JSON_LOGGING%"=="true" (
    echo { > "%JSON_LOG%"
    echo   "launch_timestamp": "%TIMESTAMP%", >> "%JSON_LOG%"
    echo   "rootdir": "%ROOTDIR%", >> "%JSON_LOG%"
    echo   "v15_enabled": %V15_ENABLED%, >> "%JSON_LOG%"
    echo   "phases": [ >> "%JSON_LOG%"
)

goto :main_entry

:: ============================================================================
:: LOGGING FUNCTIONS
:: ============================================================================

:log
:: Usage: call :log <LEVEL> <MESSAGE>
set "LEVEL=%~1"
set "MESSAGE=%~2"
set "COLOR=!C_%LEVEL%!"

echo %COLOR%[%LEVEL%]%C_RESET% %MESSAGE%
echo [%date% %time%] [%LEVEL%] %MESSAGE% >> "%LOGFILE%"

if "%ENABLE_JSON_LOGGING%"=="true" (
    echo     { "timestamp": "%date% %time%", "level": "%LEVEL%", "message": "%MESSAGE%" }, >> "%JSON_LOG%"
)

if "%LEVEL%"=="CRITICAL" set /a CRITICAL_ERRORS+=1
if "%LEVEL%"=="WARNING" set /a WARNING_COUNT+=1
if "%LEVEL%"=="ERROR" set /a CRITICAL_ERRORS+=1

goto :eof

:log_phase
:: Usage: call :log_phase <PHASE_NAME> <STATUS>
set "PHASE=%~1"
set "STATUS=%~2"

call :log INFO "=========================================="
call :log INFO "PHASE: %PHASE%"
call :log INFO "STATUS: %STATUS%"
call :log INFO "=========================================="

if "%ENABLE_JSON_LOGGING%"=="true" (
    echo     { "phase": "%PHASE%", "status": "%STATUS%", "timestamp": "%date% %time%" }, >> "%JSON_LOG%"
)
goto :eof

:retry_command
:: Usage: call :retry_command <COMMAND> <MAX_RETRIES>
set "CMD=%~1"
set "MAX=%~2"
set "ATTEMPT=0"

:retry_loop
set /a ATTEMPT+=1
call :log INFO "Executing: %CMD% (Attempt %ATTEMPT%/%MAX%)"

%CMD% >> "%LOGFILE%" 2>&1
if %errorlevel% equ 0 (
    call :log SUCCESS "Command succeeded: %CMD%"
    goto :eof
)

if %ATTEMPT% lss %MAX% (
    call :log WARNING "Command failed, retrying in %RETRY_DELAY%s..."
    timeout /t %RETRY_DELAY% /nobreak >nul
    goto retry_loop
)

call :log ERROR "Command failed after %MAX% attempts: %CMD%"
exit /b 1

:auto_fix
:: Usage: call :auto_fix <ISSUE_TYPE> <FIX_ACTION>
set "ISSUE=%~1"
set "FIX=%~2"

if "%AUTO_FIX_MODE%"=="false" (
    call :log WARNING "Auto-fix disabled for: %ISSUE%"
    exit /b 1
)

call :log INFO "Auto-fixing: %ISSUE%"
call :log INFO "Action: %FIX%"

%FIX% >> "%LOGFILE%" 2>&1
if %errorlevel% equ 0 (
    call :log SUCCESS "Auto-fix successful: %ISSUE%"
    exit /b 0
) else (
    call :log ERROR "Auto-fix failed: %ISSUE%"
    exit /b 1
)

:main_entry

:: ============================================================================
:: PHASE 0: PRE-FLIGHT CHECKS
:: ============================================================================

call :log_phase "0_PREFLIGHT" "STARTING"

call :log INFO "QFS × ATLAS Autonomous Launcher v2.0.0"
call :log INFO "Root Directory: %ROOTDIR%"
call :log INFO "Log File: %LOGFILE%"
call :log INFO "v15 Mode: %V15_ENABLED%"
call :log INFO "Auto-Fix Mode: %AUTO_FIX_MODE%"

:: Check Windows version for ANSI color support
ver | findstr /i "10\." >nul
if %errorlevel% neq 0 (
    call :log WARNING "Windows 10+ recommended for color support"
)

call :log_phase "0_PREFLIGHT" "COMPLETE"

:: ============================================================================
:: PHASE 1: PYTHON ENVIRONMENT VALIDATION
:: ============================================================================

call :log_phase "1_PYTHON_ENV" "STARTING"

:: Check Python installation
call :log INFO "Validating Python installation..."
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log CRITICAL "Python not found in PATH"
    call :log ERROR "Please install Python 3.9+ and add to PATH"
    goto :critical_exit
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :log SUCCESS "Python detected: %PYTHON_VERSION%"

:: Validate Python version (must be 3.9+)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>nul
if %errorlevel% neq 0 (
    call :log CRITICAL "Python 3.9+ required"
    goto :critical_exit
)

:: Check pip
call :log INFO "Validating pip..."
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    call :auto_fix "pip_missing" "python -m ensurepip --upgrade"
    if !errorlevel! neq 0 goto :critical_exit
)

call :retry_command "python -m pip install --upgrade pip" %MAX_RETRIES%
if %errorlevel% neq 0 (
    call :log ERROR "pip upgrade failed"
    set /a PHASE_FAILURES+=1
)

:: Virtual environment
call :log INFO "Checking virtual environment..."
if exist "%ROOTDIR%venv\Scripts\activate.bat" (
    call :log SUCCESS "Virtual environment found"
    call "%ROOTDIR%venv\Scripts\activate.bat"
) else (
    call :log WARNING "Virtual environment not found, creating..."
    call :retry_command "python -m venv %ROOTDIR%venv" %MAX_RETRIES%
    if !errorlevel! neq 0 (
        call :log CRITICAL "Failed to create virtual environment"
        goto :critical_exit
    )
    call "%ROOTDIR%venv\Scripts\activate.bat"
)

call :log_phase "1_PYTHON_ENV" "COMPLETE"

:: ============================================================================
:: PHASE 2: DEPENDENCY MANAGEMENT
:: ============================================================================

call :log_phase "2_DEPENDENCIES" "STARTING"

:: Check requirements.txt
if not exist "%ROOTDIR%requirements.txt" (
    call :log WARNING "requirements.txt not found, generating..."
    call :auto_fix "requirements_missing" "powershell -Command \" 'pytest>=7.4.0', 'pytest-asyncio>=0.21.0', 'pytest-cov>=4.1.0', 'hypothesis>=6.80.0', 'mypy>=1.5.0', 'black>=23.7.0', 'flake8>=6.1.0' | Out-File -FilePath '%ROOTDIR%requirements.txt' -Encoding UTF8\""
)

:: Install dependencies with retry
call :log INFO "Installing dependencies..."
call :retry_command "python -m pip install -r %ROOTDIR%requirements.txt" %MAX_RETRIES%
if %errorlevel% neq 0 (
    call :log ERROR "Dependency installation failed"
    set /a PHASE_FAILURES+=1
) else (
    call :log SUCCESS "Dependencies installed"
)

:: Verify critical packages
call :log INFO "Verifying critical packages..."
for %%p in (pytest mypy) do (
    python -c "import %%p" 2>nul
    if !errorlevel! neq 0 (
        call :log ERROR "Critical package missing: %%p"
        call :retry_command "python -m pip install %%p" %MAX_RETRIES%
    )
)

call :log_phase "2_DEPENDENCIES" "COMPLETE"

:: ============================================================================
:: PHASE 3: DIRECTORY STRUCTURE VALIDATION
:: ============================================================================

call :log_phase "3_STRUCTURE" "STARTING"

:: Required directories
set "REQUIRED_DIRS=v13 v13\libs v13\atlas v13\policy v13\tests v13\tests\unit v13\tests\regression v13\policy\bounties v13\policy\treasury"

call :log INFO "Validating directory structure..."
for %%d in (%REQUIRED_DIRS%) do (
    if not exist "%ROOTDIR%%%d" (
        call :log WARNING "Directory missing: %%d"
        if "%AUTO_FIX_MODE%"=="true" (
            mkdir "%ROOTDIR%%%d"
            call :log SUCCESS "Created directory: %%d"
        )
    )
)

:: Ensure __init__.py files
call :log INFO "Validating Python packages..."
for %%p in (v13 v13\libs v13\atlas v13\policy v13\policy\bounties v13\policy\treasury v13\tests) do (
    if not exist "%ROOTDIR%%%p\__init__.py" (
        call :log WARNING "__init__.py missing in %%p"
        if "%AUTO_FIX_MODE%"=="true" (
            type nul > "%ROOTDIR%%%p\__init__.py"
            call :log SUCCESS "Created __init__.py in %%p"
        )
    )
)

call :log_phase "3_STRUCTURE" "COMPLETE"

:: ============================================================================
:: PHASE 4: CORE MODULE VALIDATION
:: ============================================================================

call :log_phase "4_CORE_MODULES" "STARTING"

:: Test BigNum128
call :log INFO "Validating BigNum128..."
python -c "from v13.libs.BigNum128 import BigNum128; bn = BigNum128.from_int(100); assert bn.value == 100000000000000000000; print('BigNum128 OK')" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    call :log CRITICAL "BigNum128 validation failed"
    goto :critical_exit
) else (
    call :log SUCCESS "BigNum128 validated"
)

:: Test CertifiedMath
call :log INFO "Validating CertifiedMath..."
python -c "from v13.libs.CertifiedMath import CertifiedMath; cm = CertifiedMath(); print('CertifiedMath OK')" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    call :log CRITICAL "CertifiedMath validation failed"
    goto :critical_exit
) else (
    call :log SUCCESS "CertifiedMath validated"
)

:: Test type_guards
call :log INFO "Validating type_guards..."
python -c "from v13.libs.type_guards import ensure_bignum, ensure_int; print('type_guards OK')" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    call :log WARNING "type_guards not found (non-critical)"
) else (
    call :log SUCCESS "type_guards validated"
)

call :log_phase "4_CORE_MODULES" "COMPLETE"

:: ============================================================================
:: PHASE 5: ATLAS MODULES VALIDATION
:: ============================================================================

call :log_phase "5_ATLAS_MODULES" "STARTING"

:: Check bootstrap
if not exist "%ROOTDIR%v13\atlas\bootstrap.py" (
    call :log WARNING "bootstrap.py missing, creating minimal version..."
    (
        echo """ATLAS Bootstrap Module - Auto-generated"""
        echo.
        echo def quick_check^(^):
        echo     try:
        echo         from v13.libs.CertifiedMath import CertifiedMath
        echo         from v13.libs.BigNum128 import BigNum128
        echo         return True
        echo     except Exception as e:
        echo         print^(f"Bootstrap check failed: {e}"^)
        echo         return False
    ) > "%ROOTDIR%v13\atlas\bootstrap.py"
    call :log SUCCESS "bootstrap.py created"
)

:: Test bootstrap
call :log INFO "Testing bootstrap..."
python -c "from v13.atlas.bootstrap import quick_check; assert quick_check(), 'Bootstrap failed'" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    call :log ERROR "Bootstrap validation failed"
    set /a PHASE_FAILURES+=1
) else (
    call :log SUCCESS "Bootstrap validated"
)

:: Test social layer modules
for %%m in (spaces wall chat) do (
    call :log INFO "Validating %%m module..."
    python -c "import v13.atlas.%%m; print('%%m OK')" >> "%LOGFILE%" 2>&1
    if !errorlevel! neq 0 (
        call :log ERROR "Module %%m import failed"
        set /a PHASE_FAILURES+=1
    ) else (
        call :log SUCCESS "Module %%m validated"
    )
)

call :log_phase "5_ATLAS_MODULES" "COMPLETE"

:: ============================================================================
:: PHASE 6: TEST SUITE EXECUTION (v15 Governance + Operational Tools)
:: ============================================================================

call :log_phase "6_TEST_SUITE" "STARTING"

:: Run v15 Full Audit Suite (includes all governance, stress, and ops tests)
call :log INFO "Running v15 Full Audit Suite..."
python v15\tests\autonomous\test_full_audit_suite.py
if %errorlevel% neq 0 (
    call :log CRITICAL "v15 Audit Suite FAILED - check AUDIT_RESULTS_SUMMARY.md"
    set /a CRITICAL_ERRORS+=1
    goto :critical_exit
)
call :log SUCCESS "v15 Audit Suite PASSED - All invariants verified"

call :log_phase "6_TEST_SUITE" "COMPLETE"

:: ============================================================================
:: PHASE 7: GOLDEN HASH GENERATION
:: ============================================================================

call :log_phase "7_GOLDEN_HASH" "STARTING"

if exist "%ROOTDIR%v13\tests\regression\generate_golden_hashes.py" (
    call :log INFO "Generating golden regression hashes..."
    python "%ROOTDIR%v13\tests\regression\generate_golden_hashes.py" >> "%LOGFILE%" 2>&1
    if !errorlevel! neq 0 (
        call :log WARNING "Golden hash generation failed"
        set /a PHASE_FAILURES+=1
    ) else (
        call :log SUCCESS "Golden hashes generated"
    )
) else (
    call :log WARNING "generate_golden_hashes.py not found"
)

call :log_phase "7_GOLDEN_HASH" "COMPLETE"

:: ============================================================================
:: PHASE 8: WALLET WALLET TESTING
:: ============================================================================

call :log_phase "8_WALLET_TEST" "STARTING"

:: Create wallet test if missing
if not exist "%ROOTDIR%test_wallet.py" (
    call :log INFO "Creating wallet test script..."
    (
        echo """Wallet Functionality Test"""
        echo import sys
        echo from pathlib import Path
        echo sys.path.insert^(0, str^(Path^(__file__^).parent^)^)
        echo from v13.libs.CertifiedMath import CertifiedMath
        echo from v13.libs.BigNum128 import BigNum128
        echo.
        echo def test_wallet^(^):
        echo     print^("Testing Wallet..."^)
        echo     try:
        echo         cm = CertifiedMath^(^)
        echo         bal = BigNum128.from_int^(1000^)
        echo         tx = BigNum128.from_int^(100^)
        echo         new_bal = cm.sub^(bal, tx, []^)
        echo         print^(f"Balance: {new_bal.value}"^)
        echo         return True
        echo     except Exception as e:
        echo         print^(f"Error: {e}"^)
        echo         return False
        echo.
        echo if __name__ == "__main__":
        echo     sys.exit^(0 if test_wallet^(^) else 1^)
    ) > "%ROOTDIR%test_wallet.py"
    call :log SUCCESS "Created test_wallet.py"
)

call :retry_command "python \"%ROOTDIR%test_wallet.py\"" %MAX_RETRIES%
if %errorlevel% neq 0 (
    call :log ERROR "Wallet test failed"
    set /a CRITICAL_ERRORS+=1
) else (
    call :log SUCCESS "Wallet test passed"
)

call :log_phase "8_WALLET_TEST" "COMPLETE"

:: ============================================================================
:: PHASE 9: TYPE SAFETY CHECK
:: ============================================================================

call :log_phase "9_TYPE_SAFETY" "STARTING"

call :log INFO "Running Type Safety verification for core economics modules..."
python -m mypy v13/libs/economics/EconomicsGuard.py v13/libs/BigNum128.py v13/libs/CertifiedMath.py --config-file mypy.ini >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    call :log ERROR "Type Safety verification failed for core modules"
    set /a PHASE_FAILURES+=1
) else (
    call :log SUCCESS "Type Safety verification: GREEN (0 errors in core libs)"
)

call :log_phase "9_TYPE_SAFETY" "COMPLETE"

:: ============================================================================
:: PHASE 10: ZERO-SIMULATION ANALYSIS
:: ============================================================================

call :log_phase "10_ZERO_SIM" "STARTING"

call :log INFO "Running AST Zero-Simulation analysis on economics modules..."
python v13/libs/AST_ZeroSimChecker.py v13/libs/economics/EconomicsGuard.py >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    call :log ERROR "Zero-Simulation analysis identified potential violations"
    set /a PHASE_FAILURES+=1
) else (
    call :log SUCCESS "Zero-Simulation analysis: GREEN (0 violations in core economics)"
)

call :log_phase "10_ZERO_SIM" "COMPLETE"

:: ============================================================================
:: COMPLETION REPORT
:: ============================================================================


call :log INFO "=========================================="
call :log INFO "LAUNCH COMPLETE"
call :log INFO "=========================================="
call :log INFO "Critical Errors: %CRITICAL_ERRORS%"
call :log INFO "Warnings: %WARNING_COUNT%"
call :log INFO "Phase Failures: %PHASE_FAILURES%"
call :log INFO "Log File: %LOGFILE%"

if %CRITICAL_ERRORS% equ 0 (
    if %PHASE_FAILURES% equ 0 (
        call :log SUCCESS "SYSTEM STATUS: GREEN - ALL SYSTEMS GO"
    ) else (
        call :log WARNING "SYSTEM STATUS: YELLOW - OPERATIONAL WITH WARNINGS"
    )
) else (
    call :log CRITICAL "SYSTEM STATUS: RED - CRITICAL FAILURE"
)

:: Close JSON log
if "%ENABLE_JSON_LOGGING%"=="true" (
    echo     { "timestamp": "%date% %time%", "status": "completed" } >> "%JSON_LOG%"
    echo   ] >> "%JSON_LOG%"
    echo } >> "%JSON_LOG%"
)

if %CRITICAL_ERRORS% neq 0 exit /b 1
exit /b 0

:critical_exit
call :log CRITICAL "ABORTING LAUNCH DUE TO CRITICAL ERROR"
call :log CRITICAL "Check log file: %LOGFILE%"
if "%ENABLE_JSON_LOGGING%"=="true" (
    echo     { "timestamp": "%date% %time%", "level": "CRITICAL", "message": "ABORT_LAUNCH" } >> "%JSON_LOG%"
    echo   ] >> "%JSON_LOG%"
    echo } >> "%JSON_LOG%"
)
endlocal
exit /b 1
