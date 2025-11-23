@echo off
echo ==========================================
echo    AI Trading Bot - Local Testing Mode
echo ==========================================
echo.

echo 1. Checking dependencies...
pip install -r requirements.txt > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies. Please check python installation.
    pause
    exit /b 1
)
echo Dependencies OK.

echo.
echo 2. Starting Bot...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop.
echo.

python main.py

pause
