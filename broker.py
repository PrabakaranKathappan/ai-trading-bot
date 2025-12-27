from datetime import datetime
import logging

class AbstractBroker:
    def get_market_data(self, symbol, timeframe, limit=100):
        raise NotImplementedError
    
    def place_order(self, symbol, order_type, quantity, side):
        raise NotImplementedError
        
    def get_positions(self):
        raise NotImplementedError

class MockBroker(AbstractBroker):
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.positions = []
        self.orders = []
        self.logger = logging.getLogger("MockBroker")
        
    def get_market_data(self, symbol, timeframe, limit=100):
        # In a real app, this connects to an API.
        # Here we will rely on an external data loader or mock generator in main strategies
        # But to satisfy the interface, we return None or expect data passed to strategy
        pass

    def place_order(self, symbol, order_type, quantity, side, price=None, sl=None, tp=None):
        self.logger.info(f"MOCK ORDER: {side} {quantity} {symbol} @ {price} | SL: {sl} | TP: {tp}")
        order = {
            "id": len(self.orders) + 1,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "sl": sl,
            "tp": tp,
            "time": datetime.now(),
            "status": "FILLED"
        }
        self.orders.append(order)
        # Simplified position tracking
        if side == "BUY" or side == "BUY_CALL" or side == "BUY_PUT":
            self.positions.append({
                "symbol": symbol, 
                "quantity": quantity,
                "entry_price": price if price else 0,
                "sl": sl,
                "tp": tp,
                "side": side
            })
        elif "SELL" in side:
            # Remove matching position logic (simplified - FIFO)
            for p in self.positions:
                if p["symbol"] == symbol:
                    self.positions.remove(p)
                    break
        return order
        
    def get_positions(self):
        return self.positions

    def square_off_all(self):
        """Mock closure of all positions"""
        self.logger.info("MOCK: Squaring off all positions.")
        for p in self.positions[:]:
            self.place_order(p['symbol'], "MARKET", p['quantity'], "SELL", price=p['entry_price']) # Simple exit
        self.positions = []
        return True

class UpstoxBroker(AbstractBroker):
    def __init__(self, upstox_client):
        self.client = upstox_client
        self.logger = logging.getLogger("UpstoxBroker")
        self.orders = [] # Local cache for UI
        self.capital = 0 # In real mode, we track via account balance
        
    def place_order(self, symbol, order_type, quantity, side, price=None, sl=None, tp=None):
        """
        Places a real order on Upstox.
        """
        self.logger.info(f"LIVE ORDER: {side} {quantity} {symbol} @ {price}")
        
        upstox_side = "BUY" if "BUY" in side else "SELL"
        
        # In this professional implementation, we fire the real order
        order_id = self.client.place_order(symbol, quantity, upstox_side, order_type)
        
        if not order_id:
            self.logger.error("Failed to place order on Upstox API")
            return None

        order = {
            "id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price, # Expected price
            "sl": sl,
            "tp": tp,
            "time": datetime.now(),
            "status": "PLACED"
        }
        self.orders.append(order)
        return order
        
    def get_positions(self):
        return self.client.get_positions()

    def square_off_all(self):
        """
        Fetches all open positions and closes them.
        """
        positions = self.get_positions()
        if not positions:
            self.logger.info("No open positions to square off.")
            return True

        self.logger.info(f"LIVE: Squaring off {len(positions)} positions.")
        for p in positions:
            symbol = p['instrument_token']
            qty = abs(int(p['net_quantity']))
            if qty > 0:
                side = "SELL" if int(p['net_quantity']) > 0 else "BUY"
                self.client.place_order(symbol, qty, side, "MARKET")
        return True
