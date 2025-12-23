import time
import pandas as pd
import numpy as np
import logging
import schedule
from datetime import datetime, timedelta
from config import Config
from strategy import InstitutionalPullbackStrategy
from broker import MockBroker

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingApp")

# Initialize
config = Config()
broker = MockBroker(initial_capital=config.CAPITAL)
strategy = InstitutionalPullbackStrategy(config)

def generate_mock_data(length=100):
    """
    Generates synthetic OHLCV data to simulate market movements.
    """
    dates = [datetime.now() - timedelta(minutes=i*5) for i in range(length)]
    dates.reverse()
    
    # Random walk for price
    base_price = 45000
    prices = [base_price]
    for _ in range(length-1):
        change = np.random.normal(0, 20) # Random fluctuation
        prices.append(prices[-1] + change)
        
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p + abs(np.random.normal(0, 10)) for p in prices],
        'low': [p - abs(np.random.normal(0, 10)) for p in prices],
        'close': [p + np.random.normal(0, 5) for p in prices],
        'volume': [int(abs(np.random.normal(1000, 200))) for _ in range(length)]
    })
    return df

def trading_job():
    logger.info("Fetching market data...")
    
    # In a real app, fetch from broker:
    # df = broker.get_market_data(config.SYMBOL, config.TIMEFRAME)
    
    # For now, use Mock Data
    df = generate_mock_data(length=50)
    
    # Apply Strategy
    df = strategy.calculate_indicators(df)
    signal = strategy.check_signal(df)
    
    latest_price = df.iloc[-1]['close']
    ema_val = df.iloc[-1]['ema_20']
    
    logger.info(f"Price: {latest_price:.2f} | 20EMA: {ema_val:.2f} | Signal: {signal}")
    
    if signal:
        logger.info(f"SIGNAL DETECTED: {signal}")
        
        # Determine quantity based on risk (simplified)
        quantity = 1 # One lot/share
        
        if signal == "BUY_CALL":
            broker.place_order(config.SYMBOL, "MARKET", quantity, "BUY")
        elif signal == "BUY_PUT":
            broker.place_order(config.SYMBOL, "MARKET", quantity, "BUY_PUT_Mock") # Simplified logic
            
    positions = broker.get_positions()
    if positions:
        logger.info(f"Open Positions: {positions}")

def main():
    logger.info("Starting Institutional Pullback Trading App...")
    logger.info(f"Mode: {config.MODE}")
    logger.info("Press Ctrl+C to stop.")
    
    # Schedule the job
    schedule.every(config.CHECK_INTERVAL_SECONDS).seconds.do(trading_job)
    
    # Run once immediately
    trading_job()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
