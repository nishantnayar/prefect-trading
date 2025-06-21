#!/usr/bin/env python3
"""
Test script for standalone persistence functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data.alpaca_websocket import save_redis_data_to_postgres
import redis
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_redis_connection():
    """Test Redis connection"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis connection successful")
        return redis_client
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return None

def add_test_data_to_redis(redis_client):
    """Add test AAPL data to Redis"""
    try:
        # Add test AAPL data
        test_data = {
            "open": "150.00",
            "high": "152.50", 
            "low": "149.75",
            "close": "151.25",
            "volume": "1000000",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        redis_key = "AAPL:2024-01-15T10:30:00Z"
        redis_client.hset(name=redis_key, mapping=test_data)
        
        # Add another test record
        test_data2 = {
            "open": "151.25",
            "high": "153.00",
            "low": "150.50", 
            "close": "152.75",
            "volume": "1200000",
            "timestamp": "2024-01-15T11:30:00Z"
        }
        
        redis_key2 = "AAPL:2024-01-15T11:30:00Z"
        redis_client.hset(name=redis_key2, mapping=test_data2)
        
        logger.info("✅ Added test AAPL data to Redis")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add test data: {e}")
        return False

def check_redis_data(redis_client):
    """Check what data is in Redis"""
    try:
        keys = redis_client.keys("AAPL:*")
        logger.info(f"📊 Found {len(keys)} AAPL records in Redis:")
        for key in keys:
            data = redis_client.hgetall(key)
            logger.info(f"   {key}: {data}")
        return len(keys)
    except Exception as e:
        logger.error(f"❌ Error checking Redis data: {e}")
        return 0

def main():
    """Main test function"""
    logger.info("🚀 Starting persistence test...")
    
    # Test Redis connection
    redis_client = test_redis_connection()
    if not redis_client:
        logger.error("❌ Cannot proceed without Redis connection")
        return
    
    # Add test data
    if not add_test_data_to_redis(redis_client):
        logger.error("❌ Cannot proceed without test data")
        return
    
    # Check data before persistence
    logger.info("📋 Data in Redis BEFORE persistence:")
    count_before = check_redis_data(redis_client)
    
    # Test the persistence function
    try:
        logger.info("💾 Testing save_redis_data_to_postgres function...")
        save_redis_data_to_postgres()
        logger.info("✅ Persistence test completed successfully")
    except Exception as e:
        logger.error(f"❌ Persistence test failed: {e}")
        return
    
    # Check data after persistence
    logger.info("📋 Data in Redis AFTER persistence:")
    count_after = check_redis_data(redis_client)
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"   Records before: {count_before}")
    logger.info(f"   Records after: {count_after}")
    if count_after == 0:
        logger.info("✅ All data was successfully moved to PostgreSQL and cleaned from Redis")
    else:
        logger.warning("⚠️  Some data remains in Redis")

if __name__ == "__main__":
    main() 