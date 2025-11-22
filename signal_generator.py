from indicators import TechnicalIndicators
from order_flow import OrderFlowAnalyzer
from config import Config
from logger import Logger
import numpy as np

logger = Logger.get_logger('signal_generator')

class SignalGenerator:
    """Generate trading signals by combining technical indicators and order flow"""
    
    def __init__(self):
        self.order_flow_analyzer = OrderFlowAnalyzer()
        self.prev_market_data = None
    
    def calculate_signal_strength(self, technical_signals, order_flow_signals):
        """
        Calculate overall signal strength (0-100)
        Combines technical indicators and order flow analysis
        """
        buy_score = 0
        sell_score = 0
        total_signals = 0
        
        # Technical indicator signals (60% weight)
        tech_signals = technical_signals.get('signals', {})
        
        # RSI signal (15% weight)
        if tech_signals.get('rsi_signal') == 'BUY':
            buy_score += 15
            total_signals += 1
        elif tech_signals.get('rsi_signal') == 'SELL':
            sell_score += 15
            total_signals += 1
        
        # MACD signal (15% weight)
        if tech_signals.get('macd_signal') == 'BUY':
            buy_score += 15
            total_signals += 1
        elif tech_signals.get('macd_signal') == 'SELL':
            sell_score += 15
            total_signals += 1
        
        # Bollinger Bands signal (10% weight)
        if tech_signals.get('bb_signal') == 'BUY':
            buy_score += 10
            total_signals += 1
        elif tech_signals.get('bb_signal') == 'SELL':
            sell_score += 10
            total_signals += 1
        
        # EMA signal (10% weight)
        if tech_signals.get('ema_signal') == 'BUY':
            buy_score += 10
            total_signals += 1
        elif tech_signals.get('ema_signal') == 'SELL':
            sell_score += 10
            total_signals += 1
        
        # Breakout signal (10% weight)
        if tech_signals.get('breakout_signal') == 'BULLISH_BREAKOUT':
            buy_score += 10
            total_signals += 1
        elif tech_signals.get('breakout_signal') == 'BEARISH_BREAKOUT':
            sell_score += 10
            total_signals += 1
        
        # Order flow signals (40% weight)
        # Overall order flow signal (20% weight)
        if order_flow_signals.get('overall_signal') == 'BUY':
            buy_score += 20
            total_signals += 1
        elif order_flow_signals.get('overall_signal') == 'SELL':
            sell_score += 20
            total_signals += 1
        
        # Bid-ask imbalance (10% weight)
        bid_ask = order_flow_signals.get('bid_ask_imbalance', {})
        if bid_ask.get('signal') == 'BUY':
            buy_score += 10
            total_signals += 1
        elif bid_ask.get('signal') == 'SELL':
            sell_score += 10
            total_signals += 1
        
        # Large orders (10% weight)
        large_orders = order_flow_signals.get('large_orders', {})
        if large_orders.get('signal') == 'BUY':
            buy_score += 10
            total_signals += 1
        elif large_orders.get('signal') == 'SELL':
            sell_score += 10
            total_signals += 1
        
        # Determine overall signal and strength
        if buy_score > sell_score:
            signal_type = 'BUY'
            strength = buy_score
        elif sell_score > buy_score:
            signal_type = 'SELL'
            strength = sell_score
        else:
            signal_type = 'NEUTRAL'
            strength = 0
        
        return {
            'signal_type': signal_type,
            'strength': strength,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'total_signals': total_signals
        }
    
    def select_strike_price(self, current_nifty_price, signal_type, atm_offset=0):
        """
        Select appropriate strike price for options trading
        atm_offset: 0 for ATM, positive for OTM, negative for ITM
        """
        # Round to nearest 50 (Nifty options are in 50 point intervals)
        base_strike = round(current_nifty_price / 50) * 50
        
        # Adjust for offset
        strike_price = base_strike + (atm_offset * 50)
        
        # Determine option type
        if signal_type == 'BUY':
            option_type = 'CE'  # Call option
        elif signal_type == 'SELL':
            option_type = 'PE'  # Put option
        else:
            return None
        
        return {
            'strike_price': strike_price,
            'option_type': option_type,
            'atm_price': base_strike
        }
    
    def generate_signal(self, historical_data, current_market_data):
        """
        Generate trading signal based on all available data
        Returns: Complete signal with entry/exit recommendations
        """
        try:
            # Analyze technical indicators
            technical_analysis = TechnicalIndicators.analyze_indicators(historical_data)
            
            if not technical_analysis:
                logger.warning("Technical analysis failed - insufficient data")
                return None
            
            # Analyze order flow
            latest_candle = historical_data[-1]
            order_flow_analysis = self.order_flow_analyzer.analyze_order_flow(
                latest_candle,
                current_market_data,
                self.prev_market_data
            )
            
            # Store current market data for next iteration
            self.prev_market_data = current_market_data
            
            # Calculate signal strength
            signal_result = self.calculate_signal_strength(
                technical_analysis,
                order_flow_analysis
            )
            
            # Check if signal meets minimum strength threshold
            if signal_result['strength'] < Config.MIN_SIGNAL_STRENGTH:
                logger.info(f"Signal strength {signal_result['strength']} below threshold {Config.MIN_SIGNAL_STRENGTH}")
                return None
            
            # Select strike price
            current_price = technical_analysis['current_price']
            strike_info = self.select_strike_price(current_price, signal_result['signal_type'])
            
            if not strike_info:
                return None
            
            # Compile complete signal
            signal = {
                'timestamp': latest_candle.get('timestamp'),
                'signal_type': signal_result['signal_type'],
                'strength': signal_result['strength'],
                'current_nifty_price': current_price,
                'strike_price': strike_info['strike_price'],
                'option_type': strike_info['option_type'],
                'technical_analysis': {
                    'rsi': technical_analysis.get('rsi'),
                    'macd': technical_analysis.get('macd'),
                    'bb_position': technical_analysis.get('bollinger_bands', {}).get('position'),
                    'ema_short': technical_analysis.get('ema_short'),
                    'ema_long': technical_analysis.get('ema_long'),
                    'support': technical_analysis.get('support_resistance', {}).get('support'),
                    'resistance': technical_analysis.get('support_resistance', {}).get('resistance')
                },
                'order_flow_analysis': {
                    'volume_delta': order_flow_analysis.get('volume_delta'),
                    'cvd': order_flow_analysis.get('cvd'),
                    'bid_ask_imbalance': order_flow_analysis.get('bid_ask_imbalance', {}).get('imbalance'),
                    'large_order_detected': order_flow_analysis.get('large_orders', {}).get('is_large_order')
                },
                'buy_score': signal_result['buy_score'],
                'sell_score': signal_result['sell_score']
            }
            
            logger.info(f"Signal generated: {signal_result['signal_type']} with strength {signal_result['strength']}")
            Logger.log_signal(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def validate_signal(self, signal, current_positions):
        """
        Validate signal before execution
        Check for conflicting positions, market conditions, etc.
        """
        if not signal:
            return False
        
        # Check if we already have a position in the same direction
        for position in current_positions:
            if position.get('option_type') == signal.get('option_type'):
                logger.warning(f"Already have a {signal.get('option_type')} position")
                return False
        
        # Check if signal strength is sufficient
        if signal.get('strength', 0) < Config.MIN_SIGNAL_STRENGTH:
            return False
        
        # Additional validation can be added here
        # - Time of day checks
        # - Volatility checks
        # - News event checks
        
        return True
