import pandas as pd
import numpy as np
import math
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange

class InstitutionalPullbackStrategy:
    def __init__(self, config):
        self.config = config

    def calculate_indicators(self, df):
        """
        Calculates 20 EMA, VWAP, Slope, and ATR.
        Assumes df has columns: 'close', 'high', 'low', 'volume'
        """
        # 20 EMA
        ema20 = EMAIndicator(close=df['close'], window=self.config.EMA_PERIOD)
        df['ema_20'] = ema20.ema_indicator()
        
        # VWAP (Volume Weighted Average Price)
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        df['tp_v'] = df['tp'] * df['volume']
        df['cumulative_tp_v'] = df['tp_v'].cumsum()
        df['cumulative_vol'] = df['volume'].cumsum()
        df['vwap'] = df['cumulative_tp_v'] / df['cumulative_vol']
        
        # ATR (14 period) for volatility mapping
        atr_indicator = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
        df['atr'] = atr_indicator.average_true_range()
        
        # Slope of EMA (difference between last two points)
        df['ema_slope'] = df['ema_20'].diff()
        
        return df

    def check_signal(self, df):
        """
        Checks for Buy/Sell signals on the last candle.
        Returns: Dict with signal details or None
        """
        if len(df) < 20:
            return None
            
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = current['close']
        ema_val = current['ema_20']
        vwap_val = current['vwap']
        slope = current['ema_slope']
        atr = current['atr'] if not pd.isna(current['atr']) else 10.0
        
        # 1. Trend Filter
        # Threshold: We look for a slope that isn't flat. 
        # Using 0.01% of price as a minimum move per bar.
        threshold = price * 0.0001 
        is_uptrend = price > vwap_val and slope > threshold
        is_downtrend = price < vwap_val and slope < -threshold
        
        # 2. Bounce/Rejection Logic
        # Does the candle's range include the EMA?
        touched_ema = current['low'] <= ema_val <= current['high']
        
        if touched_ema:
            # Rejection: We dipped to EMA and closed in the trend direction
            # For Calls: Green candle touching EMA
            if is_uptrend and current['close'] > current['open']:
                entry = current['close']
                # SL: Below candle low or EMA (whichever lower) - small buffer
                sl = min(current['low'], ema_val) - (atr * 0.1)
                risk = entry - sl
                if risk <= 0: risk = atr # Fallback
                tp = entry + (risk * 2) # 1:2 Risk Reward
                
                return {
                    'side': 'BUY_CALL',
                    'entry_price': entry,
                    'stop_loss': sl,
                    'take_profit': tp
                }
                
            # For Puts: Red candle touching EMA
            elif is_downtrend and current['close'] < current['open']:
                entry = current['close']
                # SL: Above candle high or EMA (whichever higher) + small buffer
                sl = max(current['high'], ema_val) + (atr * 0.1)
                risk = sl - entry
                if risk <= 0: risk = atr # Fallback
                tp = entry - (risk * 2) # 1:2 Risk Reward
                
                return {
                    'side': 'BUY_PUT',
                    'entry_price': entry,
                    'stop_loss': sl,
                    'take_profit': tp
                }
                
        return None
