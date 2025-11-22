@echo off
REM Git Setup and Push Script

echo ================================================
echo AI Trading Bot - GitHub Push Script
echo ================================================
echo.

REM Configure Git
echo [1/7] Configuring Git user...
git config --global user.name "Prabakaran K"
if %errorlevel% neq 0 (
    echo ERROR: Git configuration failed
    echo Please make sure Git is installed and in PATH
    pause
    exit /b 1
)

echo [2/7] Configuring Git email...
git config --global user.email "prabakaran@example.com"

echo [3/7] Verifying Git configuration...
git config --list | findstr user
echo.

REM Initialize repository
echo [4/7] Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ERROR: Git init failed
    pause
    exit /b 1
)

REM Add files
echo [5/7] Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)

REM Check status
echo [6/7] Checking Git status...
git status --short
echo.

REM Commit
echo [7/7] Creating initial commit...
git commit -m "Initial commit: AI Trading Bot for Nifty Options"
if %errorlevel% neq 0 (
    echo ERROR: Git commit failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! Repository initialized and committed
echo ================================================
echo.
echo Next steps:
echo 1. Create a GitHub repository at: https://github.com/new
echo 2. Run: git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git
echo 3. Run: git branch -M main
echo 4. Run: git push -u origin main
echo.
echo For authentication, you'll need a Personal Access Token from:
echo https://github.com/settings/tokens
echo.
pause
