# Windows Task Scheduler Setup Guide

## Quick Setup Steps

### 1. Open Task Scheduler
- Press `Win + R`
- Type: `taskschd.msc`
- Press Enter

### 2. Create New Task
1. Click **"Create Task"** (not "Create Basic Task")
2. **General Tab:**
   - Name: `Institutional Pullback Bot`
   - Description: `Auto-start trading bot on system startup`
   - ✅ Check "Run whether user is logged on or not"
   - ✅ Check "Run with highest privileges"
   - Configure for: **Windows 10**

### 3. Triggers Tab
Click **"New..."**
- Begin the task: **At startup**
- ✅ Check "Enabled"
- Click **OK**

### 4. Actions Tab
Click **"New..."**
- Action: **Start a program**
- Program/script: `C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback\start_trading_bot.bat`
- Start in: `C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback`
- Click **OK**

### 5. Conditions Tab
- ✅ Uncheck "Start the task only if the computer is on AC power"
- ✅ Check "Wake the computer to run this task" (optional)

### 6. Settings Tab
- ✅ Check "Allow task to be run on demand"
- ✅ Check "Run task as soon as possible after a scheduled start is missed"
- If the task fails, restart every: **1 minute**
- Attempt to restart up to: **3 times**

### 7. Save the Task
- Click **OK**
- Enter your Windows password when prompted

## Testing the Setup

### Test 1: Manual Run
1. In Task Scheduler, find your task
2. Right-click → **Run**
3. Open browser: `http://localhost:5000`
4. Verify dashboard loads

### Test 2: Restart Test
1. Restart your computer
2. Wait 1-2 minutes
3. Open browser: `http://localhost:5000`
4. Verify bot is running

## Monitoring the Bot

### Check if Bot is Running
```powershell
# Open PowerShell and run:
Get-Process python
```

### View Task Scheduler Logs
1. Open Task Scheduler
2. Find your task
3. Click **History** tab (enable if disabled)

### Stop the Bot
```powershell
# Open PowerShell and run:
taskkill /F /IM python.exe
```

## Troubleshooting

### Bot doesn't start on boot
- Check Task Scheduler → History for errors
- Verify Python is in system PATH
- Try running `start_trading_bot.bat` manually first

### Can't access dashboard
- Check if Python process is running: `Get-Process python`
- Verify port 5000 is not blocked by firewall
- Check logs in the terminal/command window

### Bot crashes after some time
- Check the terminal window for error messages
- Verify `.env` file has correct settings
- Ensure internet connection is stable (for Upstox data)

## Alternative: Run Only During Market Hours

If you want the bot to run only during trading hours (9:15 AM - 3:30 PM IST):

### Modify Triggers:
1. **Start Trigger:**
   - Begin the task: **On a schedule**
   - Daily, recur every: **1 day**
   - Start time: **9:10 AM**
   - ✅ Enabled

2. **Stop Trigger:**
   - Settings Tab → Check "Stop the task if it runs longer than: **7 hours**"

This ensures the bot runs from 9:10 AM to ~4:10 PM daily.

## Security Notes

- The bot will have access to your Upstox credentials (if configured)
- Ensure your Windows account has a strong password
- Consider using a dedicated Windows user account for trading
- Never share your `.env` file or Upstox API keys

## Next Steps

After setup:
1. ✅ Test manual run
2. ✅ Test restart/auto-start
3. ✅ Monitor for 2 days in Paper Trading mode
4. ✅ Review logs and performance
5. ✅ Enable Live Trading only when confident
