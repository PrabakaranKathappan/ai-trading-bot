import time
from datetime import datetime, time as dt_time
import pytz
from upstox_handler import UpstoxClient
from signal_generator import SignalGenerator
from risk_manager import RiskManager
from database import Database
from config import Config
from logger import Logger

logger = Logger.get_logger('trading_engine')

class TradingEngine:
    """Main trading engine that orchestrates signal generation and execution"""
    
    def __init__(self):
        self.upstox = UpstoxClient()
        self.signal_generator = SignalGenerator()
        self.database = Database()
        self.risk_manager = RiskManager(self.database)
        self.is_running = False
        self.positions = []
        self.symbol = 'NSE_INDEX|Nifty 50'  # Nifty index symbol
        
    def initialize(self):
        """Initialize the trading engine"""
        logger.info("Initializing trading engine...")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return False
        
        # Authenticate with Upstox
        if not self.upstox.authenticate():
            logger.error("Failed to authenticate with Upstox")
            return False
        
        logger.info("Trading engine initialized successfully")
        return True
    
    def update_credentials(self, api_key, api_secret):
        """Update credentials and re-authenticate"""
        logger.info("Updating credentials...")
        self.upstox.set_credentials(api_key, api_secret)
        
        # Re-authenticate
        if self.upstox.authenticate():
            logger.info("Re-authentication successful")
            return True
        else:
            logger.error("Re-authentication failed")
            return False
    
    def is_market_open(self):
        """Check if market is currently open"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        current_time = now.time()
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = dt_time(Config.MARKET_OPEN_HOUR, Config.MARKET_OPEN_MINUTE)
        market_close = dt_time(Config.MARKET_CLOSE_HOUR, Config.MARKET_CLOSE_MINUTE)
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        return market_open <= current_time <= market_close
    
    def should_square_off(self):
        """Check if it's time to square off all positions"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        current_time = now.time()
        
        square_off_time = dt_time(Config.SQUARE_OFF_HOUR, Config.SQUARE_OFF_MINUTE)
        
        return current_time >= square_off_time
    
    def get_market_data(self):
        """Fetch current market data"""
        try:
            # Get Nifty spot price
            quote = self.upstox.get_market_quote(self.symbol)
            
            # Get historical data for analysis
            historical = self.upstox.get_historical_data(
                instrument_key=self.symbol,
                interval='1minute'
            )
            
            return {
                'quote': quote,
                'historical': historical
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def execute_signal(self, signal):
        """Execute a trading signal"""
        try:
            logger.info(f"Executing signal: {signal['signal_type']}")
            
            # Get current positions
            current_positions = self.database.get_open_positions()
            
            # Validate trade with risk manager
            if not self.risk_manager.validate_trade(signal, current_positions):
                logger.warning("Trade validation failed")
                return False
            
            # Construct option symbol
            # Format: NSE_FO|NIFTY24NOV24000CE
            expiry = self.get_current_weekly_expiry()
            strike = signal['strike_price']
            option_type = signal['option_type']
            option_symbol = f"NSE_FO|NIFTY{expiry}{int(strike)}{option_type}"
            
            # Get option price
            option_quote = self.upstox.get_market_quote(option_symbol)
            if not option_quote:
                logger.error(f"Failed to get quote for {option_symbol}")
                return False
            
            entry_price = option_quote['ltp']
            
            # Calculate stop loss and target
            stop_loss = self.risk_manager.calculate_stop_loss(entry_price, signal['signal_type'])
            target = self.risk_manager.calculate_target(entry_price, signal['signal_type'])
            
            # Calculate position size
            quantity = self.risk_manager.calculate_position_size(entry_price, stop_loss)
            
            if quantity == 0:
                logger.error("Position size is zero")
                return False
            
            # Place order
            order_side = 'BUY' if signal['signal_type'] == 'BUY' else 'SELL'
            order_result = self.upstox.place_order(
                symbol=option_symbol,
                quantity=quantity,
                side=order_side,
                order_type='MARKET'
            )
            
            if not order_result:
                logger.error("Failed to place order")
                return False
            
            # Record trade in database
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': option_symbol,
                'strike_price': strike,
                'option_type': option_type,
                'action': order_side,
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'status': 'OPEN',
                'signal_strength': signal['strength']
            }
            
            trade_id = self.database.add_trade(trade_data)
            
            # Add to positions
            position_data = {
                'symbol': option_symbol,
                'strike_price': strike,
                'option_type': option_type,
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'opened_at': datetime.now().isoformat()
            }
            
            position_id = self.database.add_position(position_data)
            
            Logger.log_trade(trade_data)
            logger.info(f"Trade executed successfully: {order_side} {quantity} {option_symbol} @ ₹{entry_price}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False
    
    def monitor_positions(self):
        """Monitor open positions and manage exits"""
        try:
            positions = self.database.get_open_positions()
            
            for position in positions:
                symbol = position['symbol']
                
                # Get current price
                quote = self.upstox.get_market_quote(symbol)
                if not quote:
                    continue
                
                current_price = quote['ltp']
                
                # Update position with current price
                unrealized_pnl = self.risk_manager.calculate_pnl(
                    position['entry_price'],
                    current_price,
                    position['quantity'],
                    position['option_type']
                )
                
                self.database.update_position(position['id'], {
                    'current_price': current_price,
                    'unrealized_pnl': unrealized_pnl['pnl']
                })
                
                # Check if position should be exited
                exit_decision = self.risk_manager.should_exit_position(position, current_price)
                
                if exit_decision['should_exit']:
                    self.close_position(position, current_price, exit_decision['reason'])
            
            # Check profit protection
            today_pnl = self.database.get_today_pnl()
            # Calculate unrealized P&L from open positions
            unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions)
            total_pnl = today_pnl + unrealized_pnl
            
            if self.risk_manager.check_profit_protection(total_pnl):
                logger.warning("Profit protection triggered! Squaring off all positions.")
                self.square_off_all_positions()
                self.stop()
                
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    def close_position(self, position, exit_price, reason):
        """Close a position"""
        try:
            logger.info(f"Closing position: {position['symbol']} - Reason: {reason}")
            
            # Place exit order
            order_side = 'SELL' if position['option_type'] == 'CE' else 'BUY'
            order_result = self.upstox.place_order(
                symbol=position['symbol'],
                quantity=position['quantity'],
                side=order_side,
                order_type='MARKET'
            )
            
            if not order_result:
                logger.error("Failed to place exit order")
                return False
            
            # Calculate P&L
            pnl_result = self.risk_manager.calculate_pnl(
                position['entry_price'],
                exit_price,
                position['quantity'],
                position['option_type']
            )
            
            # Update position in database
            self.database.close_position(position['id'])
            
            # Update trade record
            trade_data = {
                'exit_price': exit_price,
                'pnl': pnl_result['pnl'],
                'pnl_percent': pnl_result['pnl_percent'],
                'status': 'CLOSED',
                'notes': reason
            }
            
            # Find corresponding trade and update it
            # This is simplified - you may need to track trade_id in position
            
            logger.info(f"Position closed: P&L = ₹{pnl_result['pnl']:.2f} ({pnl_result['pnl_percent']:.2f}%)")
            Logger.log_trade({**position, **trade_data})
            
            return True
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False
    
    def square_off_all_positions(self):
        """Square off all open positions at end of day"""
        logger.info("Squaring off all positions...")
        
        positions = self.database.get_open_positions()
        
        for position in positions:
            quote = self.upstox.get_market_quote(position['symbol'])
            if quote:
                self.close_position(position, quote['ltp'], 'SQUARE_OFF')
    
    def get_current_weekly_expiry(self):
        """Get current week's Nifty expiry date in format YYMMMDD (e.g., 24NOV28)"""
        # This is a simplified version - actual implementation should calculate
        # the Thursday of current week
        now = datetime.now()
        # For demo purposes, returning a placeholder
        return now.strftime('%y%b%d').upper()
    
    def run(self):
        """Main trading loop"""
        logger.info("Starting trading engine...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Check if market is open
                if not self.is_market_open():
                    logger.info("Market is closed. Waiting...")
                    time.sleep(60)  # Check every minute
                    continue
                
                # Check if it's time to square off
                if self.should_square_off():
                    self.square_off_all_positions()
                    logger.info("All positions squared off. Stopping for the day.")
                    break
                
                # Get market data
                market_data = self.get_market_data()
                if not market_data:
                    time.sleep(10)
                    continue
                
                # Generate signal
                signal = self.signal_generator.generate_signal(
                    market_data['historical'],
                    market_data['quote']
                )
                
                # Execute signal if valid
                if signal and self.signal_generator.validate_signal(signal, self.database.get_open_positions()):
                    self.execute_signal(signal)
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Wait before next iteration (e.g., check every minute)
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Received stop signal")
                self.stop()
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(10)
        
        logger.info("Trading engine stopped")
    
    def stop(self):
        """Stop the trading engine"""
        logger.info("Stopping trading engine...")
        self.is_running = False
