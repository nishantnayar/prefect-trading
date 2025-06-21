#!/usr/bin/env python3
"""
Script to check data saved in PostgreSQL
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.database_connectivity import DatabaseConnectivity
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgres_data():
    """Check data in PostgreSQL market_data table"""
    try:
        db = DatabaseConnectivity()
        logger.info("✅ Connected to PostgreSQL")
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM market_data WHERE symbol = 'AAPL'"
        with db.get_session() as cursor:
            cursor.execute(count_query)
            total_count = cursor.fetchone()[0]
        
        logger.info(f"📊 Total AAPL records in PostgreSQL: {total_count}")
        
        if total_count > 0:
            # Get recent records
            recent_query = """
                SELECT symbol, timestamp, open, high, low, close, volume 
                FROM market_data 
                WHERE symbol = 'AAPL' 
                ORDER BY timestamp DESC 
                LIMIT 10
            """
            
            with db.get_session() as cursor:
                cursor.execute(recent_query)
                recent_records = cursor.fetchall()
            
            logger.info("📋 Most recent 10 AAPL records:")
            for record in recent_records:
                symbol, timestamp, open_price, high, low, close_price, volume = record
                logger.info(f"   {symbol} | {timestamp} | O:{open_price} H:{high} L:{low} C:{close_price} V:{volume}")
            
            # Get data from last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_query = """
                SELECT COUNT(*) 
                FROM market_data 
                WHERE symbol = 'AAPL' AND timestamp >= %s
            """
            
            with db.get_session() as cursor:
                cursor.execute(recent_query, (one_hour_ago,))
                recent_count = cursor.fetchone()[0]
            
            logger.info(f"📈 AAPL records in the last hour: {recent_count}")
            
            # Get data by date
            today = datetime.now().date()
            today_query = """
                SELECT COUNT(*) 
                FROM market_data 
                WHERE symbol = 'AAPL' AND DATE(timestamp) = %s
            """
            
            with db.get_session() as cursor:
                cursor.execute(today_query, (today,))
                today_count = cursor.fetchone()[0]
            
            logger.info(f"📅 AAPL records today ({today}): {today_count}")
            
        else:
            logger.info("📭 No AAPL data found in PostgreSQL")
            
    except Exception as e:
        logger.error(f"❌ Error checking PostgreSQL data: {e}")
    finally:
        if 'db' in locals():
            db.close()

def check_redis_data():
    """Check data in Redis"""
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        
        keys = redis_client.keys("AAPL:*")
        logger.info(f"📊 AAPL records in Redis: {len(keys)}")
        
        if keys:
            logger.info("📋 Redis AAPL records:")
            for key in keys[:5]:  # Show first 5
                data = redis_client.hgetall(key)
                logger.info(f"   {key}: {data}")
            if len(keys) > 5:
                logger.info(f"   ... and {len(keys) - 5} more")
        
    except Exception as e:
        logger.error(f"❌ Error checking Redis data: {e}")

def main():
    """Main function"""
    logger.info("🔍 Checking data in both Redis and PostgreSQL...")
    
    logger.info("=" * 50)
    logger.info("📊 POSTGRESQL DATA")
    logger.info("=" * 50)
    check_postgres_data()
    
    logger.info("=" * 50)
    logger.info("📊 REDIS DATA")
    logger.info("=" * 50)
    check_redis_data()
    
    logger.info("=" * 50)
    logger.info("✅ Data check completed!")

if __name__ == "__main__":
    main() 