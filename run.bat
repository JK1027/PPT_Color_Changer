@echo off
setlocal
cd /d "%~dp0"

echo Starting PPT Color Changer...

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" main.py
) else (
    python main.py
)

if errorlevel 1 (
    echo.
    echo [ERROR] An error occurred while running the application.
    pause
)
