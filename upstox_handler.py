import upstox_client
from upstox_client.rest import ApiException
import webbrowser
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import time
from config import Config
from logger import Logger

logger = Logger.get_logger('upstox')

class UpstoxClient:
    """Upstox API client for market data and order execution"""
    
    def __init__(self):
        self.api_key = Config.UPSTOX_API_KEY
        self.api_secret = Config.UPSTOX_API_SECRET
        self.redirect_uri = Config.UPSTOX_REDIRECT_URI
        self.access_token = None
        self.api_version = '2.0'
        self.configuration = None
        self.api_instance = None
        
    def set_credentials(self, api_key, api_secret):
        """Update API credentials dynamically"""
        self.api_key = api_key
        self.api_secret = api_secret
        # Also update Config to keep them in sync
        Config.set_credentials(api_key, api_secret)
        
    def get_authorization_url(self):
        """Generate authorization URL for OAuth flow"""
        auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?client_id={self.api_key}&redirect_uri={self.redirect_uri}&response_type=code"
        return auth_url
    
    def authenticate(self, auth_code=None):
        """
        Authenticate with Upstox API using OAuth 2.0
        If auth_code is None, will open browser for user to login
        """
        try:
            if not self.api_key or not self.api_secret:
                logger.warning("API credentials not set. Skipping authentication.")
                return False

            if not auth_code:
                # Open browser for user authentication
                auth_url = self.get_authorization_url()
                logger.info(f"Opening browser for authentication: {auth_url}")
                webbrowser.open(auth_url)
                
                # Wait for user to provide auth code
                print("\n" + "="*60)
                print("UPSTOX AUTHENTICATION")
                print("="*60)
                print("1. Browser window opened for Upstox login")
                print("2. After login, you'll be redirected to a URL")
                print("3. Copy the 'code' parameter from the redirected URL")
                print("="*60)
                auth_code = input("\nEnter the authorization code: ").strip()
            
            # Exchange auth code for access token
            api_instance = upstox_client.LoginApi()
            api_response = api_instance.token(
                api_version=self.api_version,
                code=auth_code,
                client_id=self.api_key,
                client_secret=self.api_secret,
                redirect_uri=self.redirect_uri,
                grant_type='authorization_code'
            )
            
            self.access_token = api_response.access_token
            
            # Configure API client
            self.configuration = upstox_client.Configuration()
            self.configuration.access_token = self.access_token
            
            logger.info("Successfully authenticated with Upstox API")
            return True
            
        except ApiException as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return False
    
    def get_market_quote(self, symbol):
        """
        Get real-time market quote for a symbol
        symbol format: NSE_FO|NIFTY24NOV24000CE
        """
        try:
            api_instance = upstox_client.MarketQuoteApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.get_full_market_quote(symbol, self.api_version)
            
            if api_response.status == 'success':
                data = api_response.data[symbol]
                return {
                    'symbol': symbol,
                    'ltp': data.last_price,
                    'open': data.ohlc.open,
                    'high': data.ohlc.high,
                    'low': data.ohlc.low,
                    'close': data.ohlc.close,
                    'volume': data.volume,
                    'bid_price': data.depth.buy[0].price if data.depth.buy else None,
                    'ask_price': data.depth.sell[0].price if data.depth.sell else None,
                    'bid_qty': data.depth.buy[0].quantity if data.depth.buy else None,
                    'ask_qty': data.depth.sell[0].quantity if data.depth.sell else None,
                    'oi': data.oi if hasattr(data, 'oi') else None,
                    'timestamp': datetime.now().isoformat()
                }
            return None
            
        except ApiException as e:
            logger.error(f"Error fetching market quote for {symbol}: {e}")
            return None
    
    def get_historical_data(self, instrument_key, interval='1minute', from_date=None, to_date=None):
        """
        Get historical candle data
        interval: 1minute, 30minute, day, week, month
        """
        try:
            if not from_date:
                from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            
            api_instance = upstox_client.HistoryApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.get_historical_candle_data(
                instrument_key=instrument_key,
                interval=interval,
                to_date=to_date,
                from_date=from_date,
                api_version=self.api_version
            )
            
            if api_response.status == 'success':
                candles = []
                for candle in api_response.data.candles:
                    candles.append({
                        'timestamp': candle[0],
                        'open': candle[1],
                        'high': candle[2],
                        'low': candle[3],
                        'close': candle[4],
                        'volume': candle[5],
                        'oi': candle[6] if len(candle) > 6 else None
                    })
                return candles
            return []
            
        except ApiException as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def place_order(self, symbol, quantity, side, order_type='MARKET', price=None, trigger_price=None):
        """
        Place an order
        side: BUY or SELL
        order_type: MARKET or LIMIT
        """
        try:
            if Config.TRADING_MODE == 'paper':
                logger.info(f"PAPER TRADE: {side} {quantity} {symbol} @ {order_type}")
                return {
                    'order_id': f"PAPER_{int(time.time())}",
                    'status': 'COMPLETE',
                    'message': 'Paper trade executed'
                }
            
            api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
            
            body = upstox_client.PlaceOrderRequest(
                quantity=quantity,
                product='I',  # Intraday
                validity='DAY',
                price=price if order_type == 'LIMIT' else 0,
                tag='trading_bot',
                instrument_token=symbol,
                order_type=order_type,
                transaction_type=side,
                disclosed_quantity=0,
                trigger_price=trigger_price if trigger_price else 0,
                is_amo=False
            )
            
            api_response = api_instance.place_order(body, self.api_version)
            
            if api_response.status == 'success':
                logger.info(f"Order placed successfully: {api_response.data.order_id}")
                return {
                    'order_id': api_response.data.order_id,
                    'status': 'PENDING',
                    'message': 'Order placed successfully'
                }
            else:
                logger.error(f"Order placement failed: {api_response}")
                return None
                
        except ApiException as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_order_status(self, order_id):
        """Get status of an order"""
        try:
            if Config.TRADING_MODE == 'paper':
                return {'status': 'COMPLETE', 'filled_quantity': 0}
            
            api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.get_order_details(
                api_version=self.api_version,
                order_id=order_id
            )
            
            if api_response.status == 'success':
                order = api_response.data[0]
                return {
                    'status': order.status,
                    'filled_quantity': order.filled_quantity,
                    'average_price': order.average_price,
                    'order_timestamp': order.order_timestamp
                }
            return None
            
        except ApiException as e:
            logger.error(f"Error fetching order status: {e}")
            return None
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        try:
            if Config.TRADING_MODE == 'paper':
                logger.info(f"PAPER TRADE: Cancel order {order_id}")
                return True
            
            api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.cancel_order(order_id, self.api_version)
            
            if api_response.status == 'success':
                logger.info(f"Order cancelled successfully: {order_id}")
                return True
            return False
            
        except ApiException as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_positions(self):
        """Get current positions"""
        try:
            if Config.TRADING_MODE == 'paper':
                return []
            
            api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.get_positions(self.api_version)
            
            if api_response.status == 'success':
                positions = []
                for pos in api_response.data:
                    positions.append({
                        'symbol': pos.instrument_token,
                        'quantity': pos.quantity,
                        'average_price': pos.average_price,
                        'last_price': pos.last_price,
                        'pnl': pos.pnl
                    })
                return positions
            return []
            
        except ApiException as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_option_chain(self, symbol='NIFTY', expiry_date=None):
        """Get option chain data for Nifty"""
        try:
            # This is a placeholder - actual implementation depends on Upstox API
            # You may need to use get_market_quote for individual strikes
            logger.info(f"Fetching option chain for {symbol}")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            return []
