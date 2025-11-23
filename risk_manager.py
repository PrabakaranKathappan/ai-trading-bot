from config import Config
from logger import Logger
from datetime import datetime

logger = Logger.get_logger('risk_manager')

class RiskManager:
    """Manage trading risk and position sizing"""
    
    def __init__(self, database):
        self.database = database
        self.capital = Config.CAPITAL
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk per trade
        Returns: number of lots to trade
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            logger.error("Invalid entry or stop loss price")
            return 0
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            logger.error("Risk per unit is zero")
            return 0
        
        # Calculate position size
        # For Nifty options, lot size is typically 50
        lot_size = 50
        
        # Maximum units we can buy with our risk limit
        max_units = Config.get_max_loss_per_trade() / risk_per_unit
        
        # Convert to lots (round down)
        lots = int(max_units / lot_size)
        
        # Ensure at least 1 lot
        if lots < 1:
            lots = 1
        
        # Calculate actual quantity
        quantity = lots * lot_size
        
        # Verify we have enough capital
        required_capital = entry_price * quantity
        if required_capital > self.capital * 0.5:  # Don't use more than 50% capital per trade
            # Reduce position size
            max_quantity = int((self.capital * 0.5) / entry_price)
            quantity = (max_quantity // lot_size) * lot_size
        
        logger.info(f"Position size calculated: {quantity} units ({quantity/lot_size} lots)")
        return quantity
    
    def calculate_stop_loss(self, entry_price, signal_type):
        """
        Calculate stop loss price
        """
        stop_loss_percent = Config.STOP_LOSS_PERCENT / 100
        
        if signal_type == 'BUY':
            # For long positions, stop loss is below entry
            stop_loss = entry_price * (1 - stop_loss_percent)
        else:
            # For short positions, stop loss is above entry
            stop_loss = entry_price * (1 + stop_loss_percent)
        
        return round(stop_loss, 2)
    
    def calculate_target(self, entry_price, signal_type):
        """
        Calculate target price
        """
        target_percent = Config.TARGET_PERCENT / 100
        
        if signal_type == 'BUY':
            # For long positions, target is above entry
            target = entry_price * (1 + target_percent)
        else:
            # For short positions, target is below entry
            target = entry_price * (1 - target_percent)
        
        return round(target, 2)
    
    def check_daily_loss_limit(self):
        """
        Check if daily loss limit has been reached
        Returns: True if we can continue trading, False if limit reached
        """
        today_pnl = self.database.get_today_pnl()
        
        if today_pnl < -Config.get_max_daily_loss():
            logger.warning(f"Daily loss limit reached: ₹{today_pnl:.2f} / ₹{-Config.get_max_daily_loss():.2f}")
            return False
        
        return True
    
    def check_max_positions(self, current_positions):
        """
        Check if maximum number of positions has been reached
        """
        if len(current_positions) >= Config.MAX_POSITIONS:
            logger.warning(f"Maximum positions reached: {len(current_positions)} / {Config.MAX_POSITIONS}")
            return False
        
        return True
    
    def should_exit_position(self, position, current_price):
        """
        Determine if a position should be exited
        Checks stop loss, target, and trailing stop
        """
        entry_price = position.get('entry_price')
        stop_loss = position.get('stop_loss')
        target = position.get('target')
        option_type = position.get('option_type')
        
        # Check stop loss
        if option_type == 'CE':  # Call option (long)
            if current_price <= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'exit_price': current_price
                }
            elif current_price >= target:
                return {
                    'should_exit': True,
                    'reason': 'TARGET',
                    'exit_price': current_price
                }
        else:  # Put option (short)
            if current_price >= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'exit_price': current_price
                }
            elif current_price <= target:
                return {
                    'should_exit': True,
                    'reason': 'TARGET',
                    'exit_price': current_price
                }
        
        # Check trailing stop
        trailing_stop = self.calculate_trailing_stop(position, current_price)
        if trailing_stop and trailing_stop.get('should_exit'):
            return trailing_stop
        
        return {
            'should_exit': False,
            'reason': None
        }
    
    def calculate_trailing_stop(self, position, current_price):
        """
        Calculate and check trailing stop
        """
        entry_price = position.get('entry_price')
        option_type = position.get('option_type')
        trailing_percent = Config.TRAILING_STOP_PERCENT / 100
        
        # Only activate trailing stop if in profit
        if option_type == 'CE':
            profit_percent = (current_price - entry_price) / entry_price
            if profit_percent > trailing_percent:
                # Calculate trailing stop level
                trailing_stop_price = current_price * (1 - trailing_percent)
                
                # Update position's trailing stop if higher than current stop loss
                if trailing_stop_price > position.get('stop_loss', 0):
                    return {
                        'should_update_stop': True,
                        'new_stop_loss': trailing_stop_price
                    }
        else:  # PE
            profit_percent = (entry_price - current_price) / entry_price
            if profit_percent > trailing_percent:
                trailing_stop_price = current_price * (1 + trailing_percent)
                
                if trailing_stop_price < position.get('stop_loss', float('inf')):
                    return {
                        'should_update_stop': True,
                        'new_stop_loss': trailing_stop_price
                    }
        
        return None
    
    def validate_trade(self, signal, current_positions):
        """
        Validate if a trade should be executed based on risk management rules
        """
        # Check daily loss limit
        if not self.check_daily_loss_limit():
            logger.warning("Trade rejected: Daily loss limit reached")
            return False
        
        # Check max positions
        if not self.check_max_positions(current_positions):
            logger.warning("Trade rejected: Maximum positions reached")
            return False
        
        # Check if we have enough capital
        # This is a simplified check - actual implementation should consider margin requirements
        total_exposure = sum(
            pos.get('entry_price', 0) * pos.get('quantity', 0) 
            for pos in current_positions
        )
        
        if total_exposure > self.capital * 0.8:  # Don't use more than 80% of capital
            logger.warning("Trade rejected: Insufficient capital")
            return False
        
        return True
    
    def calculate_pnl(self, entry_price, exit_price, quantity, option_type):
        """
        Calculate P&L for a trade
        """
        if option_type == 'CE':
            pnl = (exit_price - entry_price) * quantity
        else:  # PE
            pnl = (entry_price - exit_price) * quantity
        
        pnl_percent = (pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0
        
        return {
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2)
        }
    
    def get_risk_metrics(self):
        """
        Get current risk metrics
        """
        today_pnl = self.database.get_today_pnl()
        open_positions = self.database.get_open_positions()
        
        total_exposure = sum(
            pos.get('entry_price', 0) * pos.get('quantity', 0) 
            for pos in open_positions
        )
        
        return {
            'capital': self.capital,
            'today_pnl': today_pnl,
            'remaining_daily_loss': Config.get_max_daily_loss() + today_pnl,
            'open_positions': len(open_positions),
            'max_positions': Config.MAX_POSITIONS,
            'total_exposure': total_exposure,
            'available_capital': self.capital - total_exposure
        }
