@echo off
REM Institutional Pullback Trading Bot Launcher
REM This script starts the trading bot and keeps it running

cd /d "c:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback"

REM Activate virtual environment if you have one (optional)
REM call venv\Scripts\activate

REM Start the bot
python main_cloud.py

REM Keep window open if there's an error
pause
