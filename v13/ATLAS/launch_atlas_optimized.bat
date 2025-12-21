@echo off
setlocal enabledelayedexpansion

echo ============================================
echo ATLAS v18 - OPTIMIZED LAUNCH
echo ============================================
echo.

cd /d "D:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas"

echo [%time%] Checking dependencies...
if not exist node_modules\pino-pretty (
    echo [%time%] Installing missing dependencies...
    call npm install pino-pretty
)

echo [%time%] Checking environment configuration...
findstr /C:"v18-atlas-project-id" .env.local >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [%time%] WARNING: Using placeholder WalletConnect Project ID
    echo [%time%] Get real ID at: https://cloud.walletconnect.com/
)

echo [%time%] Killing existing processes...
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo [%time%] Starting Next.js with Turbopack...
start "ATLAS v18 Frontend" cmd /k "npm run dev:fast"

echo [%time%] Waiting for server to start...
timeout /t 5 /nobreak >nul

echo [%time%] Pre-warming application (first compile)...
curl -s http://localhost:3000 >nul 2>&1

echo.
echo ============================================
echo ATLAS v18 READY
echo ============================================
echo Frontend: http://localhost:3000
echo Network:  http://192.168.1.39:3000
echo.
echo First page load pre-compiled and cached
echo Subsequent loads will be instant
echo ============================================
echo.

pause
