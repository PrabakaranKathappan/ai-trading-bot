import pandas as pd
import numpy as np
from collections import deque
from config import Config
from logger import Logger

logger = Logger.get_logger('order_flow')

class OrderFlowAnalyzer:
    """Analyze order flow for trading signals"""
    
    def __init__(self):
        self.cvd_history = deque(maxlen=Config.CVD_LOOKBACK)
        self.last_price = None
        self.last_volume = 0
    
    def calculate_volume_delta(self, candle_data):
        """
        Calculate volume delta (buying volume - selling volume)
        Uses price movement to estimate buying vs selling pressure
        """
        if not candle_data:
            return 0
        
        close = candle_data.get('close')
        open_price = candle_data.get('open')
        high = candle_data.get('high')
        low = candle_data.get('low')
        volume = candle_data.get('volume', 0)
        
        if not all([close, open_price, high, low]):
            return 0
        
        # Calculate volume delta based on price action
        # If close > open, more buying pressure
        # If close < open, more selling pressure
        
        price_range = high - low
        if price_range == 0:
            return 0
        
        # Estimate buying and selling volume
        if close > open_price:
            # Bullish candle - more buying
            buying_ratio = (close - low) / price_range
            buying_volume = volume * buying_ratio
            selling_volume = volume * (1 - buying_ratio)
        else:
            # Bearish candle - more selling
            selling_ratio = (high - close) / price_range
            selling_volume = volume * selling_ratio
            buying_volume = volume * (1 - selling_ratio)
        
        delta = buying_volume - selling_volume
        return delta
    
    def calculate_cumulative_volume_delta(self, candle_data):
        """
        Calculate Cumulative Volume Delta (CVD)
        Tracks cumulative buying vs selling pressure over time
        """
        delta = self.calculate_volume_delta(candle_data)
        self.cvd_history.append(delta)
        
        cvd = sum(self.cvd_history)
        return cvd
    
    def analyze_bid_ask_imbalance(self, market_data):
        """
        Analyze bid-ask imbalance from order book
        Returns: imbalance ratio and signal
        """
        bid_qty = market_data.get('bid_qty', 0)
        ask_qty = market_data.get('ask_qty', 0)
        
        if bid_qty == 0 and ask_qty == 0:
            return {
                'imbalance': 0,
                'signal': None,
                'strength': 0
            }
        
        total_qty = bid_qty + ask_qty
        if total_qty == 0:
            return {
                'imbalance': 0,
                'signal': None,
                'strength': 0
            }
        
        # Calculate imbalance ratio
        bid_ratio = bid_qty / total_qty
        ask_ratio = ask_qty / total_qty
        
        imbalance = bid_ratio - ask_ratio
        
        # Determine signal
        signal = None
        strength = abs(imbalance) * 100
        
        if bid_ratio > Config.BID_ASK_IMBALANCE_THRESHOLD:
            signal = 'BUY'  # More buyers than sellers
        elif ask_ratio > Config.BID_ASK_IMBALANCE_THRESHOLD:
            signal = 'SELL'  # More sellers than buyers
        
        return {
            'imbalance': imbalance,
            'bid_ratio': bid_ratio,
            'ask_ratio': ask_ratio,
            'signal': signal,
            'strength': strength
        }
    
    def detect_large_orders(self, current_data, threshold_multiplier=3):
        """
        Detect large orders (tape reading)
        Compares current volume to average volume
        """
        current_volume = current_data.get('volume', 0)
        
        if not hasattr(self, 'volume_history'):
            self.volume_history = deque(maxlen=20)
        
        self.volume_history.append(current_volume)
        
        if len(self.volume_history) < 5:
            return {
                'is_large_order': False,
                'signal': None
            }
        
        avg_volume = np.mean(list(self.volume_history)[:-1])  # Exclude current
        
        if current_volume > avg_volume * threshold_multiplier:
            # Large order detected
            # Determine if buying or selling based on price movement
            current_price = current_data.get('close')
            
            if self.last_price:
                if current_price > self.last_price:
                    signal = 'BUY'
                elif current_price < self.last_price:
                    signal = 'SELL'
                else:
                    signal = None
            else:
                signal = None
            
            self.last_price = current_price
            
            return {
                'is_large_order': True,
                'volume': current_volume,
                'avg_volume': avg_volume,
                'multiplier': current_volume / avg_volume if avg_volume > 0 else 0,
                'signal': signal
            }
        
        self.last_price = current_data.get('close')
        
        return {
            'is_large_order': False,
            'signal': None
        }
    
    def detect_aggressive_orders(self, market_data, prev_market_data):
        """
        Detect aggressive vs passive orders
        Aggressive: Market orders that cross the spread
        Passive: Limit orders that add liquidity
        """
        if not prev_market_data:
            return {
                'aggressive_buy': False,
                'aggressive_sell': False,
                'signal': None
            }
        
        current_price = market_data.get('ltp')
        prev_price = prev_market_data.get('ltp')
        prev_ask = prev_market_data.get('ask_price')
        prev_bid = prev_market_data.get('bid_price')
        
        if not all([current_price, prev_price, prev_ask, prev_bid]):
            return {
                'aggressive_buy': False,
                'aggressive_sell': False,
                'signal': None
            }
        
        aggressive_buy = current_price >= prev_ask
        aggressive_sell = current_price <= prev_bid
        
        signal = None
        if aggressive_buy:
            signal = 'BUY'
        elif aggressive_sell:
            signal = 'SELL'
        
        return {
            'aggressive_buy': aggressive_buy,
            'aggressive_sell': aggressive_sell,
            'signal': signal
        }
    
    def analyze_order_flow_divergence(self, price_data, volume_delta_data):
        """
        Detect divergence between price and order flow
        Bullish divergence: Price making lower lows, but CVD making higher lows
        Bearish divergence: Price making higher highs, but CVD making lower highs
        """
        if len(price_data) < 10 or len(volume_delta_data) < 10:
            return {
                'divergence': None,
                'signal': None
            }
        
        # Get recent price trend
        recent_prices = price_data[-10:]
        recent_deltas = volume_delta_data[-10:]
        
        price_trend = 'UP' if recent_prices[-1] > recent_prices[0] else 'DOWN'
        delta_trend = 'UP' if recent_deltas[-1] > recent_deltas[0] else 'DOWN'
        
        divergence = None
        signal = None
        
        if price_trend == 'DOWN' and delta_trend == 'UP':
            divergence = 'BULLISH'
            signal = 'BUY'
        elif price_trend == 'UP' and delta_trend == 'DOWN':
            divergence = 'BEARISH'
            signal = 'SELL'
        
        return {
            'divergence': divergence,
            'signal': signal,
            'price_trend': price_trend,
            'delta_trend': delta_trend
        }
    
    def analyze_order_flow(self, candle_data, market_data, prev_market_data=None):
        """
        Comprehensive order flow analysis
        Returns: dict with all order flow metrics and signals
        """
        # Calculate volume delta
        volume_delta = self.calculate_volume_delta(candle_data)
        
        # Calculate CVD
        cvd = self.calculate_cumulative_volume_delta(candle_data)
        
        # Analyze bid-ask imbalance
        bid_ask = self.analyze_bid_ask_imbalance(market_data)
        
        # Detect large orders
        large_orders = self.detect_large_orders(candle_data)
        
        # Detect aggressive orders
        aggressive = self.detect_aggressive_orders(market_data, prev_market_data) if prev_market_data else {'signal': None}
        
        # Aggregate signals
        signals = []
        if bid_ask['signal']:
            signals.append(bid_ask['signal'])
        if large_orders['signal']:
            signals.append(large_orders['signal'])
        if aggressive['signal']:
            signals.append(aggressive['signal'])
        
        # Determine overall order flow signal
        overall_signal = None
        if signals:
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            
            if buy_count > sell_count:
                overall_signal = 'BUY'
            elif sell_count > buy_count:
                overall_signal = 'SELL'
        
        # Calculate signal strength
        strength = 0
        if overall_signal:
            strength = (max(buy_count, sell_count) / len(signals)) * 100 if signals else 0
        
        return {
            'volume_delta': volume_delta,
            'cvd': cvd,
            'bid_ask_imbalance': bid_ask,
            'large_orders': large_orders,
            'aggressive_orders': aggressive,
            'overall_signal': overall_signal,
            'signal_strength': strength,
            'timestamp': candle_data.get('timestamp')
        }
