#!/usr/bin/env python3
"""
Test script for hourly data persistence functionality
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data.hourly_persistence import save_redis_data_to_postgres, hourly_data_persistence, run_hourly_persistence
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
        logger.info("Redis connection successful")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None


def add_test_data_to_redis(redis_client):
    """Add some test data to Redis"""
    try:
        # Add some test AAPL data
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

        logger.info("Added test data to Redis")
        return True
    except Exception as e:
        logger.error(f"Failed to add test data: {e}")
        return False


def main():
    """Main test function"""
    logger.info("Starting hourly persistence test")

    # Test Redis connection
    redis_client = test_redis_connection()
    if not redis_client:
        return

    # Add test data
    if not add_test_data_to_redis(redis_client):
        return

    # Test the persistence function
    try:
        logger.info("Testing save_redis_data_to_postgres function...")
        save_redis_data_to_postgres()
        logger.info("Persistence test completed successfully")
    except Exception as e:
        logger.error(f"Persistence test failed: {e}")

    # Test the hourly persistence task
    try:
        logger.info("Testing hourly_data_persistence task...")
        hourly_data_persistence()
        logger.info("Hourly persistence task test completed successfully")
    except Exception as e:
        logger.error(f"Hourly persistence task test failed: {e}")

    # Test the standalone function
    try:
        logger.info("Testing run_hourly_persistence function...")
        run_hourly_persistence()
        logger.info("Standalone persistence test completed successfully")
    except Exception as e:
        logger.error(f"Standalone persistence test failed: {e}")


if __name__ == "__main__":
    main()
