# Deployment Guide - Render + GitHub

## Prerequisites

✅ Render account created
✅ GitHub account created
✅ Upstox API credentials ready

## Step 1: Push Code to GitHub

### 1.1 Initialize Git (if not done)

Open Command Prompt in your project folder:

```bash
cd c:\Users\Prabakaran K\Documents\antigravity_apps\AiTradingBot
git init
git add .
git commit -m "Initial commit - AI Trading Bot"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Name: `ai-trading-bot`
4. Description: "Automated Nifty Options Trading Bot"
5. Keep it **Private** (recommended)
6. Click "Create repository"

### 1.3 Push to GitHub

Copy the commands from GitHub and run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 2: Deploy to Render

### 2.1 Create New Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Click "Connect a repository"
4. Authorize GitHub if needed
5. Select your `ai-trading-bot` repository

### 2.2 Configure Web Service

Fill in the details:

- **Name**: `ai-trading-bot` (or any name you like)
- **Region**: Singapore (closest to India)
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main_cloud.py`
- **Instance Type**: `Free`

### 2.3 Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these variables:

| Key | Value |
|-----|-------|
| `UPSTOX_API_KEY` | Your Upstox API Key |
| `UPSTOX_API_SECRET` | Your Upstox API Secret |
| `UPSTOX_REDIRECT_URI` | `https://ai-trading-bot.onrender.com/callback` |
| `TRADING_MODE` | `paper` |
| `PYTHON_VERSION` | `3.11.0` |

> **IMPORTANT**: Replace the redirect URI with your actual Render URL after deployment

### 2.4 Create PostgreSQL Database

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `trading-bot-db`
3. Database: `trading_bot`
4. User: `trading_bot_user`
5. Region: Same as web service (Singapore)
6. Instance Type: `Free`
7. Click "Create Database"

### 2.5 Connect Database to Web Service

1. Go back to your web service
2. Click "Environment"
3. Add new environment variable:
   - Key: `DATABASE_URL`
   - Value: Copy from PostgreSQL "Internal Database URL"

### 2.6 Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. You'll see logs in real-time
4. Once done, you'll get a URL like: `https://ai-trading-bot.onrender.com`

## Step 3: Update Upstox Redirect URI

1. Go to https://account.upstox.com/developer/apps
2. Edit your app
3. Update Redirect URL to: `https://your-app.onrender.com/callback`
4. Save changes

## Step 4: Set Up Keep-Alive (Prevent Sleep)

Render free tier sleeps after 15 min inactivity. Use a cron service to keep it awake.

### 4.1 Create Cron Job

1. Go to https://cron-job.org/en/
2. Sign up (free)
3. Click "Create cronjob"

### 4.2 Configure Cron Job

- **Title**: Trading Bot Keep-Alive
- **URL**: `https://your-app.onrender.com/health`
- **Schedule**: Every 10 minutes
- **Time zone**: Asia/Kolkata (IST)
- **Active hours**: 9:00 AM - 4:00 PM (Monday-Friday)
- Click "Create cronjob"

## Step 5: Test Deployment

### 5.1 Check Health

Open in browser:
```
https://your-app.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "mode": "paper",
  "environment": "cloud"
}
```

### 5.2 Access Dashboard

Open:
```
https://your-app.onrender.com
```

You should see the trading dashboard!

## Step 6: First-Time Authentication

1. Open dashboard in browser
2. Bot will redirect to Upstox login
3. Log in with Upstox credentials
4. Copy the `code` from redirect URL
5. The bot will authenticate automatically

## Troubleshooting

### Build Failed

**Check logs** in Render dashboard:
- Look for missing dependencies
- Check Python version
- Verify requirements.txt

**Common fixes**:
```bash
# If psycopg2 fails, it will use psycopg2-binary (already in requirements)
```

### Database Connection Failed

1. Check DATABASE_URL is set correctly
2. Verify PostgreSQL database is running
3. Check database region matches web service

### Bot Not Staying Awake

1. Verify cron job is running
2. Check cron job URL is correct
3. Ensure active hours are set (9 AM - 4 PM IST)

### Authentication Failed

1. Update Upstox redirect URI
2. Check API credentials in environment variables
3. Verify redirect URI matches exactly

## Monitoring

### Render Dashboard

- View logs: https://dashboard.render.com
- Check deployment status
- Monitor resource usage

### Cron Job

- Check execution history at cron-job.org
- Verify pings are successful

### Trading Bot

- Access dashboard: `https://your-app.onrender.com`
- Check P&L, positions, trades
- Use control buttons (pause/resume)

## Updating Code

When you make changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

Render will automatically redeploy!

## Cost Summary

- **Render Web Service**: FREE (750 hours/month)
- **PostgreSQL Database**: FREE (1GB storage)
- **GitHub**: FREE (private repo)
- **Cron Job**: FREE (unlimited jobs)

**Total**: ₹0 per month 🎉

## Next Steps

1. ✅ Deploy to Render
2. ✅ Set up keep-alive
3. ⏳ Create Android app
4. ⏳ Test end-to-end

---

**Your bot is now running 24/7 in the cloud!** 🚀
