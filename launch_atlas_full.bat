@echo off
set "ROOTDIR=%~dp0"
cd /d "%ROOTDIR%"

REM Single entry point: run the orchestrator only. NoExit keeps the window open on error.
powershell -NoExit -ExecutionPolicy Bypass -File run_atlas_full.ps1 %*
