from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from database import Database
from config import Config
from logger import Logger
from datetime import datetime
import threading
import os

logger = Logger.get_logger('dashboard')

app = Flask(__name__)
# Allow CORS for mobile app (Global)
CORS(app)

# Global reference to trading engine
trading_engine = None

from functools import wraps

# ... (existing imports)

def check_pin(f):
    """Decorator to check Access PIN"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for health and static files
        if request.endpoint in ['health_check', 'index', 'static']:
            return f(*args, **kwargs)
            
        # Get PIN from header
        pin = request.headers.get('X-Access-Pin')
        
        # Check against Config
        if not pin or pin != Config.BOT_ACCESS_PIN:
            logger.warning(f"Unauthorized access attempt. PIN provided: {pin}")
            return jsonify({'error': 'Unauthorized: Invalid Access PIN'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# Apply decorator to all /api routes
@app.before_request
def before_request():
    if request.path.startswith('/api/'):
        # Manually check PIN for API routes since before_request runs before decorators
        pin = request.headers.get('X-Access-Pin')
        if not pin or pin != Config.BOT_ACCESS_PIN:
            # Allow OPTIONS for CORS
            if request.method == 'OPTIONS':
                return
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({'error': 'Unauthorized: Invalid Access PIN'}), 401

@app.route('/api/positions/close', methods=['POST'])
def close_specific_position():
    """Close a specific position"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Missing symbol'}), 400
            
        if trading_engine:
            # Find position
            positions = trading_engine.database.get_open_positions()
            target_pos = next((p for p in positions if p['symbol'] == symbol), None)
            
            if target_pos:
                # Get current price
                quote = trading_engine.upstox.get_market_quote(symbol)
                price = quote['ltp'] if quote else target_pos['current_price']
                
                success = trading_engine.close_position(target_pos, price, 'MANUAL_CLOSE')
                if success:
                    return jsonify({'status': 'closed', 'message': f'Position {symbol} closed'})
                else:
                    return jsonify({'error': 'Failed to close position'}), 500
            else:
                return jsonify({'error': 'Position not found'}), 404
        else:
            return jsonify({'error': 'Trading engine not initialized'}), 500
            
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        return jsonify({'error': str(e)}), 500

# ... (existing routes)

def set_trading_engine(engine):
    """Set reference to trading engine"""
    global trading_engine
    trading_engine = engine

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and keep-alive"""
    try:
        # Check if trading engine is running
        status = 'healthy'
        if trading_engine:
            status = 'running' if trading_engine.is_running else 'paused'
        
        return jsonify({
            'status': status,
            'mode': Config.TRADING_MODE,
            'environment': 'cloud' if os.environ.get('DATABASE_URL') else 'local',
            'timestamp': str(datetime.now())
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    try:
        db = Database()
        
        # Get open positions
        positions = db.get_open_positions()
        
        # Get today's trades
        trades = db.get_today_trades()
        
        # Get today's P&L
        today_pnl = db.get_today_pnl()
        
        # Get performance stats
        stats = db.get_performance_stats(days=30)
        
        # Get risk metrics
        if trading_engine:
            risk_metrics = trading_engine.risk_manager.get_risk_metrics()
        else:
            risk_metrics = {}
        
        return jsonify({
            'status': 'running' if trading_engine and trading_engine.is_running else 'stopped',
            'mode': Config.TRADING_MODE,
            'positions': positions,
            'trades': trades,
            'today_pnl': today_pnl,
            'stats': stats,
            'risk_metrics': risk_metrics,
            'capital': Config.CAPITAL
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def get_positions():
    """Get all open positions"""
    try:
        db = Database()
        positions = db.get_open_positions()
        return jsonify({'positions': positions})
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    try:
        db = Database()
        trades = db.get_today_trades()
        return jsonify({'trades': trades})
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    try:
        db = Database()
        days = request.args.get('days', 30, type=int)
        stats = db.get_performance_stats(days=days)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy-performance')
def get_strategy_performance():
    """Get performance stats for all strategies"""
    try:
        db = Database()
        strategies = db.get_strategy_performance()
        return jsonify({'strategies': strategies})
    except Exception as e:
        logger.error(f"Error getting strategy performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/control/pause', methods=['POST'])
def pause_trading():
    """Pause trading"""
    try:
        if trading_engine:
            trading_engine.is_running = False
            logger.info("Trading paused via dashboard")
            return jsonify({'status': 'paused'})
        return jsonify({'error': 'Trading engine not initialized'}), 400
    except Exception as e:
        logger.error(f"Error pausing trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/control/resume', methods=['POST'])
def resume_trading():
    """Resume trading"""
    try:
        if trading_engine:
            trading_engine.is_running = True
            logger.info("Trading resumed via dashboard")
            return jsonify({'status': 'running'})
        return jsonify({'error': 'Trading engine not initialized'}), 400
    except Exception as e:
        logger.error(f"Error resuming trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/control/square-off', methods=['POST'])
def square_off():
    """Square off all positions"""
    try:
        if trading_engine:
            trading_engine.square_off_all_positions()
            logger.info("Square off initiated via dashboard")
            return jsonify({'status': 'squared_off'})
        return jsonify({'error': 'Trading engine not initialized'}), 400
    except Exception as e:
        logger.error(f"Error squaring off: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['GET'])
@check_pin
def get_strategies():
    """Get enabled strategies"""
    return jsonify(Config.ENABLED_STRATEGIES)

@app.route('/api/strategies', methods=['POST'])
@check_pin
def update_strategies():
    """Update enabled strategies"""
    try:
        data = request.json
        Config.update_strategies(data)
        logger.info(f"Strategies updated: {Config.ENABLED_STRATEGIES}")
        return jsonify({'status': 'success', 'strategies': Config.ENABLED_STRATEGIES})
    except Exception as e:
        logger.error(f"Error updating strategies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/risk', methods=['GET'])
@check_pin
def get_risk_settings():
    """Get risk settings"""
    return jsonify({
        'RISK_PER_TRADE': Config.RISK_PER_TRADE,
        'STOP_LOSS_PERCENT': Config.STOP_LOSS_PERCENT,
        'TARGET_PERCENT': Config.TARGET_PERCENT,
        'TRAILING_STOP_PERCENT': Config.TRAILING_STOP_PERCENT,
        'MAX_DAILY_LOSS': Config.MAX_DAILY_LOSS,
        'SECURE_PROFIT_ENABLED': Config.SECURE_PROFIT_ENABLED,
        'SECURE_PROFIT_AMOUNT': Config.SECURE_PROFIT_AMOUNT
    })

@app.route('/api/settings/risk', methods=['POST'])
@check_pin
def update_risk_settings():
    """Update risk settings"""
    try:
        data = request.json
        Config.update_risk_settings(data)
        logger.info(f"Risk settings updated: {data}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating risk settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure API credentials"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        
        if not api_key or not api_secret:
            return jsonify({'error': 'Missing api_key or api_secret'}), 400
            
        # Update Config
        Config.set_credentials(api_key, api_secret)
        
        # Update Trading Engine if initialized
        if trading_engine:
            success = trading_engine.update_credentials(api_key, api_secret)
            if success:
                return jsonify({'status': 'configured', 'message': 'Credentials updated and authenticated'})
            else:
                return jsonify({'error': 'Authentication failed with new credentials'}), 401
        else:
            return jsonify({'error': 'Trading engine not initialized'}), 500
            
    except Exception as e:
        logger.error(f"Error configuring credentials: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-check')
def system_check():
    """Perform comprehensive system check"""
    status = {
        'server': {'status': 'ok', 'message': 'Server is running'},
        'engine': {'status': 'error', 'message': 'Not initialized'},
        'auth': {'status': 'error', 'message': 'Not authenticated'},
        'market_data': {'status': 'error', 'message': 'Not connected'}
    }
    
    try:
        if trading_engine:
            status['engine'] = {'status': 'ok', 'message': 'Trading Engine Initialized'}
            
            # Check Auth
            if trading_engine.upstox.access_token:
                status['auth'] = {'status': 'ok', 'message': 'Authenticated'}
                
                # Check Market Data (Try to get Nifty quote)
                try:
                    quote = trading_engine.upstox.get_market_quote('NSE_INDEX|Nifty 50')
                    if quote:
                        status['market_data'] = {'status': 'ok', 'message': f"Data Live: {quote['ltp']}"}
                    else:
                        status['market_data'] = {'status': 'error', 'message': 'Failed to fetch quote'}
                except Exception as e:
                    status['market_data'] = {'status': 'error', 'message': str(e)}
            else:
                status['auth'] = {'status': 'error', 'message': 'Missing Access Token'}
        else:
            status['engine'] = {'status': 'error', 'message': 'Engine not started'}
            
        return jsonify(status)
    except Exception as e:
        logger.error(f"System check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login')
def login():
    """Redirect to Upstox login"""
    if trading_engine:
        auth_url = trading_engine.upstox.get_authorization_url()
        return jsonify({'auth_url': auth_url})
    return jsonify({'error': 'Trading engine not initialized'}), 500

@app.route('/callback')
def callback():
    """Handle Upstox callback"""
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400
        
    if trading_engine:
        if trading_engine.upstox.authenticate(code):
            return "Authentication successful! You can close this window and return to the app."
        else:
            return "Authentication failed. Please check logs."
    return "Error: Trading engine not initialized", 500

def run_dashboard(engine=None):
    """Run the dashboard server"""
    if engine:
        set_trading_engine(engine)
    
    logger.info(f"Starting dashboard on {Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    app.run(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    run_dashboard()
