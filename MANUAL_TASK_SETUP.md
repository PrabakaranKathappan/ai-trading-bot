# Manual Task Scheduler Setup (If Automated Script Fails)

If the automated scripts aren't working, follow these manual steps:

## Step 1: Open Task Scheduler
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

## Step 2: Create New Task
1. In the right panel, click **"Create Task"** (NOT "Create Basic Task")

## Step 3: General Tab
- **Name:** `Institutional Pullback Bot`
- **Description:** `Auto-start trading bot on system startup`
- ✅ Check **"Run whether user is logged on or not"**
- ✅ Check **"Run with highest privileges"**
- **Configure for:** Windows 10

## Step 4: Triggers Tab
1. Click **"New..."**
2. **Begin the task:** At startup
3. ✅ Check **"Enabled"**
4. Click **OK**

## Step 5: Actions Tab
1. Click **"New..."**
2. **Action:** Start a program
3. **Program/script:** Click **Browse** and select:
   ```
   C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback\start_trading_bot.bat
   ```
4. **Start in (optional):**
   ```
   C:\Users\Prabakaran K\.gemini\antigravity\scratch\institutional_pullback
   ```
5. Click **OK**

## Step 6: Conditions Tab
- ✅ **UNCHECK** "Start the task only if the computer is on AC power"
- ✅ Check "Wake the computer to run this task" (optional)

## Step 7: Settings Tab
- ✅ Check "Allow task to be run on demand"
- ✅ Check "Run task as soon as possible after a scheduled start is missed"
- **If the task fails, restart every:** 1 minute
- **Attempt to restart up to:** 3 times

## Step 8: Save
1. Click **OK**
2. Enter your Windows password when prompted
3. Click **OK**

## Step 9: Test the Task
1. In Task Scheduler, find "Institutional Pullback Bot"
2. Right-click → **Run**
3. Open browser: http://localhost:5000
4. Verify the dashboard loads

## Troubleshooting

### Task doesn't appear in Task Scheduler
- Make sure you clicked "Create Task" not "Create Basic Task"
- Check you have administrator privileges

### Task fails to run
- Verify the path to `start_trading_bot.bat` is correct
- Check that Python is installed and in PATH
- Try running `start_trading_bot.bat` manually first

### Bot doesn't start on system restart
- Check Task Scheduler → History tab for errors
- Verify "Run with highest privileges" is checked
- Ensure trigger is set to "At startup"
