#!/usr/bin/env python3
"""
Master test script for hourly persistence functionality
"""
import subprocess
import sys
import os
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test(test_name, script_path):
    """Run a test script and return success status"""
    logger.info(f"🧪 Running {test_name}...")
    logger.info("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            logger.info(f"✅ {test_name} completed successfully")
            if result.stdout:
                logger.info("📋 Output:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(f"   {line}")
            return True
        else:
            logger.error(f"❌ {test_name} failed")
            if result.stderr:
                logger.error("📋 Error output:")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        logger.error(f"   {line}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {test_name} timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ Error running {test_name}: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting comprehensive hourly persistence tests...")
    
    # Define test scripts
    tests = [
        ("Standalone Persistence Test", "src/scripts/test_persistence_standalone.py"),
        ("Data Check Test", "src/scripts/check_postgres_data.py"),
    ]
    
    # Run tests
    passed = 0
    total = len(tests)
    
    for test_name, script_path in tests:
        if os.path.exists(script_path):
            if run_test(test_name, script_path):
                passed += 1
            logger.info("")  # Empty line for readability
        else:
            logger.error(f"❌ Test script not found: {script_path}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Passed: {passed}/{total}")
    logger.info(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Hourly persistence is working correctly.")
    else:
        logger.error("⚠️  Some tests failed. Please check the errors above.")
    
    # Optional WebSocket test
    logger.info("")
    logger.info("🔌 OPTIONAL: WebSocket Test")
    logger.info("=" * 60)
    logger.info("To test the full WebSocket flow with persistence:")
    logger.info("   python src/scripts/test_websocket_short.py")
    logger.info("")
    logger.info("This will run for 2 minutes and test persistence every 30 seconds.")
    logger.info("Only run this during market hours for real data.")

if __name__ == "__main__":
    main() 