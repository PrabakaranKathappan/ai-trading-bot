"""
Daily Data Cleanup for Render Free Tier
Automatically cleans up old data to prevent database from growing too large
"""

from database import Database
from logger import Logger
from datetime import datetime, timedelta
import schedule
import time

logger = Logger.get_logger('cleanup')

class DataCleanup:
    """Manages daily data cleanup to keep database small"""
    
    def __init__(self):
        self.db = Database()
    
    def cleanup_old_data(self):
        """Clean up data older than 1 day"""
        try:
            logger.info("Starting daily data cleanup...")
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Calculate cutoff time (keep only today's data)
            if self.db.is_postgres:
                # PostgreSQL - delete trades older than today
                cursor.execute('''
                    DELETE FROM trades 
                    WHERE DATE(timestamp) < CURRENT_DATE
                ''')
                deleted_trades = cursor.rowcount
                
                # Delete old signals
                cursor.execute('''
                    DELETE FROM signals 
                    WHERE DATE(timestamp) < CURRENT_DATE
                ''')
                deleted_signals = cursor.rowcount
                
                # Delete closed positions
                cursor.execute('''
                    DELETE FROM positions 
                    WHERE status = 'CLOSED' AND DATE(exit_time) < CURRENT_DATE
                ''')
                deleted_positions = cursor.rowcount
                
                # Keep strategy performance data (it's cumulative and small)
                # Don't delete from strategy_performance table
                
            else:
                # SQLite - delete trades older than today
                cursor.execute('''
                    DELETE FROM trades 
                    WHERE DATE(timestamp) < DATE('now')
                ''')
                deleted_trades = cursor.rowcount
                
                # Delete old signals
                cursor.execute('''
                    DELETE FROM signals 
                    WHERE DATE(timestamp) < DATE('now')
                ''')
                deleted_signals = cursor.rowcount
                
                # Delete closed positions
                cursor.execute('''
                    DELETE FROM positions 
                    WHERE status = 'CLOSED' AND DATE(exit_time) < DATE('now')
                ''')
                deleted_positions = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Cleanup complete: Deleted {deleted_trades} trades, {deleted_signals} signals, {deleted_positions} positions")
            return True
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False
    
    def schedule_daily_cleanup(self, cleanup_time="00:05"):
        """
        Schedule daily cleanup at specified time
        Default: 00:05 AM (5 minutes after midnight)
        """
        schedule.every().day.at(cleanup_time).do(self.cleanup_old_data)
        logger.info(f"Daily cleanup scheduled for {cleanup_time}")
        
        # Run cleanup loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def run_cleanup_now():
    """Run cleanup immediately (for testing)"""
    cleanup = DataCleanup()
    cleanup.cleanup_old_data()

if __name__ == '__main__':
    # For testing: run cleanup immediately
    print("Running data cleanup...")
    run_cleanup_now()
    print("Cleanup complete!")
