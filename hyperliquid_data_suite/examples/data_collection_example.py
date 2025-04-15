#!/usr/bin/env python3
"""
Hyperliquid Data Collection Suite Example

This example demonstrates how to use the enhanced data collection capabilities
of the Hyperliquid Data Collection Suite, including both Hyperliquid and Coinbase
data sources with cross-validation.
"""

import os
import sys
import matplotlib.pyplot as plt
import logging

# Add the parent directory to the path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the data integration module
from hyperliquid_data_suite.fetchers.data_integration import DataIntegration
from hyperliquid_data_suite.clients.hyperliquid_client import HyperliquidClient
from hyperliquid_data_suite.clients.coinbase_client import CoinbaseClient
from hyperliquid_data_suite.fetchers.enhanced_hyperliquid_fetcher import EnhancedHyperliquidFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_data_integration():
    """Demonstrate the data integration capabilities."""
    print("\n=== Data Integration Example ===")
    
    # Initialize the data integration module
    data = DataIntegration(use_coinbase=True, use_hyperliquid=True)
    
    # Fetch historical data with cross-validation
    symbol = 'BTC'
    timeframe = '1h'
    days = 7
    
    print(f"\nFetching {days} days of {timeframe} data for {symbol} with cross-validation...")
    df = data.get_historical_data(symbol, timeframe, days=days, validate=True)
    
    if not df.empty:
        print(f"Successfully fetched {len(df)} candles")
        print(f"Date range: {df.index.min()} to {df.index.max()}")
        print("\nSample data:")
        print(df.head())
    else:
        print("Failed to fetch data")
    
    # Get current price from multiple sources
    print("\nGetting current price from multiple sources:")
    hl_price = data.get_current_price(symbol, prefer='hyperliquid')
    cb_price = data.get_current_price(symbol, prefer='coinbase')
    
    print(f"Hyperliquid price for {symbol}: ${hl_price}")
    print(f"Coinbase price for {symbol}: ${cb_price}")
    print(f"Price difference: {abs(hl_price - cb_price) / hl_price * 100:.2f}%")
    
    return df

def example_long_term_historical():
    """Demonstrate fetching long-term historical data from Coinbase."""
    print("\n=== Long-Term Historical Data Example ===")
    
    # Initialize the Coinbase client directly
    coinbase = CoinbaseClient()
    
    # Fetch 52 weeks (1 year) of data
    symbol = 'BTC/USD'
    timeframe = '1d'
    weeks = 52
    
    print(f"\nFetching {weeks} weeks of {timeframe} data for {symbol} from Coinbase...")
    df = coinbase.get_historical_data(symbol, timeframe, weeks=weeks)
    
    if not df.empty:
        print(f"Successfully fetched {len(df)} daily candles")
        print(f"Date range: {df.index.min()} to {df.index.max()}")
        print("\nSample data:")
        print(df.head())
        
        # Plot the closing prices
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['close'])
        plt.title(f"{symbol} Price - Past {weeks} Weeks")
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot
        plot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'btc_yearly.png')
        plt.savefig(plot_path)
        print(f"\nPlot saved to {plot_path}")
    else:
        print("Failed to fetch data")
    
    return df

def example_enhanced_hyperliquid():
    """Demonstrate the enhanced Hyperliquid fetcher capabilities."""
    print("\n=== Enhanced Hyperliquid Fetcher Example ===")
    
    # Initialize the enhanced Hyperliquid fetcher
    fetcher = EnhancedHyperliquidFetcher()
    
    # Fetch data for multiple symbols
    symbols = ['BTC', 'ETH', 'SOL']
    timeframe = '15m'
    days = 2
    
    results = {}
    
    for symbol in symbols:
        print(f"\nFetching {days} days of {timeframe} data for {symbol}...")
        df = fetcher.fetch_historical_data(symbol, timeframe, days_back=days, save_csv=False)
        
        if not df.empty:
            print(f"Successfully fetched {len(df)} candles for {symbol}")
            print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            results[symbol] = df
        else:
            print(f"Failed to fetch data for {symbol}")
    
    # Compare volumes
    if len(results) > 1:
        print("\nComparing trading volumes:")
        for symbol, df in results.items():
            total_volume = df['volume'].sum()
            print(f"{symbol}: {total_volume:,.2f}")
    
    return results

def example_hyperliquid_client():
    """Demonstrate the standard Hyperliquid client capabilities."""
    print("\n=== Hyperliquid Client Example ===")
    
    # Initialize the Hyperliquid client
    client = HyperliquidClient()
    
    # Get market stats
    print("\nGetting market stats...")
    stats = client.get_market_stats()
    
    if stats:
        print(f"Successfully fetched stats for {len(stats)} markets")
        print("\nTop markets by 24h volume:")
        
        # Sort by 24h volume
        sorted_stats = sorted(stats, key=lambda x: float(x.get('dailyVolume', 0)), reverse=True)
        
        for i, market in enumerate(sorted_stats[:5], 1):
            print(f"{i}. {market.get('name', 'Unknown')}: ${float(market.get('dailyVolume', 0)):,.2f}")
    else:
        print("Failed to fetch market stats")
    
    # Get order book for BTC
    print("\nGetting BTC order book...")
    order_book = client.get_order_book('BTC')
    
    if order_book and 'bids' in order_book and 'asks' in order_book:
        print(f"Order book depth: {len(order_book['bids'])} bids, {len(order_book['asks'])} asks")
        
        if order_book['bids']:
            print(f"Top bid: ${order_book['bids'][0]['px']} ({order_book['bids'][0]['sz']} contracts)")
        
        if order_book['asks']:
            print(f"Top ask: ${order_book['asks'][0]['px']} ({order_book['asks'][0]['sz']} contracts)")
    else:
        print("Failed to fetch order book")
    
    return stats

def main():
    """Run all examples."""
    print("\n===== Hyperliquid Data Collection Suite Examples =====\n")
    print("This script demonstrates the enhanced data collection capabilities")
    print("of the Hyperliquid Data Collection Suite, including both Hyperliquid")
    print("and Coinbase data sources.")
    
    # Run examples
    try:
        # Run examples and store results for potential future use
        example_data_integration()
        example_long_term_historical()
        example_enhanced_hyperliquid()
        example_hyperliquid_client()
        
        print("\n===== All Examples Completed Successfully =====\n")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
