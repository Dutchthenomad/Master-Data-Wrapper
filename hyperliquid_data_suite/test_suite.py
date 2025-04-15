#!/usr/bin/env python3
"""
Test script for Hyperliquid Data Collection Suite

This script verifies the functionality of the suite after installation,
testing all major components to ensure they work correctly together.
"""

import time
from hyperliquid_data_suite.clients.hyperliquid_client import HyperliquidClient
from hyperliquid_data_suite.fetchers.market_data import fetch_market_data
from hyperliquid_data_suite.utils.hyperliquid_helpers import (
    ask_bid, get_sz_px_decimals, get_ohlcv2, 
    calculate_bollinger_bands, calculate_vwap_with_symbol,
    supply_demand_zones_hl
)

def test_client():
    """Test the HyperliquidClient functionality"""
    print("\n=== Testing HyperliquidClient ===")
    client = HyperliquidClient()
    
    # Test market stats
    print("\nTesting get_market_stats()...")
    btc_stats = client.get_market_stats("BTC")
    print(f"BTC Market Stats: {btc_stats.get('mark', 'N/A')}")
    
    # Test all markets
    print("\nTesting get_all_markets()...")
    markets = client.get_all_markets()
    print(f"Retrieved {len(markets)} markets")
    if markets:
        print(f"Sample prices: BTC=${markets.get('BTC', 'N/A')}, ETH=${markets.get('ETH', 'N/A')}")
    
    # Test exchange metadata
    print("\nTesting get_exchange_meta()...")
    meta = client.get_exchange_meta()
    universe = meta.get("universe", [])
    print(f"Exchange has {len(universe)} assets")
    
    # Test order book
    print("\nTesting get_order_book()...")
    order_book = client.get_order_book("BTC")
    print(f"Order book has {len(order_book.get('bids', []))} bids and {len(order_book.get('asks', []))} asks")
    if order_book.get('bids'):
        print(f"Top bid: ${order_book['bids'][0]['price']} for {order_book['bids'][0]['size']} BTC")
    if order_book.get('asks'):
        print(f"Top ask: ${order_book['asks'][0]['price']} for {order_book['asks'][0]['size']} BTC")
    
    # Test recent trades
    print("\nTesting get_recent_trades()...")
    trades = client.get_recent_trades("BTC", limit=5)
    print(f"Retrieved {len(trades)} recent trades")
    if trades:
        print("Recent trades:")
        for trade in trades[:3]:  # Show first 3 trades
            print(f"  {trade['side'].upper()} {trade['size']} BTC @ ${trade['price']}")
    
    # Test candle data
    print("\nTesting get_candle_data()...")
    candles = client.get_candle_data("BTC", "1h", lookback_days=1)
    print(f"Retrieved {len(candles)} hourly candles")
    
    # Test funding rate
    print("\nTesting get_funding_rate()...")
    funding_rate = client.get_funding_rate("BTC")
    print(f"BTC funding rate: {funding_rate}%")
    
    # Test open interest
    print("\nTesting get_open_interest()...")
    open_interest = client.get_open_interest("BTC")
    print(f"BTC open interest: {open_interest}")

def test_fetchers():
    """Test the fetchers module"""
    print("\n=== Testing Fetchers ===")
    
    # Test market data fetcher
    print("\nTesting fetch_market_data()...")
    symbols = ["BTC", "ETH", "SOL"]
    data = fetch_market_data(symbols)
    print(f"Fetched data for {len(data)} symbols")
    for item in data:
        print(f"- {item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']} | Trend: {item['trend']}")

def test_helpers():
    """Test the helper functions"""
    print("\n=== Testing Helper Functions ===")
    
    # Test ask_bid
    print("\nTesting ask_bid()...")
    symbol = "BTC"
    ask, bid, l2_data = ask_bid(symbol)
    print(f"{symbol} Ask: {ask}, Bid: {bid}")
    
    # Test get_sz_px_decimals
    print("\nTesting get_sz_px_decimals()...")
    sz_dec, px_dec = get_sz_px_decimals(symbol)
    print(f"{symbol} Size Decimals: {sz_dec}, Price Decimals: {px_dec}")
    
    # Test get_ohlcv2
    print("\nTesting get_ohlcv2()...")
    ohlcv_df = get_ohlcv2(symbol, "1h", 1)
    if not ohlcv_df.empty:
        print(f"OHLCV Data for {symbol}:")
        print(ohlcv_df.head())
        
        # Test Bollinger Bands
        print("\nTesting calculate_bollinger_bands()...")
        df_with_bb, tight, wide = calculate_bollinger_bands(ohlcv_df)
        print(f"Bollinger Bands - Tight: {tight}, Wide: {wide}")
        
        # Test VWAP
        print("\nTesting calculate_vwap_with_symbol()...")
        vwap = calculate_vwap_with_symbol(symbol)
        print(f"VWAP for {symbol}: {vwap}")
        
        # Test Supply/Demand Zones
        print("\nTesting supply_demand_zones_hl()...")
        zones = supply_demand_zones_hl(symbol, "1h", 100)
        print(f"Supply Zones: {len(zones['supply_zones'])}")
        print(f"Demand Zones: {len(zones['demand_zones'])}")
    else:
        print(f"Failed to fetch OHLCV data for {symbol}")

def run_all_tests():
    """Run all test functions and handle exceptions"""
    tests = [
        ("Client Tests", test_client),
        ("Fetcher Tests", test_fetchers),
        ("Helper Function Tests", test_helpers)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"Running {test_name}")
        print(f"{'=' * 50}")
        try:
            start_time = time.time()
            test_func()
            end_time = time.time()
            duration = end_time - start_time
            results.append((test_name, "PASSED", f"{duration:.2f}s"))
        except Exception as e:
            results.append((test_name, "FAILED", str(e)))
            print(f"Error in {test_name}: {e}")
    
    # Print summary
    print(f"\n{'=' * 50}")
    print("Test Summary")
    print(f"{'=' * 50}")
    for name, status, info in results:
        print(f"{name}: {status} ({info})")

if __name__ == "__main__":
    print("=== Hyperliquid Data Collection Suite Test ===")
    print("Testing all components to ensure they work correctly together.")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_total = time.time()
    run_all_tests()
    end_total = time.time()
    
    print(f"\nTotal test duration: {end_total - start_total:.2f} seconds")
    print("Test completed.")
