import pandas as pd
import numpy as np
from config import Config
from logger import Logger

logger = Logger.get_logger('indicators')

class TechnicalIndicators:
    """Calculate technical indicators for trading signals"""
    
    @staticmethod
    def calculate_rsi(data, period=None):
        """
        Calculate RSI (Relative Strength Index)
        Returns: RSI value (0-100)
        """
        if period is None:
            period = Config.RSI_PERIOD
        
        if len(data) < period + 1:
            return None
        
        df = pd.DataFrame(data)
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    @staticmethod
    def calculate_macd(data, fast=None, slow=None, signal=None):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns: dict with macd, signal, histogram
        """
        if fast is None:
            fast = Config.MACD_FAST
        if slow is None:
            slow = Config.MACD_SLOW
        if signal is None:
            signal = Config.MACD_SIGNAL
        
        if len(data) < slow + signal:
            return None
        
        df = pd.DataFrame(data)
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    @staticmethod
    def calculate_bollinger_bands(data, period=None, std=None):
        """
        Calculate Bollinger Bands
        Returns: dict with upper, middle, lower bands and position
        """
        if period is None:
            period = Config.BB_PERIOD
        if std is None:
            std = Config.BB_STD
        
        if len(data) < period:
            return None
        
        df = pd.DataFrame(data)
        
        # Calculate middle band (SMA)
        middle = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std_dev = df['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        current_price = df['close'].iloc[-1]
        upper_val = upper.iloc[-1]
        middle_val = middle.iloc[-1]
        lower_val = lower.iloc[-1]
        
        # Determine position relative to bands
        if current_price >= upper_val:
            position = 'ABOVE_UPPER'
        elif current_price <= lower_val:
            position = 'BELOW_LOWER'
        elif current_price > middle_val:
            position = 'ABOVE_MIDDLE'
        else:
            position = 'BELOW_MIDDLE'
        
        return {
            'upper': upper_val,
            'middle': middle_val,
            'lower': lower_val,
            'position': position,
            'bandwidth': (upper_val - lower_val) / middle_val * 100 if middle_val > 0 else 0
        }
    
    @staticmethod
    def calculate_ema(data, period=None):
        """
        Calculate EMA (Exponential Moving Average)
        Returns: EMA value
        """
        if period is None:
            period = Config.EMA_SHORT
        
        if len(data) < period:
            return None
        
        df = pd.DataFrame(data)
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return ema.iloc[-1]
    
    @staticmethod
    def calculate_support_resistance(data, lookback=20):
        """
        Calculate support and resistance levels
        Returns: dict with support and resistance levels
        """
        if len(data) < lookback:
            return None
        
        df = pd.DataFrame(data)
        recent_data = df.tail(lookback)
        
        # Find local maxima and minima
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        resistance = np.max(highs)
        support = np.min(lows)
        
        # Find pivot points
        pivot = (recent_data['high'].iloc[-1] + recent_data['low'].iloc[-1] + recent_data['close'].iloc[-1]) / 3
        
        return {
            'resistance': resistance,
            'support': support,
            'pivot': pivot,
            'r1': 2 * pivot - support,
            's1': 2 * pivot - resistance
        }
    
    @staticmethod
    def detect_breakout(data, current_price, lookback=20):
        """
        Detect if current price is breaking out of recent range
        Returns: 'BULLISH_BREAKOUT', 'BEARISH_BREAKOUT', or None
        """
        if len(data) < lookback:
            return None
        
        df = pd.DataFrame(data)
        recent_data = df.tail(lookback)
        
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        
        # Check for breakout with 0.5% buffer
        if current_price > resistance * 1.005:
            return 'BULLISH_BREAKOUT'
        elif current_price < support * 0.995:
            return 'BEARISH_BREAKOUT'
        
        return None
    
    @staticmethod
    def calculate_volume_trend(data, period=10):
        """
        Calculate volume trend
        Returns: 'INCREASING', 'DECREASING', or 'NEUTRAL'
        """
        if len(data) < period:
            return 'NEUTRAL'
        
        df = pd.DataFrame(data)
        recent_volume = df['volume'].tail(period)
        
        avg_volume = recent_volume.mean()
        current_volume = df['volume'].iloc[-1]
        
        if current_volume > avg_volume * 1.5:
            return 'INCREASING'
        elif current_volume < avg_volume * 0.5:
            return 'DECREASING'
        
        return 'NEUTRAL'
    
    @staticmethod
    def analyze_indicators(data):
        """
        Analyze all indicators and return comprehensive analysis
        Returns: dict with all indicator values and signals
        """
        if len(data) < Config.BB_PERIOD:
            logger.warning("Insufficient data for indicator analysis")
            return None
        
        current_price = data[-1]['close']
        
        # Calculate all indicators
        rsi = TechnicalIndicators.calculate_rsi(data)
        macd = TechnicalIndicators.calculate_macd(data)
        bb = TechnicalIndicators.calculate_bollinger_bands(data)
        ema_short = TechnicalIndicators.calculate_ema(data, Config.EMA_SHORT)
        ema_long = TechnicalIndicators.calculate_ema(data, Config.EMA_LONG)
        sr = TechnicalIndicators.calculate_support_resistance(data)
        breakout = TechnicalIndicators.detect_breakout(data, current_price)
        volume_trend = TechnicalIndicators.calculate_volume_trend(data)
        
        # Generate signals
        signals = {
            'rsi_signal': None,
            'macd_signal': None,
            'bb_signal': None,
            'ema_signal': None,
            'breakout_signal': breakout,
            'volume_signal': volume_trend
        }
        
        # RSI signals
        if rsi:
            if rsi < Config.RSI_OVERSOLD:
                signals['rsi_signal'] = 'BUY'
            elif rsi > Config.RSI_OVERBOUGHT:
                signals['rsi_signal'] = 'SELL'
        
        # MACD signals
        if macd:
            if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
                signals['macd_signal'] = 'BUY'
            elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
                signals['macd_signal'] = 'SELL'
        
        # Bollinger Bands signals
        if bb:
            if bb['position'] == 'BELOW_LOWER':
                signals['bb_signal'] = 'BUY'
            elif bb['position'] == 'ABOVE_UPPER':
                signals['bb_signal'] = 'SELL'
        
        # EMA signals
        if ema_short and ema_long:
            if ema_short > ema_long:
                signals['ema_signal'] = 'BUY'
            else:
                signals['ema_signal'] = 'SELL'
        
        return {
            'current_price': current_price,
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bb,
            'ema_short': ema_short,
            'ema_long': ema_long,
            'support_resistance': sr,
            'signals': signals
        }
