@echo off
echo ================================================
echo Pushing AI Trading Bot to GitHub
echo ================================================
echo.
echo Repository: https://github.com/PrabakaranKathappan/ai-trading-bot
echo.
echo When prompted:
echo   Username: PrabakaranKathappan
echo   Password: [Paste your Personal Access Token]
echo.
echo Note: The password won't show as you type - that's normal!
echo.
pause
echo.
echo Pushing code...
"C:\Program Files\Git\bin\git.exe" push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ================================================
    echo SUCCESS! Code pushed to GitHub
    echo ================================================
    echo.
    echo View your repository at:
    echo https://github.com/PrabakaranKathappan/ai-trading-bot
    echo.
) else (
    echo ================================================
    echo ERROR: Push failed
    echo ================================================
    echo.
    echo Please check:
    echo 1. You pasted the correct token
    echo 2. Token has 'repo' permissions
    echo 3. You're connected to the internet
    echo.
)
pause
