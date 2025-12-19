@echo off
setlocal enabledelayedexpansion
set "C_INFO=[94m"
set "C_RESET=[0m"
set "LOGFILE=test.log"
call :log INFO "Test Message"
goto :eof

:log
set "LEVEL=%~1"
set "MESSAGE=%~2"
set "COLOR=!C_%LEVEL%!"
echo %COLOR%[%LEVEL%]%C_RESET% %MESSAGE%
echo [%date% %time%] [%LEVEL%] %MESSAGE% >> "%LOGFILE%"
goto :eof
