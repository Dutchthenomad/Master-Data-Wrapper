"""
Enhanced data fetcher for Hyperliquid with improved error handling and timestamp correction.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import os
import logging
from typing import Dict, List, Optional
from master_data_collection.config.settings import get_data_path

logger = logging.getLogger(__name__)

class EnhancedHyperliquidFetcher:
    """Enhanced fetcher for Hyperliquid data with timestamp correction and robust error handling."""
    
    def __init__(self, max_retries: int = 3, batch_size: int = 5000):
        """Initialize the fetcher with default settings.
        
        Args:
            max_retries: Maximum number of retry attempts for API calls
            batch_size: Number of candles to fetch per request (max 5000 for Hyperliquid)
        """
        self.timestamp_offset = None
        self.max_retries = max_retries
        self.batch_size = min(batch_size, 5000)  # Ensure we don't exceed Hyperliquid's limit
        self.api_url = 'https://api.hyperliquid.xyz/info'
        logger.info(f"Enhanced Hyperliquid Fetcher initialized with batch_size={self.batch_size}, max_retries={self.max_retries}")
    
    def adjust_timestamp(self, dt: datetime) -> datetime:
        """Adjust API timestamps by subtracting the timestamp offset.
        
        Args:
            dt: Datetime to adjust
            
        Returns:
            Adjusted datetime
        """
        if self.timestamp_offset is not None:
            corrected_dt = dt - self.timestamp_offset
            return corrected_dt
        return dt
    
    def get_ohlcv(self, symbol: str, interval: str, start_time: datetime, 
                 end_time: datetime, batch_size: Optional[int] = None) -> List[Dict]:
        """Fetch OHLCV data from Hyperliquid with timestamp correction.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            interval: Timeframe interval (e.g., '15m', '1h')
            start_time: Start time for data fetch
            end_time: End time for data fetch
            batch_size: Number of candles to fetch (max 5000)
            
        Returns:
            List of candle data dictionaries from Hyperliquid API
        """
        batch_size = batch_size or self.batch_size
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)
        
        logger.info(f"Requesting data for {symbol} ({interval}) from {start_time} to {end_time}")
        logger.info(f"Batch size: {batch_size}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers={'Content-Type': 'application/json'},
                    json={
                        "type": "candleSnapshot",
                        "req": {
                            "coin": symbol,
                            "interval": interval,
                            "startTime": start_ts,
                            "endTime": end_ts,
                            "limit": batch_size
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    snapshot_data = response.json()
                    
                    if snapshot_data:
                        # Calculate timestamp offset if not already done
                        if self.timestamp_offset is None:
                            latest_api_timestamp = datetime.utcfromtimestamp(snapshot_data[-1]['t'] / 1000)
                            system_current_date = datetime.utcnow()
                            # Calculate offset (API time - system time)
                            self.timestamp_offset = latest_api_timestamp - system_current_date
                            logger.info(f"Calculated timestamp offset: {self.timestamp_offset}")
                        
                        # Adjust timestamps
                        for candle in snapshot_data:
                            dt = datetime.utcfromtimestamp(candle['t'] / 1000)
                            adjusted_dt = self.adjust_timestamp(dt)
                            candle['t'] = int(adjusted_dt.timestamp() * 1000)
                        
                        first_time = datetime.utcfromtimestamp(snapshot_data[0]['t'] / 1000)
                        last_time = datetime.utcfromtimestamp(snapshot_data[-1]['t'] / 1000)
                        
                        logger.info(f"Received {len(snapshot_data)} candles")
                        logger.info(f"First candle: {first_time}")
                        logger.info(f"Last candle: {last_time}")
                        
                        return snapshot_data
                    else:
                        logger.warning("No data returned by API")
                        return []
                else:
                    logger.warning(f"HTTP Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                
            # Wait before retrying
            if attempt < self.max_retries - 1:
                wait_time = 1 * (attempt + 1)  # Exponential backoff
                logger.info(f"Waiting {wait_time}s before retry {attempt + 2}")
                time.sleep(wait_time)
        
        logger.error(f"Failed to fetch data after {self.max_retries} attempts")
        return []
    
    def process_data_to_df(self, snapshot_data: List[Dict]) -> pd.DataFrame:
        """Convert raw API data to a pandas DataFrame.
        
        Args:
            snapshot_data: Raw candle data from Hyperliquid API
            
        Returns:
            DataFrame with OHLCV data
        """
        if not snapshot_data:
            logger.warning("No data to process")
            return pd.DataFrame()
            
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        data = []
        
        for snapshot in snapshot_data:
            timestamp = datetime.utcfromtimestamp(snapshot['t'] / 1000)
            open_price = snapshot['o']
            high_price = snapshot['h']
            low_price = snapshot['l']
            close_price = snapshot['c']
            volume = snapshot['v']
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])
        
        df = pd.DataFrame(data, columns=columns)
        return df
    
    def fetch_historical_data(self, symbol: str, timeframe: str, days_back: int = 30, 
                             save_csv: bool = True, output_dir: Optional[str] = None) -> pd.DataFrame:
        """Fetch historical data for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            timeframe: Timeframe interval (e.g., '15m', '1h')
            days_back: Number of days to look back
            save_csv: Whether to save the data to a CSV file
            output_dir: Directory to save CSV files (default: centralized MARKET_DATA_DIR)
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching historical data for {symbol} ({timeframe}) for the past {days_back} days")
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        logger.info(f"Time range: {start_time} to {end_time}")
        
        # Fetch the data
        data = self.get_ohlcv(symbol, timeframe, start_time, end_time, batch_size=self.batch_size)
        
        if not data:
            logger.warning("No data available")
            return pd.DataFrame()
        
        # Process the data
        df = self.process_data_to_df(data)
        
        if df.empty:
            logger.warning("Processed DataFrame is empty")
            return df
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        df = df.reset_index(drop=True)
        
        logger.info("Final data summary:")
        logger.info(f"Total candles: {len(df)}")
        logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Save to CSV if requested
        if save_csv:
            if output_dir is None:
                # Use the centralized market data directory
                output_dir = get_data_path('market', symbol, timeframe)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Create a standardized filename with start and end dates
            start_date = start_time.strftime('%Y%m%d')
            end_date = end_time.strftime('%Y%m%d')
            file_path = os.path.join(output_dir, f'{symbol.lower()}_{timeframe}_{start_date}_to_{end_date}.csv')
            
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")
        
        return df
    
    def fetch_latest_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Fetch the most recent candles for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            timeframe: Timeframe interval (e.g., '15m', '1h')
            limit: Number of candles to fetch (max 5000)
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching latest {limit} candles for {symbol} ({timeframe})")
        
        end_time = datetime.utcnow()
        # Set a wide enough start time to ensure we get at least 'limit' candles
        start_time = end_time - timedelta(days=30)  
        
        # Fetch the data
        data = self.get_ohlcv(symbol, timeframe, start_time, end_time, batch_size=limit)
        
        if not data:
            logger.warning("No data available")
            return pd.DataFrame()
        
        # Process the data
        df = self.process_data_to_df(data)
        
        if df.empty:
            logger.warning("Processed DataFrame is empty")
            return df
        
        # Sort by timestamp and take the most recent 'limit' candles
        df = df.sort_values('timestamp', ascending=False).head(limit).sort_values('timestamp')
        df = df.reset_index(drop=True)
        
        logger.info(f"Fetched {len(df)} latest candles")
        
        return df
