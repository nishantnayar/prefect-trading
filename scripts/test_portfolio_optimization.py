#!/usr/bin/env python3
"""
Test script to verify portfolio manager optimization.

This script tests the optimized PortfolioManager to ensure it:
1. Reduces API calls through caching
2. Provides the same data as before
3. Works correctly with the new get_all_portfolio_data() method
"""

import sys
import os
import time
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.sources.portfolio_manager import PortfolioManager


def test_portfolio_optimization():
    """Test the optimized portfolio manager."""
    print("🧪 Testing Portfolio Manager Optimization")
    print("=" * 50)
    
    try:
        # Initialize portfolio manager with 30-second cache
        print("📊 Initializing PortfolioManager...")
        portfolio_manager = PortfolioManager(cache_duration=30)
        
        # Test 1: First call - should make API calls
        print("\n🔄 Test 1: First data fetch (should make API calls)")
        start_time = time.time()
        all_data_1 = portfolio_manager.get_all_portfolio_data()
        first_call_time = time.time() - start_time
        
        if all_data_1:
            print(f"✅ First call successful in {first_call_time:.2f} seconds")
            print(f"   - Account ID: {all_data_1['account_info'].get('id', 'unknown')}")
            print(f"   - Portfolio Value: ${all_data_1['metrics'].get('total_value', 0):,.2f}")
            print(f"   - Total Positions: {all_data_1['total_positions']}")
            print(f"   - Pending Orders: {all_data_1['pending_orders']}")
        else:
            print("❌ First call failed")
            return False
        
        # Test 2: Second call - should use cache
        print("\n🔄 Test 2: Second data fetch (should use cache)")
        start_time = time.time()
        all_data_2 = portfolio_manager.get_all_portfolio_data()
        second_call_time = time.time() - start_time
        
        if all_data_2:
            print(f"✅ Second call successful in {second_call_time:.2f} seconds")
            print(f"   - Cache hit: {second_call_time < first_call_time}")
            print(f"   - Speed improvement: {((first_call_time - second_call_time) / first_call_time * 100):.1f}%")
        else:
            print("❌ Second call failed")
            return False
        
        # Test 3: Individual method calls - should use cache
        print("\n🔄 Test 3: Individual method calls (should use cache)")
        start_time = time.time()
        account_info = portfolio_manager.get_account_info()
        positions = portfolio_manager.get_positions()
        closed_orders = portfolio_manager.get_orders("closed")
        open_orders = portfolio_manager.get_orders("open")
        individual_call_time = time.time() - start_time
        
        print(f"✅ Individual calls successful in {individual_call_time:.2f} seconds")
        print(f"   - Account info: {len(account_info)} fields")
        print(f"   - Positions: {len(positions)} positions")
        print(f"   - Closed orders: {len(closed_orders)} orders")
        print(f"   - Open orders: {len(open_orders)} orders")
        
        # Test 4: Cache clearing
        print("\n🔄 Test 4: Cache clearing")
        portfolio_manager.clear_cache()
        print("✅ Cache cleared")
        
        # Test 5: Post-clear call - should make API calls again
        print("\n🔄 Test 5: Post-clear data fetch (should make API calls)")
        start_time = time.time()
        all_data_3 = portfolio_manager.get_all_portfolio_data()
        post_clear_time = time.time() - start_time
        
        if all_data_3:
            print(f"✅ Post-clear call successful in {post_clear_time:.2f} seconds")
            print(f"   - API calls made: {post_clear_time > second_call_time}")
        else:
            print("❌ Post-clear call failed")
            return False
        
        # Test 6: Data consistency
        print("\n🔄 Test 6: Data consistency check")
        if (all_data_1['account_info'].get('id') == all_data_2['account_info'].get('id') == 
            all_data_3['account_info'].get('id')):
            print("✅ Data consistency verified")
        else:
            print("❌ Data inconsistency detected")
            return False
        
        # Summary
        print("\n" + "=" * 50)
        print("📈 OPTIMIZATION SUMMARY")
        print("=" * 50)
        print(f"First call time: {first_call_time:.2f} seconds")
        print(f"Second call time: {second_call_time:.2f} seconds")
        print(f"Speed improvement: {((first_call_time - second_call_time) / first_call_time * 100):.1f}%")
        print(f"Cache effectiveness: {'✅ Working' if second_call_time < first_call_time else '❌ Not working'}")
        
        if second_call_time < first_call_time:
            print("\n🎉 Portfolio Manager optimization is working correctly!")
            print("   - API calls are being cached")
            print("   - Subsequent calls are faster")
            print("   - Data consistency is maintained")
            return True
        else:
            print("\n⚠️  Optimization may not be working as expected")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False


def test_backward_compatibility():
    """Test that the optimized portfolio manager maintains backward compatibility."""
    print("\n🧪 Testing Backward Compatibility")
    print("=" * 50)
    
    try:
        portfolio_manager = PortfolioManager()
        
        # Test old methods still work
        print("🔄 Testing old method: get_portfolio_summary()")
        old_summary = portfolio_manager.get_portfolio_summary()
        
        if old_summary:
            print("✅ get_portfolio_summary() works")
            print(f"   - Metrics: {len(old_summary.get('metrics', {}))} fields")
            print(f"   - Positions: {len(old_summary.get('positions', []))} positions")
            print(f"   - Recent activity: {len(old_summary.get('recent_activity', []))} activities")
        else:
            print("❌ get_portfolio_summary() failed")
            return False
        
        # Test individual methods
        print("\n🔄 Testing individual methods")
        account_info = portfolio_manager.get_account_info()
        positions = portfolio_manager.get_positions()
        orders = portfolio_manager.get_orders("closed")
        
        if account_info and positions is not None and orders is not None:
            print("✅ All individual methods work")
        else:
            print("❌ Some individual methods failed")
            return False
        
        print("\n🎉 Backward compatibility maintained!")
        return True
        
    except Exception as e:
        print(f"\n❌ Backward compatibility test failed: {str(e)}")
        return False


def main():
    """Run all optimization tests."""
    print("🚀 Portfolio Manager Optimization Test Suite")
    print("=" * 60)
    
    # Test optimization
    optimization_success = test_portfolio_optimization()
    
    # Test backward compatibility
    compatibility_success = test_backward_compatibility()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Optimization test: {'✅ PASSED' if optimization_success else '❌ FAILED'}")
    print(f"Backward compatibility: {'✅ PASSED' if compatibility_success else '❌ FAILED'}")
    
    if optimization_success and compatibility_success:
        print("\n🎉 All tests passed! Portfolio Manager is optimized and ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 