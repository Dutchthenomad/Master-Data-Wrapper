#!/usr/bin/env python3
"""
Live Market Data Fetcher Module for Hyperliquid Data Collection Suite

A lightweight, modular component for fetching near real-time market data from Hyperliquid.
Designed to be the best-in-class example of data collection capabilities.
This module is portable for use in future projects and built for reliability.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import configuration settings
from master_data_collection.config.settings import CACHE_DURATION_SECONDS, DEFAULT_SYMBOLS, LOGGING_LEVEL

# Set up logging for debugging and monitoring
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the root directory to the path for module imports (if needed for standalone testing)
SUITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if SUITE_ROOT not in sys.path:
    sys.path.append(SUITE_ROOT)
    logger.info(f"Added {SUITE_ROOT} to sys.path for imports.")

# Import HyperliquidClient from the suite
try:
    from master_data_collection.clients.hyperliquid_client import HyperliquidClient
    CLIENT = HyperliquidClient()
    HYPERLIQUID_AVAILABLE = True
    logger.info("HyperliquidClient successfully imported.")
except ImportError as e:
    logger.error(f"Failed to import HyperliquidClient: {e}")
    HYPERLIQUID_AVAILABLE = False
    CLIENT = None

# Cache to store recent data and avoid redundant API calls
# Format: {symbol: (timestamp, data)}
DATA_CACHE = {}

# Historical price storage for change calculation
# Format: {symbol: price} - updated with each successful fetch to calculate change from last known price
HISTORICAL_PRICES = {}

def fetch_symbol_data(symbol: str, client: Any) -> Dict[str, Any]:
    """
    Fetch data for a single symbol. Used for parallel processing.
    
    Args:
        symbol (str): Cryptocurrency symbol to fetch data for.
        client: HyperliquidClient instance.
    
    Returns:
        Dict[str, Any]: Market data for the symbol.
    """
    try:
        logger.info(f"Fetching live data for {symbol}")
        stats = client.get_market_stats(symbol)
        if stats and 'price' in stats and stats.get('price', 0) > 0:
            # Calculate 24h change using last known price if available
            ref_price = HISTORICAL_PRICES.get(symbol, stats.get('price', 0))
            change = 0.0 if ref_price == 0 else ((stats.get('price', 0) - ref_price) / ref_price) * 100
            
            data = {
                "symbol": symbol,
                "price": float(stats.get('price', 0)),
                "change": round(change, 2),
                "volume": str(round(stats.get('volume_24h', 0) / 1000000, 1)) + "M",  # Volume in millions
                "trend": "up" if change > 0 else "down",
                "timestamp": datetime.now().isoformat()
            }
            # Update historical price for next change calculation
            HISTORICAL_PRICES[symbol] = float(stats.get('price', 0))
            return data
        else:
            logger.warning(f"Invalid or zero price data for {symbol}, using fallback.")
            return _get_fallback_for_symbol(symbol)
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return _get_fallback_for_symbol(symbol)

def fetch_market_data(symbols: List[str] = DEFAULT_SYMBOLS) -> List[Dict[str, Any]]:
    """
    Fetch near real-time market data for the specified symbols.
    Uses caching to prevent API overload, parallel requests for speed, and includes fallback for reliability.
    
    Args:
        symbols (List[str]): List of cryptocurrency symbols to fetch data for.
    
    Returns:
        List[Dict[str, Any]]: List of market data for each symbol.
    """
    if not HYPERLIQUID_AVAILABLE or CLIENT is None:
        logger.warning("HyperliquidClient not available. Returning fallback data.")
        return _get_fallback_data(symbols)
    
    current_time = time.time()
    result = []
    symbols_to_fetch = []
    
    # Check cache first
    for symbol in symbols:
        if symbol in DATA_CACHE:
            cache_time, cached_data = DATA_CACHE[symbol]
            if current_time - cache_time < CACHE_DURATION_SECONDS:
                logger.info(f"Using cached data for {symbol}")
                result.append(cached_data)
            else:
                symbols_to_fetch.append(symbol)
        else:
            symbols_to_fetch.append(symbol)
    
    # Fetch remaining symbols in parallel
    if symbols_to_fetch:
        logger.info(f"Fetching data for {len(symbols_to_fetch)} symbols in parallel.")
        futures = []
        with ThreadPoolExecutor(max_workers=len(symbols_to_fetch)) as executor:
            futures = [executor.submit(fetch_symbol_data, symbol, CLIENT) for symbol in symbols_to_fetch]
            for future in as_completed(futures):
                data = future.result()
                DATA_CACHE[data['symbol']] = (current_time, data)
                result.append(data)
    
    # Ensure result order matches input symbols order
    ordered_result = []
    for symbol in symbols:
        for item in result:
            if item['symbol'] == symbol:
                ordered_result.append(item)
                break
    return ordered_result

def _get_fallback_data(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Return fallback data if Hyperliquid API is unavailable.
    
    Args:
        symbols (List[str]): List of symbols to generate fallback data for.
    
    Returns:
        List[Dict[str, Any]]: Fallback market data.
    """
    fallback_base = [
        {"symbol": "BTC", "price": 83525.0, "change": 2.1, "volume": "2.3B", "trend": "up"},
        {"symbol": "ETH", "price": 3200.5, "change": -0.5, "volume": "1.1B", "trend": "down"},
        {"symbol": "SOL", "price": 145.2, "change": 4.8, "volume": "650M", "trend": "up"}
    ]
    # Map fallback data to requested symbols if possible, or use defaults
    result = []
    fallback_dict = {item['symbol']: item for item in fallback_base}
    for symbol in symbols:
        if symbol in fallback_dict:
            result.append(fallback_dict[symbol])
        else:
            result.append(_get_fallback_for_symbol(symbol))
    return result

def _get_fallback_for_symbol(symbol: str) -> Dict[str, Any]:
    """
    Generate fallback data for a single symbol.
    
    Args:
        symbol (str): Symbol to generate fallback data for.
    
    Returns:
        Dict[str, Any]: Fallback data for the symbol.
    """
    return {
        "symbol": symbol,
        "price": 0.0,
        "change": 0.0,
        "volume": "N/A",
        "trend": "down",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    """Test the market data fetcher independently."""
    print("Testing Live Market Data Fetcher...")
    start = time.time()
    data = fetch_market_data(DEFAULT_SYMBOLS)
    end = time.time()
    print(f"Fetch took {end - start:.2f} seconds.")
    print("Fetched Market Data:")
    for item in data:
        print(f"- {item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']} | Trend: {item['trend']}")
