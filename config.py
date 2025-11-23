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
    
    # Security
    BOT_ACCESS_PIN = os.getenv('BOT_ACCESS_PIN', '0000')  # Default PIN if not set
    
    # Trading Configuration
    CAPITAL = float(os.getenv('CAPITAL', 70000))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 2))  # Percentage
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 3))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 5))  # Percentage
    
    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper').lower()
    
    # Enabled Strategies
    ENABLED_STRATEGIES = {
        'RSI': True,
        'MACD': True,
        'BOLLINGER_BANDS': True,
        'EMA': True,
        'BREAKOUT': True,
        'ORDER_FLOW': True  # Controls all order flow signals
    }
    
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
        if cls.TRADING_MODE not in ['paper', 'live']:
            raise ValueError("TRADING_MODE must be 'paper' or 'live'")
            
        if cls.TRADING_MODE == 'live':
            if not cls.UPSTOX_API_KEY or not cls.UPSTOX_API_SECRET:
                raise ValueError("API Key and Secret are required for LIVE trading")
        
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

    # Profit Protection
    SECURE_PROFIT_ENABLED = False
    SECURE_PROFIT_AMOUNT = 0.0

    @classmethod
    def update_strategies(cls, strategies):
        """Update enabled strategies"""
        for key, value in strategies.items():
            if key in cls.ENABLED_STRATEGIES:
                cls.ENABLED_STRATEGIES[key] = bool(value)

    @classmethod
    def update_risk_settings(cls, settings):
        """Update risk settings"""
        if 'RISK_PER_TRADE' in settings:
            cls.RISK_PER_TRADE = float(settings['RISK_PER_TRADE'])
        if 'STOP_LOSS_PERCENT' in settings:
            cls.STOP_LOSS_PERCENT = float(settings['STOP_LOSS_PERCENT'])
        if 'TARGET_PERCENT' in settings:
            cls.TARGET_PERCENT = float(settings['TARGET_PERCENT'])
        if 'TRAILING_STOP_PERCENT' in settings:
            cls.TRAILING_STOP_PERCENT = float(settings['TRAILING_STOP_PERCENT'])
        if 'MAX_DAILY_LOSS' in settings:
            cls.MAX_DAILY_LOSS = float(settings['MAX_DAILY_LOSS'])
        if 'SECURE_PROFIT_ENABLED' in settings:
            cls.SECURE_PROFIT_ENABLED = bool(settings['SECURE_PROFIT_ENABLED'])
        if 'SECURE_PROFIT_AMOUNT' in settings:
            cls.SECURE_PROFIT_AMOUNT = float(settings['SECURE_PROFIT_AMOUNT'])
