import pandas as pd
import numpy as np
import math
from ta.trend import EMAIndicator

class InstitutionalPullbackStrategy:
    def __init__(self, config):
        self.config = config

    def calculate_indicators(self, df):
        """
        Calculates 20 EMA, VWAP, and Slope.
        Assumes df has columns: 'close', 'high', 'low', 'volume'
        """
        # 20 EMA
        ema20 = EMAIndicator(close=df['close'], window=self.config.EMA_PERIOD)
        df['ema_20'] = ema20.ema_indicator()
        
        # VWAP (Volume Weighted Average Price)
        # VWAP = Cumulative(Price * Volume) / Cumulative(Volume)
        # Typically calculated intraday, resetting at start of day. 
        # Here we do a rolling calculation or simple full-series for simplicity in mock
        # For a clearer intraday VWAP, we'd group by Date.
        # Simplified approximation:
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        df['tp_v'] = df['tp'] * df['volume']
        df['cumulative_tp_v'] = df['tp_v'].cumsum()
        df['cumulative_vol'] = df['volume'].cumsum()
        df['vwap'] = df['cumulative_tp_v'] / df['cumulative_vol']
        
        # Slope of EMA
        # Calculate slope based on last 2 points usually
        # Angle = arctan(change_in_price / change_in_time) 
        # But 'time' is 1 bar. So just change in price?
        # To normalize, we can check percentage change or simple difference.
        # "45 degrees" is visual and depends on chart scaling. 
        # A robust code equivalent is checking if the trend is strong positive.
        df['ema_slope'] = df['ema_20'].diff()
        
        return df

    def check_signal(self, df):
        """
        Checks for Buy/Sell signals on the last candle.
        Returns: 'BUY_CALL', 'BUY_PUT', or None
        """
        if len(df) < 20:
            return None
            
        current_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]
        
        price = current_candle['close']
        ema_20 = current_candle['ema_20']
        vwap = current_candle['vwap']
        slope = current_candle['ema_slope']
        
        # Define "Touch" buffer (e.g., within 0.1% or 0.2% of EMA)
        # or Low < EMA < High (price actually crossed/touched it)
        # "Bounce" means it touched and rejected.
        # For a "Limit" entry, we might look for price entering the zone.
        # Let's check if Low <= EMA <= High for the touch.
        touched_ema = current_candle['low'] <= ema_20 <= current_candle['high'] 
        
        # Or maybe the previous candle touched it and now we are green?
        # The user says: "The first time the price touches the 20 EMA after a breakout."
        # This implies waiting for the touch.
        
        # Slope check (Positive for Calls)
        # This is a rudimentary checks logic. "45 degrees" implies strong trend.
        # Let's assume a positive slope > 0 is a basic requirement, 
        # maybe > some small threshold to filter flat markets.
        is_slope_positive = slope > 0
        is_slope_negative = slope < 0
        
        # Signal Logic
        if touched_ema:
            if price > vwap and is_slope_positive:
                return "BUY_CALL"
            elif price < vwap and is_slope_negative:
                return "BUY_PUT"
                
        return None
