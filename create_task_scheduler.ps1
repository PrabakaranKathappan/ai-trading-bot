# PowerShell Script to Create Task Scheduler Task for Trading Bot
# Run this script as Administrator

$TaskName = "Institutional Pullback Bot"
$TaskDescription = "Auto-start institutional pullback trading bot on system startup"
$ScriptPath = "C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback\start_trading_bot.bat"
$WorkingDirectory = "C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback"

Write-Host "Creating Task Scheduler task: $TaskName" -ForegroundColor Cyan

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the action (what to run)
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDirectory

# Create the trigger (when to run - at startup)
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Create the principal (run with highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal

Write-Host "`nTask created successfully!" -ForegroundColor Green
Write-Host "`nTask Details:" -ForegroundColor Cyan
Write-Host "  Name: $TaskName"
Write-Host "  Trigger: At system startup"
Write-Host "  Action: $ScriptPath"
Write-Host "`nTo verify, open Task Scheduler (taskschd.msc) and look for '$TaskName'" -ForegroundColor Yellow
Write-Host "`nTo test the task now, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
