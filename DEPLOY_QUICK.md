# Quick Deployment Guide (Without Upstox Credentials)

## Step 1: Push to GitHub

Open Command Prompt in your project folder and run these commands:

```bash
cd c:\Users\Prabakaran K\Documents\antigravity_apps\AiTradingBot

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Trading Bot"
```

Now create a GitHub repository:

1. Go to https://github.com/new
2. Repository name: `ai-trading-bot`
3. Description: `Automated Nifty Options Trading Bot`
4. **Private** (recommended)
5. Click **"Create repository"**

Then push your code (replace YOUR_USERNAME with your GitHub username):

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### 2.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"**
4. If prompted, authorize GitHub
5. Select **"ai-trading-bot"** repository
6. Click **"Connect"**

### 2.2 Configure Service

Fill in these details:

- **Name**: `ai-trading-bot`
- **Region**: **Singapore** (closest to India)
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: **Python 3**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main_cloud.py`
- **Instance Type**: **Free**

### 2.3 Add Environment Variables (Optional for now)

Click **"Advanced"** → **"Add Environment Variable"**

Add these (you can add Upstox credentials later):

| Key | Value |
|-----|-------|
| `TRADING_MODE` | `paper` |
| `PYTHON_VERSION` | `3.11.0` |

### 2.4 Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `trading-bot-db`
3. **Database**: `trading_bot`
4. **User**: `trading_bot_user`
5. **Region**: **Singapore** (same as web service)
6. **Instance Type**: **Free**
7. Click **"Create Database"**

Wait for database to be created (~2 minutes)

### 2.5 Connect Database

1. Go to your PostgreSQL database
2. Copy the **"Internal Database URL"**
3. Go back to your **Web Service**
4. Click **"Environment"** tab
5. Click **"Add Environment Variable"**
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL
6. Click **"Save Changes"**

### 2.6 Deploy!

1. Click **"Create Web Service"** (or "Manual Deploy" if already created)
2. Watch the deployment logs
3. Wait 5-10 minutes for first deployment
4. You'll get a URL like: `https://ai-trading-bot.onrender.com`

## Step 3: Test Deployment

### Check Health Endpoint

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

### Access Dashboard

Open:
```
https://your-app.onrender.com
```

You should see the trading dashboard!

## Step 4: Set Up Keep-Alive

1. Go to https://cron-job.org/en/signup
2. Sign up (free)
3. Verify email
4. Click **"Cronjobs"** → **"Create cronjob"**

Configure:
- **Title**: `Trading Bot Keep-Alive`
- **URL**: `https://your-app.onrender.com/health` (use your actual URL)
- **Schedule**: 
  - **Every**: `10 minutes`
  - **Days**: Monday to Friday
  - **Time**: 9:00 AM - 4:00 PM
  - **Timezone**: Asia/Kolkata
- Click **"Create cronjob"**

## Step 5: Add Upstox Credentials Later

When you get your Upstox API credentials:

1. Go to Render dashboard
2. Select your web service
3. Click **"Environment"**
4. Add these variables:
   - `UPSTOX_API_KEY`: Your API key
   - `UPSTOX_API_SECRET`: Your API secret
   - `UPSTOX_REDIRECT_URI`: `https://your-app.onrender.com/callback`
5. Click **"Save Changes"**
6. Service will auto-redeploy

## Troubleshooting

### Build Failed
- Check logs in Render dashboard
- Look for error messages
- Verify all files are pushed to GitHub

### Can't Access Dashboard
- Wait 5-10 minutes for first deployment
- Check deployment status in Render
- Verify URL is correct

### Database Connection Error
- Ensure DATABASE_URL is set correctly
- Check PostgreSQL database is running
- Verify both services are in same region

## What Works Without Credentials

✅ Dashboard loads
✅ Health check works
✅ Database connection works
✅ Server stays alive with cron job

❌ Trading (needs Upstox credentials)
❌ Live data (needs Upstox credentials)

## Next Steps

1. ✅ Deploy to Render
2. ✅ Set up keep-alive
3. ⏳ Get Upstox credentials
4. ⏳ Create Android app

---

**Your bot will be running in the cloud!** 🚀

Once deployed, I'll create the Android app that connects to your cloud URL.
