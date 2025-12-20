@echo off
echo Building and Starting V18 Staging Frontend...
cd %~dp0..\v13\atlas

echo Building Next.js App...
call npm run build

echo Starting Production Server...
set PORT=3000
npm start
