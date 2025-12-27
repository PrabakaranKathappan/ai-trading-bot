@echo off
echo ========================================
echo Creating Task Scheduler Task
echo ========================================
echo.
echo IMPORTANT: You will see a UAC prompt.
echo Please click YES to allow administrator access.
echo.
echo Press any key to continue...
pause > nul

REM Create a VBS script to run PowerShell as admin
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\elevate.vbs"
echo UAC.ShellExecute "powershell.exe", "-ExecutionPolicy Bypass -File ""%~dp0create_task_scheduler.ps1""", "", "runas", 1 >> "%temp%\elevate.vbs"

REM Run the VBS script
cscript //nologo "%temp%\elevate.vbs"

REM Clean up
del "%temp%\elevate.vbs"

echo.
echo.
echo Task creation process started!
echo.
echo A PowerShell window should have opened.
echo If you don't see it, check your taskbar.
echo.
echo After the PowerShell window closes, verify the task:
echo 1. Press Win + R
echo 2. Type: taskschd.msc
echo 3. Look for "Institutional Pullback Bot"
echo.
pause
