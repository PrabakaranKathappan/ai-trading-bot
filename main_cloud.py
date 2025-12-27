import time
import requests
import threading
import pandas as pd
import numpy as np
import logging
import schedule
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from strategy import InstitutionalPullbackStrategy
from broker import MockBroker

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingApp")

# Initialize Flask
app = Flask(__name__)

# Initialize Bot Components
config = Config()
paper_broker = MockBroker(initial_capital=config.CAPITAL)
live_broker = None # Initialized after Upstox login
strategy = InstitutionalPullbackStrategy(config)

# Global State for Bot
latest_price = 0.0 # Bank Nifty
nifty_price = 0.0  # Nifty 50
sensex_price = 0.0 # Sensex
is_connected = True if config.UPSTOX_ACCESS_TOKEN else False
bot_active = False # Master Control
access_token = config.UPSTOX_ACCESS_TOKEN if config.UPSTOX_ACCESS_TOKEN else None
upstox_client = None

def build_option_symbol(idx_key, spot_price, side, moneyness, expiry_type):
    """
    Constructs the Upstox/Broker symbol for the target option.
    Example: NSE_FO|NIFTY25JAN24500CE
    """
    # 1. Determine Strike Step
    strike_step = 100
    if idx_key == "NIFTY": strike_step = 50
    elif idx_key == "SENSEX": strike_step = 100
    
    # 2. Round Spot to ATM
    atm_strike = round(spot_price / strike_step) * strike_step
    
    # 3. Apply Moneyness Offset
    target_strike = atm_strike
    if moneyness == "ITM":
        if "BUY" in side and "PUT" not in side: # CALL
            target_strike = atm_strike - strike_step
        else: # PUT
            target_strike = atm_strike + strike_step
    elif moneyness == "OTM":
        if "BUY" in side and "PUT" not in side: # CALL
            target_strike = atm_strike + strike_step
        else: # PUT
            target_strike = atm_strike - strike_step
            
    # 4. Handle Expiry Date Logic
    # In a real app, this would calculate actual dates or fetch from Upstox.
    # For this professional mock, we include the specific expiry type in the symbol.
    suffix = "CE" if ("BUY" in side and "PUT" not in side) else "PE"
    
    # Mapping for cleaner logging
    exp_map = {
        "CURR_WEEK": "WK1",
        "NEXT_WEEK": "WK2",
        "CURR_MONTH": "MN1",
        "NEXT_MONTH": "MN2",
        "WEEKLY": "WK1", # Backwards compatibility
        "MONTHLY": "MN1"  # Backwards compatibility
    }
    exp_code = exp_map.get(expiry_type, expiry_type)

    return f"{idx_key}_{exp_code}_{int(target_strike)}_{suffix}"

from upstox_client import UpstoxClient

def generate_mock_data(length=100):
    """
    Generates synthetic OHLCV data to simulate market movements.
    """
    dates = [datetime.now() - timedelta(minutes=i*5) for i in range(length)]
    dates.reverse()
    
    # Random walk for price
    base_price = 45000
    prices = [base_price]
    for _ in range(length-1):
        change = np.random.normal(0, 20) # Random fluctuation
        prices.append(prices[-1] + change)
        
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p + abs(np.random.normal(0, 10)) for p in prices],
        'low': [p - abs(np.random.normal(0, 10)) for p in prices],
        'close': [p + np.random.normal(0, 5) for p in prices],
        'volume': [int(abs(np.random.normal(1000, 200))) for _ in range(length)]
    })
    return df

def trading_job():
    global latest_price, nifty_price, sensex_price, upstox_client, is_connected, bot_active
    logger.info(f"Fetching market data... Connected: {is_connected}, Bot Active: {bot_active}")
    
    df = None
    
    if is_connected and config.UPSTOX_ACCESS_TOKEN:
        if not upstox_client:
            upstox_client = UpstoxClient(config.UPSTOX_ACCESS_TOKEN)
            
        # Correct Instrument Key for BANKNIFTY Spot Index
        # NSE_INDEX|Nifty Bank is often 'NSE_INDEX|Nifty Bank' or 'NSE_INDEX|26009'
        # Let's use the one that works or try to fetch it.
        instrument_key = "NSE_INDEX|Nifty Bank" 
        
        # Upstox Interval Map (Historical only supports: 1minute, 30minute, day, week, month)
        # We will fetch 1minute data and use it.
        interval = "1minute"
        
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        df = upstox_client.get_historical_candles(instrument_key, interval, from_date, to_date)
        
        if df is not None and not df.empty:
            logger.info("Fetched REAL data from Upstox")
            latest_price = df.iloc[-1]['close'] 
            
            # --- FETCH ALL 3 LTPs ---
            # 1. Bank Nifty
            bn_ltp = upstox_client.get_market_ltp(config.INDEX_MAPPINGS["BANKNIFTY"])
            if bn_ltp: 
                latest_price = bn_ltp
                logger.info(f"BN LTP: {latest_price}")
            
            # 2. Nifty 50
            nifty_ltp = upstox_client.get_market_ltp(config.INDEX_MAPPINGS["NIFTY"])
            if nifty_ltp: 
                nifty_price = nifty_ltp
                logger.info(f"Nifty LTP: {nifty_price}")
                
            # 3. Sensex
            sensex_ltp = upstox_client.get_market_ltp(config.INDEX_MAPPINGS["SENSEX"])
            if sensex_ltp: 
                sensex_price = sensex_ltp
                logger.info(f"Sensex LTP: {sensex_price}")
        else:
            logger.warning("Failed to fetch Upstox data, falling back to MOCK")
            df = generate_mock_data(length=50)
            latest_price = df.iloc[-1]['close']
            nifty_price = 24000.0 + np.random.normal(0, 50)
            sensex_price = 80000.0 + np.random.normal(0, 100)
            
    else:
        # Fallback to Mock Data
        df = generate_mock_data(length=50)
        latest_price = df.iloc[-1]['close']
        nifty_price = 24000.0 + np.random.normal(0, 50)
        sensex_price = 80000.0 + np.random.normal(0, 100)
    
    if not bot_active:
        logger.info("Bot is STOPPED. Skipping strategy execution.")
        return

    # Apply Strategy per selected index
    # We use 'df' (Bank Nifty candles) as a technical proxy for the touch-EMA logic 
    # but we use the specific index price for crossing.
    
    for idx_key in config.SELECTED_INDICES:
        idx_key = idx_key.strip()
        if not idx_key: continue
        
        # Get current price for this specific index
        current_idx_price = latest_price
        if idx_key == "NIFTY": current_idx_price = nifty_price
        elif idx_key == "SENSEX": current_idx_price = sensex_price
        
        full_symbol = config.INDEX_MAPPINGS.get(idx_key)
        if not full_symbol: continue
        
        logger.info(f"Analyzing {idx_key} at {current_idx_price}...")
        
        # Calculate Indicators 
        df_analysis = strategy.calculate_indicators(df.copy())
        # We override the last close with current real-time price for the check
        df_analysis.loc[df_analysis.index[-1], 'close'] = current_idx_price
        
        signal_data = strategy.check_signal(df_analysis)
        
        if signal_data:
            side = signal_data['side']
            entry = signal_data['entry_price']
            sl = signal_data['stop_loss']
            tp = signal_data['take_profit']
            
            # Get index-specific settings
            lot_count = getattr(config, f"LOT_SIZE_{idx_key}")
            quantity = lot_count * config.LOT_MULTIPLIERS.get(idx_key, 1)
            
            moneyness = getattr(config, f"MONEYNESS_{idx_key}")
            expiry = getattr(config, f"EXPIRY_{idx_key}")
            
            # Build Option Symbol
            option_symbol = build_option_symbol(idx_key, current_idx_price, side, moneyness, expiry)
            
            logger.info(f"SIGNAL DETECTED for {idx_key}: {side} | Target Option: {option_symbol}")
            
            # Place Paper Trade if enabled
            if config.PAPER_TRADING_ENABLED:
                logger.info(f"Executing Paper Trade for {option_symbol}...")
                paper_broker.place_order(option_symbol, "MARKET", quantity, side, price=current_idx_price, sl=sl, tp=tp)
                
            # Place Live Trade if enabled
            if config.LIVE_TRADING_ENABLED and live_broker:
                logger.info(f"Executing LIVE Trade for {option_symbol} on Upstox...")
                # Note: For live, we would use the actual Upstox instrument key
                live_broker.place_order(option_symbol, "MARKET", quantity, side, price=current_idx_price, sl=sl, tp=tp)
            
    # Combine positions/orders for display
    all_positions = paper_broker.get_positions()
    all_orders = paper_broker.orders[:]
    
    if live_broker:
        all_positions += live_broker.get_positions()
        all_orders += live_broker.orders
        
    if all_positions:
        logger.info(f"Open Positions: {len(all_positions)}")

def run_scheduler():
    """Background thread to run schedule"""
    # Run once immediately
    trading_job()
    
    # Schedule
    schedule.every(config.CHECK_INTERVAL_SECONDS).seconds.do(trading_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask Routes
from flask import Flask, render_template, request, redirect, url_for
@app.route('/')
def dashboard():
    # Merge for UI
    positions = paper_broker.get_positions()
    orders = paper_broker.orders[:]
    
    if live_broker:
        positions += live_broker.get_positions()
        orders += live_broker.orders
    
    # Calculate P&L for display
    total_pnl = 0
    display_positions = []
    
    for p in positions:
        # Handle Upstox Position Object vs Mock Dict
        symbol = p.get('symbol') or p.get('instrument_token')
        entry_price = float(p.get('entry_price') or p.get('avg_price') or 0)
        qty = int(p.get('quantity') or p.get('net_quantity') or 0)
        
        # Determine current mark
        current_mark = latest_price # Fallback to Spot
        
        # If it's a real Upstox position, try to get LTP for that symbol
        if is_connected and upstox_client and symbol:
            try:
                ltp = upstox_client.get_market_ltp(symbol)
                if ltp: current_mark = ltp
            except:
                pass
        
        pnl = (current_mark - entry_price) * qty
        # Inverse P&L for Puts if it's a mock position (Real Upstox pos handles signs in net_quantity)
        if p.get('side') == 'BUY_PUT' and 'net_quantity' not in p:
             pnl = (entry_price - current_mark) * qty
             
        p['pnl'] = pnl
        p['current_price'] = current_mark
        p['entry_price'] = entry_price # Normalize for UI
        p['quantity'] = qty
        p['symbol_display'] = symbol if "|" not in str(symbol) else str(symbol).split("|")[1]
        
        total_pnl += pnl
        display_positions.append(p)
    
    return render_template('index.html', 
                         pnl=total_pnl, 
                         positions=display_positions, 
                         orders=orders,
                         capital=paper_broker.capital + total_pnl,
                         config=config,
                         is_connected=is_connected,
                         bot_active=bot_active,
                         latest_price=latest_price,
                         nifty_price=nifty_price,
                         sensex_price=sensex_price)

@app.route('/toggle_bot', methods=['POST'])
def toggle_bot():
    global bot_active
    bot_active = not bot_active
    logger.info(f"Bot toggled: {bot_active}")
    return redirect(url_for('dashboard'))

@app.route('/square_off', methods=['POST'])
def square_off():
    # Square off both paper and live
    paper_broker.square_off_all()
    if live_broker:
        live_broker.square_off_all()
    logger.info("Manual Square Off triggered from UI.")
    return redirect(url_for('dashboard'))

@app.route('/update_selection', methods=['POST'])
def update_selection():
    selected = []
    if request.form.get('idx_nifty') == 'on': selected.append('NIFTY')
    if request.form.get('idx_banknifty') == 'on': selected.append('BANKNIFTY')
    if request.form.get('idx_sensex') == 'on': selected.append('SENSEX')
    
    if not selected: selected = ['BANKNIFTY'] # Default
    
    config.SELECTED_INDICES = selected
    
    # Persist to .env
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    new_lines = []
    updated = False
    for line in lines:
        if line.startswith("SELECTED_INDICES="):
            new_lines.append(f"SELECTED_INDICES={','.join(selected)}\n")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"SELECTED_INDICES={','.join(selected)}\n")
        
    with open(env_path, "w") as f:
        f.writelines(new_lines)
        
    return redirect(url_for('dashboard'))

@app.route('/login_upstox')
def login_upstox():
    if not config.UPSTOX_API_KEY or not config.UPSTOX_REDIRECT_URI:
        return "Please configure API Credentials first in Settings."
        
    auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={config.UPSTOX_API_KEY}&redirect_uri={config.UPSTOX_REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global is_connected, access_token
    code = request.args.get('code')
    
    if not code:
        return "Error: No code received from Upstox."
        
    # Exchange Code for Token
    url = "https://api.upstox.com/v2/login/authorization/token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'code': code,
        'client_id': config.UPSTOX_API_KEY,
        'client_secret': config.UPSTOX_API_SECRET,
        'redirect_uri': config.UPSTOX_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response_json = response.json()
        
        if response.status_code == 200:
            access_token = response_json.get('access_token')
            is_connected = True
            config.UPSTOX_ACCESS_TOKEN = access_token
            
            # Initialize Live Broker
            global live_broker, upstox_client
            upstox_client = UpstoxClient(access_token)
            live_broker = UpstoxBroker(upstox_client)
            
            # Persist token to .env
            env_path = ".env"
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()
            
            new_lines = []
            token_updated = False
            for line in lines:
                if line.startswith("UPSTOX_ACCESS_TOKEN="):
                    new_lines.append(f"UPSTOX_ACCESS_TOKEN={access_token}\n")
                    token_updated = True
                else:
                    new_lines.append(line)
            
            if not token_updated:
                new_lines.append(f"UPSTOX_ACCESS_TOKEN={access_token}\n")
            
            with open(env_path, "w") as f:
                f.writelines(new_lines)

            logger.info("Upstox Login Successful and Token Persisted!")
            return redirect(url_for('dashboard'))
        else:
            logger.error(f"Upstox Login Failed: {response.text}")
            return f"Login Failed: {response_json.get('message', 'Unknown Error')}"
            
    except Exception as e:
        logger.error(f"Error during token exchange: {e}")
        return f"Error: {e}"

@app.route('/settings', methods=['POST'])
def save_settings():
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')
    redirect_uri = request.form.get('redirect_uri')
    paper_enabled = request.form.get('paper_enabled') == 'on'
    live_enabled = request.form.get('live_enabled') == 'on'
    option_moneyness_nifty = request.form.get('moneyness_nifty', 'ATM')
    option_moneyness_bn = request.form.get('moneyness_banknifty', 'ATM')
    option_moneyness_sensex = request.form.get('moneyness_sensex', 'ATM')
    
    expiry_nifty = request.form.get('expiry_nifty', 'WEEKLY')
    expiry_bn = request.form.get('expiry_banknifty', 'MONTHLY')
    expiry_sensex = request.form.get('expiry_sensex', 'WEEKLY')
    
    # Safety fallbacks for Int conversion
    def safe_int(val, default=1):
        try:
            return int(val) if val and str(val).strip() else default
        except:
            return default

    lot_size_nifty = safe_int(request.form.get('lot_size_nifty'))
    lot_size_banknifty = safe_int(request.form.get('lot_size_banknifty'))
    lot_size_sensex = safe_int(request.form.get('lot_size_sensex'))
    
    # Selected Indices
    selected_indices = []
    if request.form.get('idx_banknifty') == 'on': selected_indices.append('BANKNIFTY')
    if request.form.get('idx_nifty') == 'on': selected_indices.append('NIFTY')
    if request.form.get('idx_sensex') == 'on': selected_indices.append('SENSEX')
    
    # Defaults to BANKNIFTY if nothing selected
    if not selected_indices: selected_indices = ['BANKNIFTY']
    selected_indices_str = ",".join(selected_indices)

    # Update Config Object
    config.UPSTOX_API_KEY = api_key
    config.UPSTOX_API_SECRET = api_secret
    config.UPSTOX_REDIRECT_URI = redirect_uri
    config.PAPER_TRADING_ENABLED = paper_enabled
    config.LIVE_TRADING_ENABLED = live_enabled
    config.SELECTED_INDICES = selected_indices
    config.MONEYNESS_NIFTY = option_moneyness_nifty
    config.MONEYNESS_BANKNIFTY = option_moneyness_bn
    config.MONEYNESS_SENSEX = option_moneyness_sensex
    
    config.EXPIRY_NIFTY = expiry_nifty
    config.EXPIRY_BANKNIFTY = expiry_bn
    config.EXPIRY_SENSEX = expiry_sensex
    config.LOT_SIZE_NIFTY = lot_size_nifty
    config.LOT_SIZE_BANKNIFTY = lot_size_banknifty
    config.LOT_SIZE_SENSEX = lot_size_sensex
    
    # Update .env file
    env_path = ".env"
    
    # Read existing lines
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    # Helper to update or append
    new_lines = []
    keys_updated = {
        'UPSTOX_API_KEY': False, 
        'UPSTOX_API_SECRET': False, 
        'UPSTOX_REDIRECT_URI': False,
        'PAPER_TRADING_ENABLED': False,
        'LIVE_TRADING_ENABLED': False,
        'SELECTED_INDICES': False,
        'MONEYNESS_NIFTY': False,
        'MONEYNESS_BANKNIFTY': False,
        'MONEYNESS_SENSEX': False,
        'EXPIRY_NIFTY': False,
        'EXPIRY_BANKNIFTY': False,
        'EXPIRY_SENSEX': False,
        'LOT_SIZE_NIFTY': False,
        'LOT_SIZE_BANKNIFTY': False,
        'LOT_SIZE_SENSEX': False
    }
    
    for line in lines:
        if "=" in line:
             key = line.split('=')[0].strip()
             if key in keys_updated:
                if key == 'UPSTOX_API_KEY':
                    new_lines.append(f"UPSTOX_API_KEY={api_key}\n")
                elif key == 'UPSTOX_API_SECRET':
                    new_lines.append(f"UPSTOX_API_SECRET={api_secret}\n")
                elif key == 'UPSTOX_REDIRECT_URI':
                    new_lines.append(f"UPSTOX_REDIRECT_URI={redirect_uri}\n")
                elif key == 'PAPER_TRADING_ENABLED':
                    new_lines.append(f"PAPER_TRADING_ENABLED={paper_enabled}\n")
                elif key == 'LIVE_TRADING_ENABLED':
                    new_lines.append(f"LIVE_TRADING_ENABLED={live_enabled}\n")
                elif key == 'SELECTED_INDICES':
                    new_lines.append(f"SELECTED_INDICES={selected_indices_str}\n")
                elif key == 'MONEYNESS_NIFTY':
                    new_lines.append(f"MONEYNESS_NIFTY={option_moneyness_nifty}\n")
                elif key == 'MONEYNESS_BANKNIFTY':
                    new_lines.append(f"MONEYNESS_BANKNIFTY={option_moneyness_bn}\n")
                elif key == 'MONEYNESS_SENSEX':
                    new_lines.append(f"MONEYNESS_SENSEX={option_moneyness_sensex}\n")
                elif key == 'EXPIRY_NIFTY':
                    new_lines.append(f"EXPIRY_NIFTY={expiry_nifty}\n")
                elif key == 'EXPIRY_BANKNIFTY':
                    new_lines.append(f"EXPIRY_BANKNIFTY={expiry_bn}\n")
                elif key == 'EXPIRY_SENSEX':
                    new_lines.append(f"EXPIRY_SENSEX={expiry_sensex}\n")
                elif key == 'LOT_SIZE_NIFTY':
                    new_lines.append(f"LOT_SIZE_NIFTY={lot_size_nifty}\n")
                elif key == 'LOT_SIZE_BANKNIFTY':
                    new_lines.append(f"LOT_SIZE_BANKNIFTY={lot_size_banknifty}\n")
                elif key == 'LOT_SIZE_SENSEX':
                    new_lines.append(f"LOT_SIZE_SENSEX={lot_size_sensex}\n")
                keys_updated[key] = True
             else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    # Append if missing
    for key, updated in keys_updated.items():
        if not updated:
            if key == 'UPSTOX_API_KEY':
                new_lines.append(f"UPSTOX_API_KEY={api_key}\n")
            elif key == 'UPSTOX_API_SECRET':
                new_lines.append(f"UPSTOX_API_SECRET={api_secret}\n")
            elif key == 'UPSTOX_REDIRECT_URI':
                new_lines.append(f"UPSTOX_REDIRECT_URI={redirect_uri}\n")
            elif key == 'PAPER_TRADING_ENABLED':
                new_lines.append(f"PAPER_TRADING_ENABLED={paper_enabled}\n")
            elif key == 'LIVE_TRADING_ENABLED':
                new_lines.append(f"LIVE_TRADING_ENABLED={live_enabled}\n")
            elif key == 'SELECTED_INDICES':
                new_lines.append(f"SELECTED_INDICES={selected_indices_str}\n")
            elif key == 'MONEYNESS_NIFTY':
                new_lines.append(f"MONEYNESS_NIFTY={option_moneyness_nifty}\n")
            elif key == 'MONEYNESS_BANKNIFTY':
                new_lines.append(f"MONEYNESS_BANKNIFTY={option_moneyness_bn}\n")
            elif key == 'MONEYNESS_SENSEX':
                new_lines.append(f"MONEYNESS_SENSEX={option_moneyness_sensex}\n")
            elif key == 'EXPIRY_NIFTY':
                new_lines.append(f"EXPIRY_NIFTY={expiry_nifty}\n")
            elif key == 'EXPIRY_BANKNIFTY':
                new_lines.append(f"EXPIRY_BANKNIFTY={expiry_bn}\n")
            elif key == 'EXPIRY_SENSEX':
                new_lines.append(f"EXPIRY_SENSEX={expiry_sensex}\n")
            elif key == 'LOT_SIZE_NIFTY':
                new_lines.append(f"LOT_SIZE_NIFTY={lot_size_nifty}\n")
            elif key == 'LOT_SIZE_BANKNIFTY':
                new_lines.append(f"LOT_SIZE_BANKNIFTY={lot_size_banknifty}\n")
            elif key == 'LOT_SIZE_SENSEX':
                new_lines.append(f"LOT_SIZE_SENSEX={lot_size_sensex}\n")
        
    with open(env_path, "w") as f:
        f.writelines(new_lines)
        
    logger.info("Settings updated via Web UI")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # Start Scheduler in Background Thread
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    
    # Start Flask Server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
