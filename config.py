import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Trading Settings
    SYMBOL = "BANKNIFTY" # Example
    TIMEFRAME = "5minute"
    CAPITAL = 80000
    RISK_PER_TRADE = 0.02 # 2% risk
    
    # Selection of Active Indices
    INDEX_MAPPINGS = {
        "BANKNIFTY": "NSE_INDEX|Nifty Bank",
        "NIFTY": "NSE_INDEX|Nifty 50",
        "SENSEX": "BSE_INDEX|SENSEX"
    }
    
    # Load selected indices from comma-separated string in .env
    # e.g SELECTED_INDICES=BANKNIFTY,NIFTY
    SELECTED_INDICES = os.getenv("SELECTED_INDICES", "BANKNIFTY").split(",")

    # Options Settings (Granular Control)
    MONEYNESS_NIFTY = os.getenv("MONEYNESS_NIFTY", "ATM")
    MONEYNESS_BANKNIFTY = os.getenv("MONEYNESS_BANKNIFTY", "ATM")
    MONEYNESS_SENSEX = os.getenv("MONEYNESS_SENSEX", "ATM")

    EXPIRY_NIFTY = os.getenv("EXPIRY_NIFTY", "WEEKLY")
    EXPIRY_BANKNIFTY = os.getenv("EXPIRY_BANKNIFTY", "MONTHLY") # Defaulting to Monthly per SEBI
    EXPIRY_SENSEX = os.getenv("EXPIRY_SENSEX", "WEEKLY")
    
    # Lot Sizes (Quantity of Lots)
    LOT_SIZE_NIFTY = int(os.getenv("LOT_SIZE_NIFTY", 1))
    LOT_SIZE_BANKNIFTY = int(os.getenv("LOT_SIZE_BANKNIFTY", 1))
    LOT_SIZE_SENSEX = int(os.getenv("LOT_SIZE_SENSEX", 1))

    # Standard Lot Multipliers (Quantity per Lot)
    LOT_MULTIPLIERS = {
        "NIFTY": 25,
        "BANKNIFTY": 15,
        "SENSEX": 10
    }
    
    # Strategy Settings
    EMA_PERIOD = 20
    SLOPE_THRESHOLD_DEGREES = 30 # Minimum angle for valid trend
    
    # Mode Toggles
    PAPER_TRADING_ENABLED = os.getenv("PAPER_TRADING_ENABLED", "True").lower() == "true"
    LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "False").lower() == "true"
    
    # Mode: 'MOCK' or 'LIVE' (Legacy - will be replaced by above toggles)
    MODE = os.getenv("TRADING_MODE", "MOCK") 
    
    # Upstox API Credentials
    UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY", "")
    UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET", "")
    UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI", "https://localhost:5000") 
    UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "") # If generated manually
    
    # Render / System
    CHECK_INTERVAL_SECONDS = 60
