import os
import sys
from dashboard import app as application, set_trading_engine
from trading_engine import TradingEngine
from logger import Logger
from config import Config
import threading

# Initialize logger
logger = Logger.get_logger('wsgi')

# Initialize trading engine
logger.info("Initializing trading engine in WSGI...")
engine = TradingEngine()

# Try to initialize (will return False if auth needed, but won't block now)
if not engine.initialize():
    logger.warning("Trading engine initialization failed (likely needs auth). Server starting anyway.")
else:
    logger.info("Trading engine initialized successfully")
    # Start trading thread
    trading_thread = threading.Thread(
        target=engine.run,
        daemon=True
    )
    trading_thread.start()

# Set engine in dashboard
set_trading_engine(engine)

if __name__ == "__main__":
    application.run()
