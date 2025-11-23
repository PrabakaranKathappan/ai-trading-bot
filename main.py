import threading
import sys
from trading_engine import TradingEngine
from dashboard import run_dashboard
from logger import Logger
from config import Config
from data_cleanup import DataCleanup
from keepalive import KeepAlive

logger = Logger.get_logger('main')

def main():
    """Main application entry point"""
    print("=" * 60)
    print("AI TRADING BOT FOR NIFTY OPTIONS")
    print("=" * 60)
    print(f"Mode: {Config.TRADING_MODE.upper()}")
    print(f"Capital: Rs.{Config.CAPITAL:,.2f}")
    print(f"Risk per trade: {Config.RISK_PER_TRADE}%")
    print("=" * 60)
    print()
    
    # Initialize trading engine
    logger.info("Initializing trading engine...")
    engine = TradingEngine()
    
    if not engine.initialize():
        logger.error("Failed to initialize trading engine")
        sys.exit(1)
    
    print("\n[OK] Trading engine initialized successfully")
    print(f"\n[DASHBOARD] Available at: http://localhost:{Config.DASHBOARD_PORT}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the bot\n")
    
    # Start dashboard in a separate thread
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        args=(engine,),
        daemon=True
    )
    dashboard_thread.start()
    
    logger.info("Dashboard started")
    
    # Start daily data cleanup in a separate thread (for Render free tier)
    cleanup = DataCleanup()
    cleanup_thread = threading.Thread(
        target=cleanup.schedule_daily_cleanup,
        args=("00:05",),  # Run cleanup at 12:05 AM daily
        daemon=True
    )
    cleanup_thread.start()
    logger.info("Daily data cleanup scheduled for 00:05 AM")
    
    # Start keep-alive for Render free tier (prevents spin-down)
    keepalive = KeepAlive()
    keepalive_thread = threading.Thread(
        target=keepalive.schedule_keepalive,
        daemon=True
    )
    keepalive_thread.start()
    logger.info("Keep-alive system started (pings every 10 minutes)")
    
    # Start trading engine
    try:
        engine.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        engine.stop()
        print("\n\n" + "=" * 60)
        print("Trading bot stopped")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
