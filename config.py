import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for trading bot settings"""
    
    # Upstox API Configuration
    UPSTOX_API_KEY = os.getenv('UPSTOX_API_KEY', '')
    UPSTOX_API_SECRET = os.getenv('UPSTOX_API_SECRET', '')
    UPSTOX_REDIRECT_URI = os.getenv('UPSTOX_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Trading Configuration
    CAPITAL = float(os.getenv('CAPITAL', 70000))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 2))  # Percentage
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 3))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 5))  # Percentage
    
    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper')  # 'paper' or 'live'
    
    # Market Hours (IST)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 15
    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30
    SQUARE_OFF_HOUR = 15
    SQUARE_OFF_MINUTE = 15
    
    # Technical Indicator Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BB_PERIOD = 20
    BB_STD = 2
    
    EMA_SHORT = 9
    EMA_LONG = 21
    
    # Order Flow Parameters
    VOLUME_DELTA_THRESHOLD = 1000  # Minimum volume delta to consider
    BID_ASK_IMBALANCE_THRESHOLD = 0.6  # 60% imbalance
    CVD_LOOKBACK = 20  # Bars to look back for CVD
    
    # Signal Generation
    MIN_SIGNAL_STRENGTH = 60  # Minimum signal strength (0-100) to trade
    
    # Risk Management
    STOP_LOSS_PERCENT = 1.5  # Percentage from entry
    TARGET_PERCENT = 3.0  # Percentage from entry
    TRAILING_STOP_PERCENT = 1.0
    
    # Database
    DB_PATH = 'trading_bot.db'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = 'logs'
    
    # Dashboard
    DASHBOARD_HOST = '0.0.0.0'
    DASHBOARD_PORT = 5000
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        # UPSTOX credentials are now optional at startup (can be set dynamically)
        # if not cls.UPSTOX_API_KEY or not cls.UPSTOX_API_SECRET:
        #     raise ValueError("Upstox API credentials not configured. Please set UPSTOX_API_KEY and UPSTOX_API_SECRET in .env file")
        
        if cls.CAPITAL <= 0:
            raise ValueError("Capital must be greater than 0")
        
        if cls.RISK_PER_TRADE <= 0 or cls.RISK_PER_TRADE > 100:
            raise ValueError("Risk per trade must be between 0 and 100")
        
        return True
    
    @classmethod
    def set_credentials(cls, api_key, api_secret):
        """Set Upstox API credentials dynamically"""
        cls.UPSTOX_API_KEY = api_key
        cls.UPSTOX_API_SECRET = api_secret
    
    @classmethod
    def get_max_loss_per_trade(cls):
        """Calculate maximum loss per trade"""
        return cls.CAPITAL * (cls.RISK_PER_TRADE / 100)
    
    @classmethod
    def get_max_daily_loss(cls):
        """Calculate maximum daily loss"""
        return cls.CAPITAL * (cls.MAX_DAILY_LOSS / 100)
