# Institutional Pullback Trading App

## Deployment on Render

This application is designed to run on Render as a **Background Worker** or **Web Service**.

### Method 1: Background Worker (Preferred for Bots)
1. Link your GitHub repository to Render.
2. Select **New** > **Background Worker**.
3. Choose this repository.
4. Set the **Build Command** to: `pip install -r requirements.txt`
5. Set the **Start Command** to: `python main.py`
6. Deploys!

### Method 2: Web Service (Free Tier)
Note: The Free Tier on Render spins down Web Services after 15 minutes of inactivity. For a bot that needs to run 24/7, you might need a paid plan or use a keep-alive mechanism (e.g., uptime robot pinging a dummy flask route).

1. Select **New** > **Web Service**.
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `python main.py`
  - *Note*: If `main.py` is just a loop, Render might mark the deploy as failed if it doesn't bind to a port (PORT env var). You may need to wrap it in a simple Flask app if using Web Service type.

### Configuration
Set the following **Environment Variables** in Render:
- `TRADING_MODE`: `MOCK` (or `LIVE` when ready)
- `BROKER_API_KEY`: Your API Key
- `BROKER_CLIENT_ID`: Your Client ID
- `BROKER_PASSWORD`: Your Password
