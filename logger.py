import logging
import os
from datetime import datetime
from config import Config

class Logger:
    """Centralized logging system for the trading bot"""
    
    _loggers = {}
    
    @staticmethod
    def setup():
        """Setup logging directory and configuration"""
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)
    
    @staticmethod
    def get_logger(name):
        """Get or create a logger with the specified name"""
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        Logger.setup()
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Remove existing handlers
        logger.handlers = []
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(detailed_formatter)
        logger.addHandler(console_handler)
        
        # File handler - general log
        today = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.FileHandler(
            os.path.join(Config.LOG_DIR, f'{name}_{today}.log')
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        Logger._loggers[name] = logger
        return logger
    
    @staticmethod
    def log_trade(trade_data):
        """Log trade execution to dedicated trade log"""
        trade_logger = Logger.get_logger('trades')
        trade_logger.info(f"TRADE: {trade_data}")
    
    @staticmethod
    def log_signal(signal_data):
        """Log trading signals to dedicated signal log"""
        signal_logger = Logger.get_logger('signals')
        signal_logger.info(f"SIGNAL: {signal_data}")
    
    @staticmethod
    def log_error(error_data):
        """Log errors to dedicated error log"""
        error_logger = Logger.get_logger('errors')
        error_logger.error(f"ERROR: {error_data}")
