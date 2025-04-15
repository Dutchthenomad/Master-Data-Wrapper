"""
Coinbase client for historical data collection.
Uses the legacy Coinbase API via CCXT.
"""

import pandas as pd
import datetime
import os
import ccxt
from math import ceil
import logging
from typing import Optional

from ..config import credentials

logger = logging.getLogger(__name__)

class CoinbaseClient:
    """Client for fetching historical data from Coinbase."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the Coinbase client with API credentials.
        
        Args:
            api_key: Coinbase API key (defaults to key in credentials module)
            api_secret: Coinbase API secret (defaults to secret in credentials module)
        """
        self.api_key = api_key or credentials.COINBASE_API_KEY
        self.api_secret = api_secret or credentials.COINBASE_API_SECRET
        self.exchange = ccxt.coinbase({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
        })
        logger.info("Coinbase client initialized")
    
    @staticmethod
    def timeframe_to_sec(timeframe: str) -> int:
        """Convert timeframe string to seconds.
        
        Args:
            timeframe: Timeframe string (e.g., '1m', '1h', '1d')
            
        Returns:
            Number of seconds in the timeframe
        """
        if 'm' in timeframe:
            return int(''.join([char for char in timeframe if char.isnumeric()])) * 60
        elif 'h' in timeframe:
            return int(''.join([char for char in timeframe if char.isnumeric()])) * 60 * 60
        elif 'd' in timeframe:
            return int(''.join([char for char in timeframe if char.isnumeric()])) * 24 * 60 * 60
        else:
            raise ValueError(f"Unsupported timeframe format: {timeframe}")
    
    def get_historical_data(self, symbol: str, timeframe: str, weeks: int = 4, 
                           cache: bool = True, output_dir: Optional[str] = None) -> pd.DataFrame:
        """Fetch historical OHLCV data from Coinbase.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '1h', '15m', '1d')
            weeks: Number of weeks of historical data to fetch
            cache: Whether to cache results to CSV
            output_dir: Directory to save CSV files (default: current directory)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Create a clean filename for the CSV
        clean_symbol = symbol.replace('/', '-')
        cache_filename = f'{clean_symbol}-{timeframe}-{weeks}wks-data.csv'
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            cache_path = os.path.join(output_dir, cache_filename)
        else:
            cache_path = cache_filename
            
        # Check if cached data exists
        if cache and os.path.exists(cache_path):
            logger.info(f"Loading cached data from {cache_path}")
            return pd.read_csv(cache_path, index_col=0, parse_dates=True)

        logger.info(f"Fetching {weeks} weeks of {timeframe} data for {symbol}")
        now = datetime.datetime.utcnow()
        
        # Calculate parameters for batched fetching
        granularity = self.timeframe_to_sec(timeframe)
        total_time = weeks * 7 * 24 * 60 * 60  # weeks to seconds
        # Coinbase API limit is 300 candles per request, but we'll use 200 to be safe
        run_times = ceil(total_time / (granularity * 200))
        
        dataframe = pd.DataFrame()
        
        for i in range(run_times):
            try:
                # Calculate the start time for this batch
                since = now - datetime.timedelta(seconds=granularity * 200 * (i + 1))
                since_timestamp = int(since.timestamp()) * 1000  # Convert to milliseconds
                
                logger.debug(f"Batch {i+1}/{run_times}: Fetching data since {since}")
                
                # Fetch the data
                data = self.exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=200)
                
                if not data:
                    logger.warning(f"No data returned for batch {i+1}")
                    continue
                    
                # Convert to DataFrame
                df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
                
                # Append to the main dataframe
                dataframe = pd.concat([df, dataframe])
                
                logger.debug(f"Batch {i+1}: Got {len(df)} candles")
                
            except Exception as e:
                logger.error(f"Error fetching batch {i+1}: {e}")
        
        if dataframe.empty:
            logger.warning("No data was fetched")
            return dataframe
            
        # Process the final dataframe
        dataframe = dataframe.drop_duplicates(subset=['datetime'])
        dataframe = dataframe.set_index('datetime')
        dataframe = dataframe.sort_index()
        dataframe = dataframe[["open", "high", "low", "close", "volume"]]
        
        # Cache the data if requested
        if cache:
            logger.info(f"Saving data to {cache_path}")
            dataframe.to_csv(cache_path)
        
        logger.info(f"Successfully fetched {len(dataframe)} candles from {dataframe.index.min()} to {dataframe.index.max()}")
        return dataframe
    
    def get_current_price(self, symbol: str) -> float:
        """Get the current price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USD')
            
        Returns:
            Current price
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return 0.0
