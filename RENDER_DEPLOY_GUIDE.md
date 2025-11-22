# 🚀 Deploying AI Trading Bot to Render

Since Render's API doesn't support creating **Free Tier** services automatically, the best way is to use a **Blueprint**. I've already configured everything in `render.yaml`.

## Step 1: Create New Blueprint

1. Go to your Render Dashboard: https://dashboard.render.com
2. Click the **"New +"** button (top right).
3. Select **"Blueprint"**.
4. You should see your repository `ai-trading-bot` in the list.
   - If not, click "Connect a repository" and select it.
5. Click **"Connect"** next to `ai-trading-bot`.

## Step 2: Configure & Deploy

Render will read the `render.yaml` file I just pushed.

1. **Service Name**: It will default to `ai-trading-bot`. You can change it if you want.
2. **Environment Variables**:
   - You do **NOT** need to enter `UPSTOX_API_KEY` or `UPSTOX_API_SECRET` anymore.
   - These will be provided via the Mobile App later.
   - `TRADING_MODE` is set to `paper` by default.
3. Click **"Apply"** or **"Create Blueprint"**.

## Step 3: Done!

Render will now:
- Build your bot (`pip install -r requirements.txt`)
- Start it (`python main_cloud.py`)
- Deploy it on the **Free Tier**.

## Verification

Once deployed (it takes a few minutes):
1. Click on the service name in the dashboard.
2. You will see a URL like `https://ai-trading-bot-xxxx.onrender.com`.
3. Click it to see your bot's dashboard!

---

**Note:** The bot is set to **Paper Trading** mode. To switch to Live trading later, just update the `TRADING_MODE` environment variable to `live` in the Render dashboard.
