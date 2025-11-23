"""
Migration script to add strategy performance tracking to the database.
Run this script once to add the necessary columns and tables.
"""

import sqlite3
import os
from logger import Logger

logger = Logger.get_logger('migration')

def migrate_database():
    """Add strategy performance tracking to existing database"""
    db_path = 'trading_bot.db'
    
    if not os.path.exists(db_path):
        logger.info("Database doesn't exist yet, will be created with new schema")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(trades)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add strategy_name column if it doesn't exist
        if 'strategy_name' not in columns:
            logger.info("Adding strategy_name column to trades table...")
            cursor.execute('ALTER TABLE trades ADD COLUMN strategy_name TEXT')
            logger.info("✓ Added strategy_name column")
        else:
            logger.info("strategy_name column already exists")
        
        # Add strategy_signal_strength column if it doesn't exist
        if 'strategy_signal_strength' not in columns:
            logger.info("Adding strategy_signal_strength column to trades table...")
            cursor.execute('ALTER TABLE trades ADD COLUMN strategy_signal_strength INTEGER')
            logger.info("✓ Added strategy_signal_strength column")
        else:
            logger.info("strategy_signal_strength column already exists")
        
        # Create strategy_performance table
        logger.info("Creating strategy_performance table...")
        cursor.execute('''\r
            CREATE TABLE IF NOT EXISTS strategy_performance (\r
                id INTEGER PRIMARY KEY AUTOINCREMENT,\r
                strategy_name TEXT UNIQUE,\r
                total_trades INTEGER DEFAULT 0,\r
                winning_trades INTEGER DEFAULT 0,\r
                losing_trades INTEGER DEFAULT 0,\r
                total_pnl REAL DEFAULT 0,\r
                win_rate REAL DEFAULT 0,\r
                avg_pnl REAL DEFAULT 0,\r
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP\r
            )\r
        ''')
        logger.info("✓ Created strategy_performance table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Strategy Performance Tracking - Database Migration")
    print("=" * 60)
    print()
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\nThe following changes were made:")
        print("  • Added 'strategy_name' column to trades table")
        print("  • Added 'strategy_signal_strength' column to trades table")
        print("  • Created 'strategy_performance' table")
        print("\nYou can now run the trading bot with strategy performance tracking!")
    else:
        print("\n❌ Migration failed. Please check the logs.")
