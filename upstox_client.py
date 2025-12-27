import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import urllib.parse

class UpstoxClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.upstox.com/v2"
        self.logger = logging.getLogger("UpstoxClient")
        
    def get_historical_candles(self, instrument_key, interval, from_date, to_date):
        """
        Fetches historical candles from Upstox.
        interval: 1minute, 5minute, 30minute, day, etc.
        """
        encoded_key = urllib.parse.quote(instrument_key)
        url = f"{self.base_url}/historical-candle/{encoded_key}/{interval}/{to_date}/{from_date}"
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            self.logger.info(f"DEBUG: Fetching candles from {url}")
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('data'):
                    candles = data['data']['candles']
                    # Upstox returns: [timestamp, open, high, low, close, volume, oi]
                    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                    
                    # Convert timestamp to datetime
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Sort by timestamp ascending
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    return df
                else:
                    self.logger.info(f"DEBUG: Upstox API Data Error: {data}")
                    self.logger.warning(f"No data or error in response: {data}")
                    return None
            else:
                self.logger.info(f"DEBUG: Upstox API HTTP Error {response.status_code}: {response.text}")
                self.logger.error(f"Upstox API Error: {response.text}")
                return None
        except Exception as e:
            self.logger.info(f"DEBUG: Upstox Exception: {e}")
            self.logger.error(f"Exception fetching candles: {e}")
            return None
            
    def get_market_ltp(self, instrument_key):
        """
        Get Last Traded Price (LTP) for a specific key
        """
        encoded_key = urllib.parse.quote(instrument_key)
        url = f"{self.base_url}/market-quote/ltp?instrument_key={encoded_key}"
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            self.logger.info(f"DEBUG: Fetching LTP from {url}")
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                self.logger.info(f"DEBUG: LTP API Data: {data}")
                
                # Upstox sometimes returns key with ':' instead of '|'
                alt_key = instrument_key.replace('|', ':')
                
                if instrument_key in data:
                    return data[instrument_key].get('last_price')
                elif alt_key in data:
                    return data[alt_key].get('last_price')
                
                # Fallback to first available value if only one key requested
                if len(data) == 1:
                    return list(data.values())[0].get('last_price')
                    
                return None
            self.logger.info(f"DEBUG: LTP API Error {response.status_code}: {response.text}")
            return None
        except Exception as e:
            self.logger.info(f"DEBUG: LTP API Exception: {e}")
            self.logger.error(f"Exception fetching LTP: {e}")
            return None
    def place_order(self, instrument_key, quantity, side, order_type="MARKET", product="I"):
        """
        Places an order on Upstox.
        product: I (Intraday), D (Delivery)
        """
        url = f"{self.base_url}/order/place"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        payload = {
            "quantity": int(quantity),
            "product": product,
            "validity": "DAY",
            "price": 0,
            "tag": "PullbackBot",
            "instrument_token": instrument_key,
            "order_type": order_type,
            "transaction_type": side,
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        
        try:
            self.logger.info(f"DEBUG: Placing order on {url} | Payload: {payload}")
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get('data', {}).get('order_id')
            self.logger.error(f"Order Placement Failed {response.status_code}: {response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Exception during order placement: {e}")
            return None

    def get_order_details(self, order_id):
        """
        Fetches details for a specific order to get execution price.
        """
        url = f"{self.base_url}/order/details?order_id={order_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            self.logger.error(f"Exception fetching order details: {e}")
            return None

    def get_positions(self):
        """
        Fetches current open positions.
        """
        url = f"{self.base_url}/portfolio/get-positions"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"Exception fetching positions: {e}")
            return []
