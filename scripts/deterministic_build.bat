@echo off
REM QFS V13 Deterministic Build Script (Windows)

echo Building QFS V13 in deterministic environment...

REM Create build directory
if not exist build mkdir build

REM Copy source files
xcopy src build\src\ /E /I /Y
xcopy tests build\tests\ /E /I /Y
copy requirements.txt build\
copy requirements-dev.txt build\

REM Create deterministic build hash
echo Creating build manifest...
certutil -hashfile build\requirements.txt SHA256 > build\BUILD_HASH.txt

echo Deterministic build completed!
echo Build hash:
type build\BUILD_HASH.txt