#!/usr/bin/env python3
"""
Simple test script for Hyperliquid Data Collection Suite

This script tests the core functionality of the HyperliquidClient
to ensure it can connect to the API and retrieve basic data.
"""

import time
from hyperliquid_data_suite.clients.hyperliquid_client import HyperliquidClient

def test_basic_functionality():
    """Test basic functionality of the HyperliquidClient"""
    print("\n=== Testing Basic HyperliquidClient Functionality ===")
    
    try:
        # Initialize client
        print("Initializing HyperliquidClient...")
        client = HyperliquidClient()
        print(f"Client initialized with base URL: {client.base_url}")
        
        # Test getting all markets
        print("\nFetching all markets...")
        markets = client.get_all_markets()
        print(f"Retrieved {len(markets)} markets")
        if markets:
            print(f"Sample prices: BTC=${markets.get('BTC', 'N/A')}, ETH=${markets.get('ETH', 'N/A')}")
        
        # Test getting order book for BTC
        print("\nFetching BTC order book...")
        order_book = client.get_order_book("BTC")
        print(f"Order book has {len(order_book.get('bids', []))} bids and {len(order_book.get('asks', []))} asks")
        
        print("\nBasic functionality test completed successfully!")
        return True
    except Exception as e:
        print(f"\nError during basic functionality test: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple Hyperliquid Data Collection Suite Test ===")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    success = test_basic_functionality()
    end_time = time.time()
    
    print(f"\nTest duration: {end_time - start_time:.2f} seconds")
    print(f"Test result: {'SUCCESS' if success else 'FAILURE'}")
