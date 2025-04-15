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
import pandas as pd
import time

# Add the parent directory to the path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the data integration module
from master_data_collection.fetchers.data_integration import DataIntegration
from master_data_collection.clients.hyperliquid_client import HyperliquidClient
from master_data_collection.clients.coinbase_client import CoinbaseClient
from master_data_collection.fetchers.enhanced_hyperliquid_fetcher import EnhancedHyperliquidFetcher

# Configure logging - direct all logs to file only to keep console output clean
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example_run.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w')
    ]
)

# Disable matplotlib debug logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def example_data_integration():
    """Demonstrate the data integration capabilities."""
    print("\n=== Data Integration Example ===")
    
    try:
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
        
        try:
            cb_price = data.get_current_price(symbol, prefer='coinbase')
            print(f"Hyperliquid price for {symbol}: ${hl_price}")
            print(f"Coinbase price for {symbol}: ${cb_price}")
            hl_price = float(hl_price)
            cb_price = float(cb_price)
            print(f"Price difference: {abs(hl_price - cb_price) / hl_price * 100:.2f}%")
        except Exception as error:
            print(f"Hyperliquid price for {symbol}: ${hl_price}")
            print(f"Coinbase price unavailable - check API credentials: {error}")
        
        return df
    except Exception as error:
        print(f"Error in data integration example: {error}")
        return pd.DataFrame()

def example_long_term_historical():
    """Demonstrate fetching long-term historical data from Coinbase."""
    print("\n=== Long-Term Historical Data Example ===")
    
    try:
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
    except Exception as error:
        print(f"Error in long-term historical example: {error}")
        print("Note: This example requires valid Coinbase API credentials")
        return pd.DataFrame()

def example_enhanced_hyperliquid():
    """Demonstrate the enhanced Hyperliquid fetcher capabilities."""
    print("\n=== Enhanced Hyperliquid Fetcher Example ===")
    
    try:
        # Initialize the enhanced Hyperliquid fetcher
        fetcher = EnhancedHyperliquidFetcher()
        
        # Fetch data for multiple symbols
        symbols = ['BTC', 'ETH', 'SOL']
        timeframe = '15m'
        days = 2
        
        results = {}
        
        for symbol in symbols:
            print(f"\nFetching {days} days of {timeframe} data for {symbol}...")
            # Set save_csv to True to explicitly save the data to the configured data directory
            df = fetcher.fetch_historical_data(symbol, timeframe, days_back=days, save_csv=True)
            
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
                total_volume = df['volume'].astype(float).sum()
                print(f"{symbol}: {total_volume:,.2f}")
        
        return results
    except Exception as error:
        print(f"Error in enhanced Hyperliquid example: {error}")
        return {}

def example_hyperliquid_client():
    """Demonstrate the standard Hyperliquid client capabilities."""
    print("\n=== Hyperliquid Client Example ===")
    
    try:
        # Initialize the Hyperliquid client
        client = HyperliquidClient()
        
        # Get market stats for BTC
        print("\nGetting market stats...")
        stats = client.get_market_stats('BTC')
        
        if stats:
            print("Successfully fetched market stats:")
            print("\nBTC Market Stats:")
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    print(f"{key}: {value:,.2f}")
                else:
                    print(f"{key}: {str(value)}")
        else:
            print("Failed to fetch market stats")
        
        # Get order book for BTC
        print("\nGetting BTC order book...")
        order_book = client.get_order_book('BTC')
        
        if order_book and 'bids' in order_book and 'asks' in order_book:
            print(f"Order book depth: {len(order_book['bids'])} bids, {len(order_book['asks'])} asks")
            
            if order_book['bids']:
                print(f"Top bid: ${order_book['bids'][0]['price']} ({order_book['bids'][0]['size']} contracts)")
            
            if order_book['asks']:
                print(f"Top ask: ${order_book['asks'][0]['price']} ({order_book['asks'][0]['size']} contracts)")
        else:
            print("Failed to fetch order book")
        
        return stats
    except Exception as error:
        print(f"Error in Hyperliquid client example: {error}")
        return {}

def main():
    """Run all examples."""
    print("\n===== Hyperliquid Data Collection Suite Examples =====\n")
    print("This script demonstrates the enhanced data collection capabilities")
    print("of the Hyperliquid Data Collection Suite, including both Hyperliquid")
    print("and Coinbase data sources.")
    
    # Run examples
    try:
        # Run examples and store results for potential future use
        print("\n----- Running Data Integration Example -----")
        example_data_integration()
        time.sleep(1)  # Add a small delay between examples
        
        print("\n----- Running Long-Term Historical Data Example -----")
        example_long_term_historical()
        time.sleep(1)  # Add a small delay between examples
        
        print("\n----- Running Enhanced Hyperliquid Fetcher Example -----")
        example_enhanced_hyperliquid()
        time.sleep(1)  # Add a small delay between examples
        
        print("\n----- Running Hyperliquid Client Example -----")
        example_hyperliquid_client()
        
        print("\n===== All Examples Completed Successfully =====\n")
    except Exception as error:
        print(f"\nError running examples: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
