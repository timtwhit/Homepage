@echo off
cd /d "%~dp0"

:: Bounce the server: kill whatever is currently listening on 8765
:: (an old save_server.py instance), then start a fresh one.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8765 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%p >nul 2>&1
)

:: Let the port free up, then start fresh.
:: save_server.py opens the browser tab itself on startup.
:: Full path to timeout.exe so a shadowed "timeout" on PATH can't break it.
"%SystemRoot%\System32\timeout.exe" /t 1 /nobreak >nul 2>&1
start "" pythonw save_server.py
