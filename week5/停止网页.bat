@echo off
rem ===========================================================================
rem  Mersey Clerk - STOP the server - DHG508 Week 5
rem  Double-click this when you are done (or before starting again).
rem  Kept pure ASCII: cmd.exe reads .bat in the OEM code page.
rem ===========================================================================
title Mersey Clerk - stop server
chcp 65001 >nul
cd /d "%~dp0"

set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PY set "PY=%%i"
if not exist "%PY%" set "PY=C:\Users\28301\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%~dp0stop.py"
echo.
echo   Press any key to close.
pause >nul
exit /b
