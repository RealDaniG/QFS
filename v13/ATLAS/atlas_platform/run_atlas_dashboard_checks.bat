@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === ATLAS Dashboard Full Verification Script (Windows) ===
REM Run from ATLAS root (where src/ and tests/ live).

echo ====================================================
echo   ATLAS Dashboard – Full Autonomy Check
echo   Time: %DATE% %TIME%
echo ====================================================
echo.

REM Optional: activate venv if you use one
REM call .venv\Scripts\activate.bat

REM Configure Python path so 'src' is importable as a package
set PYTHONPATH=%CD%

set EXITCODE=0

REM ---------- 1. Lint / static sanity (optional) ----------
echo [1/4] Running lint/static checks (if configured)...
if exist .\scripts\lint_atlas.py (
    python -m scripts.lint_atlas
    if errorlevel 1 (
        echo.
        echo [ERROR] Lint/static checks failed (scripts.lint_atlas).
        set EXITCODE=1
    ) else (
        echo [OK] Lint/static checks passed.
    )
) else (
    echo [SKIP] No lint script found (scripts/lint_atlas.py).
)
echo.

REM ---------- 2. Core ATLAS unit tests ----------
echo [2/4] Running ATLAS unit tests...
python -m pytest src\tests -v
if errorlevel 1 (
    echo.
    echo [ERROR] ATLAS unit tests failed.
    echo   - Check failing test names and tracebacks above.
    set EXITCODE=1
) else (
    echo [OK] ATLAS unit tests passed.
)
echo.

REM ---------- 3. Secure-chat and API tests ----------
echo [3/4] Running secure-chat + API tests...
python -m pytest src\secure_chat\tests -v
if errorlevel 1 (
    echo.
    echo [ERROR] Secure-chat/API tests failed.
    echo   - Look for import errors, circular imports, or API failures.
    echo   - Confirm qfs_client/real_ledger imports and ATLAS src layout.
    set EXITCODE=1
) else (
    echo [OK] Secure-chat/API tests passed.
)
echo.

REM ---------- 4. Dashboard / value-node / value-graph tests ----------
echo [4/4] Running dashboard/value-node/value-graph tests...
python -m pytest tests\value_node -v
if errorlevel 1 (
    echo.
    echo [ERROR] Value-node/value-graph tests failed.
    echo   - Likely causes:
    echo       * Event schema mismatch (missing user_id/content_id on events)
    echo       * ValueGraphRef expectations vs fixtures (amount vs amount_atr)
    echo       * Import/path issues in tests\value_node\*
    set EXITCODE=1
) else (
    echo [OK] Value-node/value-graph tests passed.
)
echo.

REM ---------- Summary ----------
echo ====================================================
echo   SUMMARY
echo ====================================================
if %EXITCODE%==0 (
    echo [SUCCESS] All configured ATLAS dashboard checks passed.
) else (
    echo [FAIL] One or more checks failed.
    echo.
    echo Please scroll up in THIS window for detailed errors.
    echo Each section above prints a short explanation and hints.
)
echo ====================================================
echo.

REM Keep window open so you can read everything
echo Press any key to close this window...
pause >nul

endlocal
exit /b %EXITCODE%
