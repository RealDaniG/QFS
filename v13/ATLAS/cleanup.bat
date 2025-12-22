@echo off
setlocal enabledelayedexpansion
title ATLAS v14-v2 Cleanup Utility
color 0C

echo ================================================
echo   ATLAS v14-v2 Cleanup Utility
echo ================================================
echo.

echo [1/4] Stopping Node.js processes...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo       Stopped Node.js processes
) else (
    echo       No Node.js processes running
)

echo [2/4] Stopping Python processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo       Stopped Python processes
) else (
    echo       No Python processes running
)

echo [3/4] Stopping Electron processes...
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM "ATLAS v18 Beta.exe" 2>nul
echo       Electron cleanup complete

echo [4/4] Clearing temporary caches...
if exist ".next" (
    rmdir /s /q ".next" 2>nul
    echo       Cleared .next cache
)
if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache" 2>nul
    echo       Cleared node_modules cache
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__" 2>nul
    echo       Cleared Python cache
)

echo.
echo ================================================
echo   Cleanup Complete
echo ================================================
echo.
echo Ports 8001 and 3000 should now be free.
echo Run launcher.bat to restart ATLAS.
echo.
pause
