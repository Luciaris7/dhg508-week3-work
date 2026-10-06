@echo off
rem ===========================================================================
rem  Mersey Clerk launcher - DHG508 Week 5
rem  DOUBLE-CLICK THIS FILE.
rem
rem  What it does:
rem   1. reads DEEPSEEK_API_KEY from your user environment (registry) into this
rem      process, so the server cannot silently fall back to the offline fixture
rem   2. its own pre-flight check: if a server is already running it just opens
rem      the browser; otherwise it opens the browser and runs the server HERE
rem   3. runs the server in THIS window: window open = server alive.
rem      To stop: press Ctrl+C here, or close this window.
rem
rem  Kept pure ASCII on purpose: cmd.exe reads .bat files in the OEM code page,
rem  so Chinese text here would show up as mojibake.
rem ===========================================================================
title Mersey Clerk server - DHG508 Week 5
chcp 65001 >nul
cd /d "%~dp0"

rem This machine has no py.exe under System32 (only C:\Windows\py.exe), so find
rem the interpreter by path and fall back to the known-good absolute path.
set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PY set "PY=%%i"
if not exist "%PY%" set "PY=C:\Users\28301\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo   [..] Reading the DeepSeek key from your user environment...
for /f "tokens=2,*" %%a in ('reg query "HKCU\Environment" /v DEEPSEEK_API_KEY 2^>nul ^| findstr /i DEEPSEEK_API_KEY') do set "DEEPSEEK_API_KEY=%%b"
if not defined DEEPSEEK_API_KEY (
  echo   [!] No key found - the page will use the OFFLINE fixture and will
  echo       only answer the 5 sample questions, with a yellow warning bar.
  echo       To fix, run once:  python code\set_key.py --verify
) else (
  echo   [OK] Key loaded.
)

echo   [..] Pre-flight check...
"%PY%" "%~dp0launch.py"

rem Skip starting a second server if one is already listening on 8000.
netstat -ano | findstr /i "LISTENING" | findstr ":8000 " >nul 2>&1
if not errorlevel 1 (
  echo.
  echo   [i] A server is already running on port 8000 - not starting another.
  echo       To stop it: run 停止网页.bat  or close the other Mersey window.
  echo.
  echo   Press any key to close this window.
  pause >nul
  exit /b 0
)

rem The page checks /api/health only once, so the browser must open only after
rem the server really answers. This detached waiter does that; the server then
rem runs in THIS window in the foreground.
echo   [..] Starting the browser waiter (opens the page once the server is up)...
start "" /b "%PY%" "%~dp0launch.py" --wait-open

echo.
echo   [..] Starting the server in this window.
echo        Keep this window open while you use the page.
echo        Stop with Ctrl+C, or just close this window.
echo.
"%PY%" -u "%~dp0app\server.py"

echo.
echo   Server stopped.
echo   Press any key to close.
pause >nul
exit /b 0
