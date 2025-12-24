@echo off
set "PYTHONPATH=%CD%"
echo Starting ATLAS from %CD%... > atlas_run.log
echo Timestamp: %DATE% %TIME% >> atlas_run.log
echo. >> atlas_run.log
echo Running python -m v13.ATLAS.src.main... >> atlas_run.log
python -m v13.ATLAS.src.main >> atlas_run.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ATLAS startup failed. Check atlas_run.log for details.
    type atlas_run.log
) else (
    echo ATLAS stopped.
)
