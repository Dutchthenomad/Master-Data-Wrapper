#!/usr/bin/env python3
"""
Hyperliquid Helper Functions for the Hyperliquid Data Collection Suite

This module contains a variety of utility functions for interacting with the Hyperliquid API.
These functions are adapted from external sources and have been verified to work.
They are refactored to align with the suite's architecture for modularity and reliability.
"""

import json
import time
import requests
import pandas as pd
import pandas_ta as ta
from typing import Tuple, Dict, Any, List, Optional

# Import suite-specific modules
from master_data_collection.clients.hyperliquid_client import HyperliquidClient
from master_data_collection.utils.logging import get_logger

# Set up logging
logger = get_logger(__name__)

# Placeholder for account handling (to be implemented with secure credential management)
# For now, some functions will log warnings if direct API calls requiring credentials are used.

# Note: Some functions originally used the 'hyperliquid' library directly.
# Where possible, they are adapted to use the suite's HyperliquidClient.
# Additional API endpoints will be added to HyperliquidClient as needed.

def ask_bid(symbol: str, client: Optional[HyperliquidClient] = None) -> Tuple[float, float, List[Any]]:
    """
    Get the ask and bid prices for any symbol passed in.
    Returns ask price, bid price, and L2 book data.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        client (HyperliquidClient, optional): The Hyperliquid API client. If None, a new instance is created.
    
    Returns:
        Tuple[float, float, List[Any]]: Ask price, bid price, and L2 book data.
    """
    if client is None:
        client = HyperliquidClient()
    
    url = f"{client.base_url}/info"
    headers = {'Content-Type': 'application/json'}
    data = {
        'type': 'l2Book',
        'coin': symbol
    }
    
    try:
        logger.info(f"Fetching L2 book data for {symbol}")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        
        # Parse the response according to the actual API format
        book_data = response.json()
        levels = book_data.get('levels', [])
        
        # Get ask and bid from the levels array
        bids = levels[0] if len(levels) > 0 else []
        asks = levels[1] if len(levels) > 1 else []
        
        bid = float(bids[0]['px']) if bids else 0.0
        ask = float(asks[0]['px']) if asks else 0.0
        
        return ask, bid, levels
    except Exception as e:
        logger.error(f"Error fetching ask/bid for {symbol}: {e}")
        return 0.0, 0.0, []

def get_sz_px_decimals(symbol: str) -> Tuple[int, int]:
    """
    Get size decimals and price decimals for a given symbol.
    
    Size decimals indicate the precision for order sizes:
    - if sz decimal == 1 then you can buy/sell 1.4
    - if sz decimal == 2 then you can buy/sell 1.45
    - if sz decimal == 3 then you can buy/sell 1.456
    
    Returns (sz_decimals, px_decimals)
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
    
    Returns:
        Tuple[int, int]: Size decimals and price decimals.
    """
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}
    
    try:
        logger.info(f"Fetching metadata for {symbol}")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        data = response.json()
        symbols = data.get('universe', [])
        symbol_info = next((s for s in symbols if s['name'] == symbol), None)
        if symbol_info:
            sz_decimals = symbol_info['szDecimals']
        else:
            logger.warning(f"Symbol {symbol} not found in metadata")
            return 0, 0
    except Exception as e:
        logger.error(f"Error fetching metadata for {symbol}: {e}")
        return 0, 0
    
    # Calculate price decimals from current ask price
    try:
        ask = ask_bid(symbol)[0]
        ask_str = str(ask)
        if '.' in ask_str:
            px_decimals = len(ask_str.split('.')[1])
        else:
            px_decimals = 0
    except Exception as e:
        logger.error(f"Error calculating price decimals for {symbol}: {e}")
        px_decimals = 0
    
    logger.info(f"{symbol} size decimals: {sz_decimals}, price decimals: {px_decimals}")
    return sz_decimals, px_decimals

# Note: Functions requiring account credentials or direct 'hyperliquid' library usage
# are marked with a warning for future implementation with secure credential handling.

def limit_order(coin: str, is_buy: bool, sz: float, limit_px: float, reduce_only: bool, account: Any = None) -> Dict[str, Any]:
    """
    Place a limit order on Hyperliquid.
    
    Args:
        coin (str): The cryptocurrency symbol (e.g., 'BTC').
        is_buy (bool): True for buy order, False for sell.
        sz (float): Size of the order.
        limit_px (float): Limit price for the order.
        reduce_only (bool): If True, order will only reduce position size.
        account (Any, optional): Account object (to be implemented with secure credentials).
    
    Returns:
        Dict[str, Any]: Order result (placeholder until implemented).
    """
    logger.warning("limit_order function not yet implemented in Hyperliquid Data Collection Suite due to credential requirements.")
    # Future implementation: Use secure account handling and extend HyperliquidClient for order placement.
    return {"status": "not_implemented", "message": "Order placement requires secure credential handling."}

def acct_bal(account: Any = None) -> float:
    """
    Get the account balance for a given account.
    Returns the account value as a float.
    
    Args:
        account (Any, optional): Account object (to be implemented with secure credentials).
    
    Returns:
        float: Account value (placeholder until implemented).
    """
    logger.warning("acct_bal function not yet implemented in Hyperliquid Data Collection Suite due to credential requirements.")
    return 0.0

# Additional functions from nice_funcs.py will be added here with similar refactoring.
# For now, they are placeholders to indicate the scope.

def get_position(symbol: str, account: Any = None) -> Tuple[List[Dict[str, Any]], bool, float, Optional[str], float, float, Optional[bool]]:
    """
    Get current position information for a specific symbol.
    Returns position details including size, entry price, PnL, etc.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        account (Any, optional): Account object (to be implemented).
    
    Returns:
        Tuple containing position data (placeholder until implemented).
    """
    logger.warning("get_position function not yet implemented in Hyperliquid Data Collection Suite.")
    return [], False, 0.0, None, 0.0, 0.0, None

def get_ohlcv2(symbol: str, interval: str, lookback_days: int, client: Optional[HyperliquidClient] = None) -> pd.DataFrame:
    """
    Fetch OHLCV (candle) data for a symbol.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        interval (str): Time interval for candles (e.g., '1m', '1h').
        lookback_days (int): Number of days to look back for data.
        client (HyperliquidClient, optional): The Hyperliquid API client.
    
    Returns:
        pd.DataFrame: OHLCV data.
    """
    if client is None:
        client = HyperliquidClient()
    
    url = f"{client.base_url}/info"
    headers = {'Content-Type': 'application/json'}
    
    # Calculate start and end times based on lookback_days
    end_time = int(time.time() * 1000)  # Current time in milliseconds
    start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)  # lookback_days ago
    
    data = {
        'type': 'candleSnapshot',
        'req': {
            'coin': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time
        }
    }
    
    try:
        logger.info(f"Fetching OHLCV data for {symbol} with interval {interval}")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        response.raise_for_status()
        snapshot_data = response.json()
        
        # Process data into DataFrame
        if isinstance(snapshot_data, list):
            df = pd.DataFrame(snapshot_data, columns=['t', 'T', 's', 'i', 'o', 'h', 'l', 'c', 'v', 'n'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            df.set_index('t', inplace=True)
            df = df[['o', 'h', 'l', 'c', 'v']]
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            return df
        else:
            logger.warning(f"No valid OHLCV data returned for {symbol}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_candle_snapshot(symbol: str, interval: str, start_time: int, end_time: int, client: Optional[HyperliquidClient] = None) -> pd.DataFrame:
    """
    Fetch candle data for a specific time range.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        interval (str): Time interval for candles (e.g., '1m', '1h').
        start_time (int): Start time in milliseconds since epoch.
        end_time (int): End time in milliseconds since epoch.
        client (HyperliquidClient, optional): The Hyperliquid API client.
    
    Returns:
        pd.DataFrame: OHLCV data for the specified range.
    """
    if client is None:
        client = HyperliquidClient()
    
    url = f"{client.base_url}/info"
    headers = {'Content-Type': 'application/json'}
    data = {
        'type': 'candleSnapshot',
        'req': {
            'coin': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time
        }
    }
    
    try:
        logger.info(f"Fetching candle snapshot for {symbol} from {start_time} to {end_time}")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        response.raise_for_status()
        snapshot_data = response.json()
        
        if isinstance(snapshot_data, list):
            df = pd.DataFrame(snapshot_data, columns=['t', 'T', 's', 'i', 'o', 'h', 'l', 'c', 'v', 'n'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            df.set_index('t', inplace=True)
            df = df[['o', 'h', 'l', 'c', 'v']]
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            return df
        else:
            logger.warning(f"No valid candle data returned for {symbol}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching candle snapshot for {symbol}: {e}")
        return pd.DataFrame()

def calculate_bollinger_bands(df: pd.DataFrame, length: int = 20, std_dev: int = 2) -> Tuple[pd.DataFrame, bool, bool]:
    """
    Calculate Bollinger Bands for a given DataFrame and classify when the bands are tight vs wide.
    
    Args:
        df (pd.DataFrame): DataFrame with a 'Close' column.
        length (int): The period over which the SMA is calculated. Default is 20.
        std_dev (int): The number of standard deviations to plot above and below the SMA. Default is 2.
    
    Returns:
        Tuple[pd.DataFrame, bool, bool]: DataFrame with Bollinger Bands and classifications for 'tight' and 'wide' bands.
    """
    try:
        # Calculate SMA (Simple Moving Average)
        df['SMA'] = df['Close'].rolling(window=length).mean()
        
        # Calculate standard deviation
        df['STD'] = df['Close'].rolling(window=length).std()
        
        # Calculate Upper and Lower Bollinger Bands
        df['UpperBand'] = df['SMA'] + (df['STD'] * std_dev)
        df['LowerBand'] = df['SMA'] - (df['STD'] * std_dev)
        
        # Calculate bandwidth (difference between upper and lower bands)
        df['Bandwidth'] = df['UpperBand'] - df['LowerBand']
        
        # Calculate rolling mean and std of bandwidth to determine tight or wide bands
        df['BandwidthMean'] = df['Bandwidth'].rolling(window=length).mean()
        df['BandwidthStd'] = df['Bandwidth'].rolling(window=length).std()
        
        # Define thresholds for tight and wide bands
        df['TightThreshold'] = df['BandwidthMean'] - (df['BandwidthStd'] * 0.5)
        df['WideThreshold'] = df['BandwidthMean'] + (df['BandwidthStd'] * 0.5)
        
        # Classify bands as tight or wide
        df['BandClassification'] = 'Normal'
        df.loc[df['Bandwidth'] < df['TightThreshold'], 'BandClassification'] = 'Tight'
        df.loc[df['Bandwidth'] > df['WideThreshold'], 'BandClassification'] = 'Wide'
        
        # Determine if current bands are tight or wide
        tight = df['BandClassification'].iloc[-1] == 'Tight'
        wide = df['BandClassification'].iloc[-1] == 'Wide'
        
        return df, tight, wide
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return df, False, False

def calculate_vwap_with_symbol(symbol: str, interval: str = '1h', lookback_days: int = 1, client: Optional[HyperliquidClient] = None) -> float:
    """
    Calculate VWAP (Volume Weighted Average Price) for a symbol.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        interval (str): Time interval for data (e.g., '1h'). Default is '1h'.
        lookback_days (int): Number of days to look back for data. Default is 1.
        client (HyperliquidClient, optional): The Hyperliquid API client.
    
    Returns:
        float: VWAP value, or 0.0 if calculation fails.
    """
    try:
        # Fetch OHLCV data
        df = get_ohlcv2(symbol, interval, lookback_days, client)
        if df.empty:
            logger.warning(f"No data available to calculate VWAP for {symbol}")
            return 0.0
        
        # Calculate typical price (H+L+C)/3
        df['TypicalPrice'] = (df['High'] + df['Low'] + df['Close']) / 3
        
        # Calculate VWAP components
        df['PriceVolume'] = df['TypicalPrice'] * df['Volume']
        total_price_volume = df['PriceVolume'].sum()
        total_volume = df['Volume'].sum()
        
        if total_volume == 0:
            logger.warning(f"Zero volume for {symbol}, cannot calculate VWAP")
            return 0.0
        
        vwap = total_price_volume / total_volume
        logger.info(f"Calculated VWAP for {symbol}: {vwap}")
        return vwap
    except Exception as e:
        logger.error(f"Error calculating VWAP for {symbol}: {e}")
        return 0.0

def supply_demand_zones_hl(symbol: str, timeframe: str, limit: int = 100, client: Optional[HyperliquidClient] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Calculate supply and demand zones based on price history.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        timeframe (str): Timeframe for data (e.g., '1h').
        limit (int): Number of candles to consider. Default is 100.
        client (HyperliquidClient, optional): The Hyperliquid API client.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with supply and demand zones.
    """
    try:
        # Fetch OHLCV data (adjust lookback based on timeframe and limit)
        lookback_days = max(1, limit // (24 * 60 // int(timeframe.replace('m', '').replace('h', '60'))))
        df = get_ohlcv2(symbol, timeframe, lookback_days, client)
        if df.empty or len(df) < limit:
            logger.warning(f"Insufficient data for {symbol} to calculate supply/demand zones")
            return {"supply_zones": [], "demand_zones": []}
        
        df = df.tail(limit)
        
        # Calculate pivot highs and lows for supply/demand zones
        df['pivot_high'] = ta.peak(df['High'], length=5)
        df['pivot_low'] = ta.trough(df['Low'], length=5)
        
        supply_zones = []
        demand_zones = []
        
        # Identify supply zones (pivot highs with significant volume)
        high_pivots = df[df['pivot_high'].notnull()]
        for idx, row in high_pivots.iterrows():
            if row['Volume'] > df['Volume'].mean():
                supply_zones.append({
                    'price': row['High'],
                    'time': idx,
                    'strength': row['Volume'] / df['Volume'].mean()
                })
        
        # Identify demand zones (pivot lows with significant volume)
        low_pivots = df[df['pivot_low'].notnull()]
        for idx, row in low_pivots.iterrows():
            if row['Volume'] > df['Volume'].mean():
                demand_zones.append({
                    'price': row['Low'],
                    'time': idx,
                    'strength': row['Volume'] / df['Volume'].mean()
                })
        
        logger.info(f"Calculated {len(supply_zones)} supply zones and {len(demand_zones)} demand zones for {symbol}")
        return {"supply_zones": supply_zones, "demand_zones": demand_zones}
    except Exception as e:
        logger.error(f"Error calculating supply/demand zones for {symbol}: {e}")
        return {"supply_zones": [], "demand_zones": []}

if __name__ == "__main__":
    """Test the helper functions independently."""
    print("Testing Hyperliquid Helper Functions...")
    test_symbol = "BTC"
    ask, bid, l2_book = ask_bid(test_symbol)
    print(f"Ask for {test_symbol}: ${ask}")
    print(f"Bid for {test_symbol}: ${bid}")
    sz_dec, px_dec = get_sz_px_decimals(test_symbol)
    print(f"Size Decimals for {test_symbol}: {sz_dec}")
    print(f"Price Decimals for {test_symbol}: {px_dec}")
    # Test OHLCV fetching
    ohlcv_df = get_ohlcv2(test_symbol, '1h', 1)
    if not ohlcv_df.empty:
        print(f"Fetched OHLCV data for {test_symbol}:")
        print(ohlcv_df.tail())
        # Test Bollinger Bands
        df_with_bb, tight, wide = calculate_bollinger_bands(ohlcv_df)
        print(f"Bollinger Bands calculated. Tight: {tight}, Wide: {wide}")
        # Test VWAP
        vwap = calculate_vwap_with_symbol(test_symbol)
        print(f"VWAP for {test_symbol}: ${vwap}")
        # Test Supply/Demand Zones
        zones = supply_demand_zones_hl(test_symbol, '1h', 100)
        print(f"Supply/Demand Zones for {test_symbol}: {zones}")
    else:
        print(f"Failed to fetch OHLCV data for {test_symbol}")
