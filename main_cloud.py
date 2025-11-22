import os
import threading
import sys
from flask import Flask
from trading_engine import TradingEngine
from dashboard import app, set_trading_engine
from logger import Logger
from config import Config

logger = Logger.get_logger('main_cloud')

def main():
    """Cloud-friendly main entry point"""
    print("=" * 60)
    print("AI TRADING BOT FOR NIFTY OPTIONS (CLOUD)")
    print("=" * 60)
    print(f"Mode: {Config.TRADING_MODE.upper()}")
    print(f"Capital: ₹{Config.CAPITAL:,.2f}")
    print(f"Environment: CLOUD (Render)")
    print("=" * 60)
    print()
    
    # Initialize trading engine
    logger.info("Initializing trading engine...")
    engine = TradingEngine()
    
    if not engine.initialize():
        logger.error("Failed to initialize trading engine")
        # Don't exit in cloud - keep Flask running for health checks
        logger.warning("Trading engine initialization failed, but keeping server alive")
    else:
        print("\n✓ Trading engine initialized successfully")
        
        # Start trading engine in a separate thread
        trading_thread = threading.Thread(
            target=engine.run,
            daemon=True
        )
        trading_thread.start()
        logger.info("Trading engine started in background thread")
    
    # Set trading engine reference in dashboard
    set_trading_engine(engine)
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n📊 Dashboard running on port {port}")
    print(f"🌐 Public URL: https://your-app.onrender.com")
    print("\nServer is ready for requests\n")
    
    # Run Flask app (this blocks)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
