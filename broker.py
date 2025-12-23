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

    def place_order(self, symbol, order_type, quantity, side):
        self.logger.info(f"MOCK ORDER: {side} {quantity} {symbol} @ MARKET")
        order = {
            "id": len(self.orders) + 1,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "time": datetime.now(),
            "status": "FILLED"
        }
        self.orders.append(order)
        # Simplified position tracking
        if side == "BUY":
            self.positions.append({"symbol": symbol, "quantity": quantity})
        elif side == "SELL":
            # Remove matching position logic (simplified)
            for p in self.positions:
                if p["symbol"] == symbol:
                    self.positions.remove(p)
                    break
        return order
        
    def get_positions(self):
        return self.positions
