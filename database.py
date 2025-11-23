import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import Config
from logger import Logger

logger = Logger.get_logger('database')

class Database:
    """Database manager supporting both SQLite (local) and PostgreSQL (cloud)"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        self.is_postgres = self.db_url is not None
        
        if self.is_postgres:
            logger.info("Using PostgreSQL database")
            self.init_postgres()
        else:
            logger.info("Using SQLite database")
            self.db_path = Config.DB_PATH
            self.init_sqlite()
    
    def get_connection(self):
        """Get database connection"""
        if self.is_postgres:
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def init_postgres(self):
        """Initialize PostgreSQL database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol VARCHAR(50),
                    option_type VARCHAR(10),
                    strike_price DECIMAL(10, 2),
                    action VARCHAR(10),
                    quantity INTEGER,
                    entry_price DECIMAL(10, 2),
                    exit_price DECIMAL(10, 2),
                    stop_loss DECIMAL(10, 2),
                    target DECIMAL(10, 2),
                    pnl DECIMAL(10, 2),
                    status VARCHAR(20),
                    signal_strength INTEGER,
                    exit_reason VARCHAR(50)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol VARCHAR(50),
                    signal_type VARCHAR(10),
                    strength INTEGER,
                    current_price DECIMAL(10, 2),
                    rsi DECIMAL(10, 2),
                    macd DECIMAL(10, 2),
                    executed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(50),
                    option_type VARCHAR(10),
                    strike_price DECIMAL(10, 2),
                    quantity INTEGER,
                    entry_price DECIMAL(10, 2),
                    current_price DECIMAL(10, 2),
                    stop_loss DECIMAL(10, 2),
                    target DECIMAL(10, 2),
                    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'OPEN'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id SERIAL PRIMARY KEY,
                    date DATE DEFAULT CURRENT_DATE,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl DECIMAL(10, 2) DEFAULT 0,
                    win_rate DECIMAL(5, 2) DEFAULT 0
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("PostgreSQL database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL: {e}")
            raise
    
    def init_sqlite(self):
        """Initialize SQLite database (existing code)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    option_type TEXT,
                    strike_price REAL,
                    action TEXT,
                    quantity INTEGER,
                    entry_price REAL,
                    exit_price REAL,
                    stop_loss REAL,
                    target REAL,
                    pnl REAL,
                    status TEXT,
                    signal_strength INTEGER,
                    exit_reason TEXT
                )
            ''')
            
            # Signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    signal_type TEXT,
                    strength INTEGER,
                    current_price REAL,
                    rsi REAL,
                    macd REAL,
                    executed INTEGER DEFAULT 0
                )
            ''')
            
            # Positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    option_type TEXT,
                    strike_price REAL,
                    quantity INTEGER,
                    entry_price REAL,
                    current_price REAL,
                    stop_loss REAL,
                    target REAL,
                    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'OPEN'
                )
            ''')
            
            # Performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite: {e}")
            raise
    
    def add_trade(self, trade_data):
        """Add a new trade"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute('''
                    INSERT INTO trades (symbol, option_type, strike_price, action, quantity,
                                      entry_price, stop_loss, target, status, signal_strength)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    trade_data['symbol'],
                    trade_data['option_type'],
                    trade_data['strike_price'],
                    trade_data['action'],
                    trade_data['quantity'],
                    trade_data['entry_price'],
                    trade_data['stop_loss'],
                    trade_data['target'],
                    trade_data['status'],
                    trade_data.get('signal_strength', 0)
                ))
                trade_id = cursor.fetchone()[0]
            else:
                cursor.execute('''
                    INSERT INTO trades (symbol, option_type, strike_price, action, quantity,
                                      entry_price, stop_loss, target, status, signal_strength)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data['symbol'],
                    trade_data['option_type'],
                    trade_data['strike_price'],
                    trade_data['action'],
                    trade_data['quantity'],
                    trade_data['entry_price'],
                    trade_data['stop_loss'],
                    trade_data['target'],
                    trade_data['status'],
                    trade_data.get('signal_strength', 0)
                ))
                trade_id = cursor.lastrowid
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Trade added with ID: {trade_id}")
            return trade_id
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            return None
    
    def get_today_trades(self):
        """Get today's trades"""
        try:
            conn = self.get_connection()
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = CURRENT_DATE
                    ORDER BY timestamp DESC
                ''')
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = DATE('now')
                    ORDER BY timestamp DESC
                ''')
            
            trades = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not self.is_postgres:
                # Convert to dict for SQLite
                columns = [desc[0] for desc in cursor.description] if trades else []
                trades = [dict(zip(columns, trade)) for trade in trades]
            
            return trades
        except Exception as e:
            logger.error(f"Error getting today's trades: {e}")
            return []
    
    def get_open_positions(self):
        """Get all open positions"""
        try:
            conn = self.get_connection()
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute('''
                    SELECT * FROM positions 
                    WHERE status = 'OPEN'
                    ORDER BY entry_time DESC
                ''')
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM positions 
                    WHERE status = 'OPEN'
                    ORDER BY entry_time DESC
                ''')
            
            positions = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not self.is_postgres:
                columns = [desc[0] for desc in cursor.description] if positions else []
                positions = [dict(zip(columns, pos)) for pos in positions]
            
            return positions
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []
    
    def get_today_pnl(self):
        """Get today's total P&L"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute('''
                    SELECT COALESCE(SUM(pnl), 0) as total_pnl
                    FROM trades 
                    WHERE DATE(timestamp) = CURRENT_DATE AND pnl IS NOT NULL
                ''')
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(pnl), 0) as total_pnl
                    FROM trades 
                    WHERE DATE(timestamp) = DATE('now') AND pnl IS NOT NULL
                ''')
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting today's P&L: {e}")
            return 0
    
    def get_performance_stats(self, days=30):
        """Get performance statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                        AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                        AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss,
                        SUM(pnl) as total_pnl
                    FROM trades 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '%s days'
                    AND pnl IS NOT NULL
                ''', (days,))
            else:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                        AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                        AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss,
                        SUM(pnl) as total_pnl
                    FROM trades 
                    WHERE timestamp >= DATE('now', '-' || ? || ' days')
                    AND pnl IS NOT NULL
                ''', (days,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0] > 0:
                total, winning, losing, avg_win, avg_loss, total_pnl = result
                win_rate = (winning / total * 100) if total > 0 else 0
                
                return {
                    'total_trades': total or 0,
                    'winning_trades': winning or 0,
                    'losing_trades': losing or 0,
                    'win_rate': round(win_rate, 2),
                    'avg_win': round(avg_win or 0, 2),
                    'avg_loss': round(avg_loss or 0, 2),
                    'total_pnl': round(total_pnl or 0, 2)
                }
            
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'total_pnl': 0
            }
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    def update_strategy_performance(self, strategy_name, pnl):
        """Update strategy performance stats"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute('''
                    SELECT total_trades, winning_trades, losing_trades, total_pnl
                    FROM strategy_performance WHERE strategy_name = %s
                ''', (strategy_name,))
            else:
                cursor.execute('''
                    SELECT total_trades, winning_trades, losing_trades, total_pnl
                    FROM strategy_performance WHERE strategy_name = ?
                ''', (strategy_name,))
            
            result = cursor.fetchone()
            
            if result:
                total_trades, winning, losing, total_pnl = result
                total_trades += 1
                if pnl > 0:
                    winning += 1
                elif pnl < 0:
                    losing += 1
                total_pnl += pnl
                win_rate = (winning / total_trades * 100) if total_trades > 0 else 0
                avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
                
                if self.is_postgres:
                    cursor.execute('''
                        UPDATE strategy_performance
                        SET total_trades = %s, winning_trades = %s, losing_trades = %s,
                            total_pnl = %s, win_rate = %s, avg_pnl = %s
                        WHERE strategy_name = %s
                    ''', (total_trades, winning, losing, total_pnl, win_rate, avg_pnl, strategy_name))
                else:
                    cursor.execute('''
                        UPDATE strategy_performance
                        SET total_trades = ?, winning_trades = ?, losing_trades = ?,
                            total_pnl = ?, win_rate = ?, avg_pnl = ?
                        WHERE strategy_name = ?
                    ''', (total_trades, winning, losing, total_pnl, win_rate, avg_pnl, strategy_name))
            else:
                winning = 1 if pnl > 0 else 0
                losing = 1 if pnl < 0 else 0
                win_rate = (winning / 1 * 100)
                
                if self.is_postgres:
                    cursor.execute('''
                        INSERT INTO strategy_performance 
                        (strategy_name, total_trades, winning_trades, losing_trades, total_pnl, win_rate, avg_pnl)
                        VALUES (%s, 1, %s, %s, %s, %s, %s)
                    ''', (strategy_name, winning, losing, pnl, win_rate, pnl))
                else:
                    cursor.execute('''
                        INSERT INTO strategy_performance 
                        (strategy_name, total_trades, winning_trades, losing_trades, total_pnl, win_rate, avg_pnl)
                        VALUES (?, 1, ?, ?, ?, ?, ?)
                    ''', (strategy_name, winning, losing, pnl, win_rate, pnl))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating strategy performance: {e}")
    
    def get_strategy_performance(self):
        """Get performance stats for all strategies"""
        try:
            conn = self.get_connection()
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute('SELECT * FROM strategy_performance ORDER BY total_pnl DESC')
            else:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM strategy_performance ORDER BY total_pnl DESC')
            
            strategies = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not self.is_postgres and strategies:
                columns = ['id', 'strategy_name', 'total_trades', 'winning_trades', 'losing_trades', 
                          'total_pnl', 'win_rate', 'avg_pnl', 'last_updated']
                strategies = [dict(zip(columns, s)) for s in strategies]
            
            return strategies
        except Exception as e:
            logger.error(f"Error getting strategy performance: {e}")
            return []
