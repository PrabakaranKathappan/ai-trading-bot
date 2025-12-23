import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Trading Settings
    SYMBOL = "BANKNIFTY" # Example
    TIMEFRAME = "5minute"
    CAPITAL = 80000
    RISK_PER_TRADE = 0.02 # 2% risk
    
    # Strategy Settings
    EMA_PERIOD = 20
    SLOPE_THRESHOLD_DEGREES = 30 # Minimum angle for valid trend
    
    # Broker Settings
    # Mode: 'MOCK' or 'LIVE'
    MODE = os.getenv("TRADING_MODE", "MOCK") 
    
    # API Keys (Load from env for security)
    API_KEY = os.getenv("BROKER_API_KEY", "")
    CLIENT_ID = os.getenv("BROKER_CLIENT_ID", "")
    PASSWORD = os.getenv("BROKER_PASSWORD", "")
    
    # Render / System
    CHECK_INTERVAL_SECONDS = 60
