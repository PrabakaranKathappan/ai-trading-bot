"""
Complete Strategy Performance Tracking Implementation
This script safely adds the remaining code changes needed
"""

import re

def update_signal_generator():
    """Add contributing_strategies to signal_generator.py"""
    with open('signal_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the return statement in calculate_signal_strength
    old_return = """    return {
        'signal_type': signal_type,
        'strength': strength,
        'buy_score': buy_score,
        'sell_score': sell_score,
        'total_signals': total_signals
    }"""
    
    new_return = """    # Track which strategies contributed to this signal
    contributing_strategies = []
    if Config.ENABLED_STRATEGIES.get('RSI', True) and tech_signals.get('rsi_signal') in ['BUY', 'SELL']:
        contributing_strategies.append('RSI')
    if Config.ENABLED_STRATEGIES.get('MACD', True) and tech_signals.get('macd_signal') in ['BUY', 'SELL']:
        contributing_strategies.append('MACD')
    if Config.ENABLED_STRATEGIES.get('BOLLINGER_BANDS', True) and tech_signals.get('bb_signal') in ['BUY', 'SELL']:
        contributing_strategies.append('BOLLINGER_BANDS')
    if Config.ENABLED_STRATEGIES.get('EMA', True) and tech_signals.get('ema_signal') in ['BUY', 'SELL']:
        contributing_strategies.append('EMA')
    if Config.ENABLED_STRATEGIES.get('BREAKOUT', True) and tech_signals.get('breakout_signal') in ['BULLISH_BREAKOUT', 'BEARISH_BREAKOUT']:
        contributing_strategies.append('BREAKOUT')
    if Config.ENABLED_STRATEGIES.get('ORDER_FLOW', True) and order_flow_signals.get('overall_signal') in ['BUY', 'SELL']:
        contributing_strategies.append('ORDER_FLOW')
    
    return {
        'signal_type': signal_type,
        'strength': strength,
        'buy_score': buy_score,
        'sell_score': sell_score,
        'total_signals': total_signals,
        'contributing_strategies': contributing_strategies
    }"""
    
    if old_return in content:
        content = content.replace(old_return, new_return)
        with open('signal_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] Updated signal_generator.py")
        return True
    else:
        print("[FAIL] Could not find return statement in signal_generator.py")
        return False

def update_generate_signal():
    """Add contributing_strategies to signal dict in generate_signal method"""
    with open('signal_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add contributing_strategies to the signal dict
    old_signal = """            signal = {
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
            }"""
    
    new_signal = """            signal = {
                'timestamp': latest_candle.get('timestamp'),
                'signal_type': signal_result['signal_type'],
                'strength': signal_result['strength'],
                'current_nifty_price': current_price,
                'strike_price': strike_info['strike_price'],
                'option_type': strike_info['option_type'],
                'contributing_strategies': signal_result.get('contributing_strategies', []),
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
            }"""
    
    if old_signal in content:
        content = content.replace(old_signal, new_signal)
        with open('signal_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] Added contributing_strategies to signal dict")
        return True
    else:
        print("[FAIL] Could not find signal dict in generate_signal method")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Completing Strategy Performance Tracking Implementation")
    print("=" * 60)
    print()
    
    success = True
    
    # Update signal_generator.py
    if not update_signal_generator():
        success = False
    
    if not update_generate_signal():
        success = False
    
    if success:
        print("\n[OK] All changes applied successfully!")
        print("\nNext: Run this script to verify syntax:")
        print("  python -m py_compile signal_generator.py")
    else:
        print("\n[FAIL] Some changes failed. Please check the file manually.")
