"""
Keep-Alive System for Render Free Tier
Prevents service from spinning down due to inactivity
"""

import requests
import schedule
import time
import os
from logger import Logger

logger = Logger.get_logger('keepalive')

class KeepAlive:
    """Keeps Render service alive by pinging health endpoint"""
    
    def __init__(self):
        # Detect if running on Render (cloud) or locally
        self.is_cloud = bool(os.environ.get('DATABASE_URL'))
        self.service_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
        
    def ping_service(self):
        """Ping the health endpoint to keep service alive"""
        if not self.is_cloud:
            # Don't ping when running locally
            return
            
        try:
            response = requests.get(f"{self.service_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"Keep-alive ping successful: {response.json().get('status')}")
            else:
                logger.warning(f"Keep-alive ping returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
    
    def schedule_keepalive(self):
        """Schedule keep-alive pings every 10 minutes"""
        if not self.is_cloud:
            logger.info("Running locally - keep-alive disabled")
            return
            
        # Ping every 10 minutes (well before the 15-minute timeout)
        schedule.every(10).minutes.do(self.ping_service)
        logger.info("Keep-alive scheduled: pinging every 10 minutes")
        
        # Initial ping
        self.ping_service()
        
        # Run scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def start_keepalive():
    """Start keep-alive in background"""
    keepalive = KeepAlive()
    keepalive.schedule_keepalive()

if __name__ == '__main__':
    # For testing
    print("Testing keep-alive...")
    keepalive = KeepAlive()
    keepalive.ping_service()
    print("Keep-alive test complete!")
