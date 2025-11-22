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
# Allow CORS for mobile app
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global reference to trading engine
trading_engine = None

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
