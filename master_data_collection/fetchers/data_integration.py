"""
Data Integration Module

This module provides unified access to data from multiple sources (Hyperliquid and Coinbase)
with smart fallback and cross-validation capabilities.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional
import os

from ..clients.coinbase_client import CoinbaseClient
from .enhanced_hyperliquid_fetcher import EnhancedHyperliquidFetcher
from ..config.settings import get_data_path

logger = logging.getLogger(__name__)

class DataIntegration:
    """Unified data access with multiple source integration and validation."""
    
    def __init__(self, use_coinbase: bool = True, use_hyperliquid: bool = True,
                data_dir: Optional[str] = None):
        """Initialize the data integration module.
        
        Args:
            use_coinbase: Whether to use Coinbase as a data source
            use_hyperliquid: Whether to use Hyperliquid as a data source
            data_dir: Directory to store cached data
        """
        self.use_coinbase = use_coinbase
        self.use_hyperliquid = use_hyperliquid
        
        if not (use_coinbase or use_hyperliquid):
            raise ValueError("At least one data source must be enabled")
        
        # Use the centralized data directory from settings
        self.data_dir = data_dir or get_data_path('market')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize clients
        if self.use_coinbase:
            self.coinbase = CoinbaseClient()
            logger.info("Coinbase client initialized")
        else:
            self.coinbase = None
            
        if self.use_hyperliquid:
            self.hyperliquid = EnhancedHyperliquidFetcher()
            logger.info("Hyperliquid fetcher initialized")
        else:
            self.hyperliquid = None
            
        logger.info("Data integration initialized with sources: Coinbase=%s, Hyperliquid=%s" % (use_coinbase, use_hyperliquid))
    
    def get_historical_data(self, symbol: str, timeframe: str, days: int = 30, 
                           weeks: Optional[int] = None, prefer: str = 'auto',
                           validate: bool = False) -> pd.DataFrame:
        """Get historical data with smart source selection.
        
        Args:
            symbol: Symbol to fetch (e.g., 'BTC' for Hyperliquid, 'BTC/USD' for Coinbase)
            timeframe: Timeframe (e.g., '1h', '15m')
            days: Number of days to look back (if weeks is None)
            weeks: Number of weeks to look back (overrides days if provided)
            prefer: Preferred data source ('hyperliquid', 'coinbase', or 'auto')
            validate: Whether to validate data across sources
            
        Returns:
            DataFrame with OHLCV data
        """
        # Convert symbol format if needed
        hl_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        cb_symbol = f"{symbol}/USD" if '/' not in symbol else symbol
        
        # Determine time range
        if weeks is not None:
            days = weeks * 7
        
        # Determine preferred source based on data requirements
        if prefer == 'auto':
            if days > 30:  # For long historical data, prefer Coinbase
                prefer = 'coinbase' if self.use_coinbase else 'hyperliquid'
            else:  # For shorter timeframes, prefer Hyperliquid for freshness
                prefer = 'hyperliquid' if self.use_hyperliquid else 'coinbase'
        
        logger.info("Getting %s days of %s data for %s (prefer: %s)" % (days, timeframe, symbol, prefer))
        
        primary_df = pd.DataFrame()
        secondary_df = pd.DataFrame()
        
        # Fetch from preferred source
        if prefer == 'hyperliquid' and self.use_hyperliquid:
            primary_df = self._get_hyperliquid_data(hl_symbol, timeframe, days)
            if validate and self.use_coinbase:
                secondary_df = self._get_coinbase_data(cb_symbol, timeframe, days=days)
                
        elif prefer == 'coinbase' and self.use_coinbase:
            primary_df = self._get_coinbase_data(cb_symbol, timeframe, days=days)
            if validate and self.use_hyperliquid:
                secondary_df = self._get_hyperliquid_data(hl_symbol, timeframe, days)
        
        # If preferred source failed, try the other
        if primary_df.empty and prefer == 'hyperliquid' and self.use_coinbase:
            logger.warning("Hyperliquid data fetch failed, falling back to Coinbase")
            primary_df = self._get_coinbase_data(cb_symbol, timeframe, days=days)
            
        elif primary_df.empty and prefer == 'coinbase' and self.use_hyperliquid:
            logger.warning("Coinbase data fetch failed, falling back to Hyperliquid")
            primary_df = self._get_hyperliquid_data(hl_symbol, timeframe, days)
        
        # Validate data if requested and we have both sources
        if validate and not secondary_df.empty and not primary_df.empty:
            self._validate_data(primary_df, secondary_df)
        
        return primary_df
    
    def _get_hyperliquid_data(self, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
        """Fetch data from Hyperliquid.
        
        Args:
            symbol: Symbol to fetch (e.g., 'BTC')
            timeframe: Timeframe (e.g., '1h')
            days: Number of days to look back
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not self.hyperliquid:
                return pd.DataFrame()
                
            logger.info("Fetching %s days of %s data for %s from Hyperliquid" % (days, timeframe, symbol))
            df = self.hyperliquid.fetch_historical_data(
                symbol, timeframe, days_back=days, 
                save_csv=False, output_dir=self.data_dir
            )
            
            if df.empty:
                logger.warning("No data returned from Hyperliquid for %s" % symbol)
            else:
                logger.info("Got %s candles from Hyperliquid" % len(df))
                
            return df
        except Exception as e:
            logger.error("Error fetching Hyperliquid data: %s" % e)
            return pd.DataFrame()
    
    def _get_coinbase_data(self, symbol: str, timeframe: str, 
                          days: Optional[int] = None, 
                          weeks: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from Coinbase.
        
        Args:
            symbol: Symbol to fetch (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '1h')
            days: Number of days to look back
            weeks: Number of weeks to look back (overrides days)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not self.coinbase:
                return pd.DataFrame()
            
            # Convert days to weeks for Coinbase API
            if weeks is None and days is not None:
                weeks = max(1, days // 7)  # At least 1 week
                
            logger.info("Fetching %s weeks of %s data for %s from Coinbase" % (weeks, timeframe, symbol))
            df = self.coinbase.get_historical_data(
                symbol, timeframe, weeks=weeks,
                cache=True, output_dir=self.data_dir
            )
            
            if df.empty:
                logger.warning("No data returned from Coinbase for %s" % symbol)
            else:
                logger.info("Got %s candles from Coinbase" % len(df))
                
            # Filter to requested days if specified
            if days is not None and not df.empty:
                cutoff = datetime.utcnow() - timedelta(days=days)
                df = df[df.index >= cutoff]
                
            return df
        except Exception as e:
            logger.error("Error fetching Coinbase data: %s" % e)
            return pd.DataFrame()
    
    def _validate_data(self, primary_df: pd.DataFrame, secondary_df: pd.DataFrame) -> None:
        """Validate data between two sources and log any discrepancies.
        
        Args:
            primary_df: Primary data source DataFrame
            secondary_df: Secondary data source DataFrame
        """
        if primary_df.empty or secondary_df.empty:
            return
            
        # Ensure both DataFrames have the same index format
        if 'timestamp' in primary_df.columns:
            primary_df = primary_df.set_index('timestamp')
            
        if 'timestamp' in secondary_df.columns:
            secondary_df = secondary_df.set_index('timestamp')
        
        # Find overlapping dates
        common_dates = primary_df.index.intersection(secondary_df.index)
        
        if len(common_dates) == 0:
            logger.warning("No overlapping dates between data sources for validation")
            return
            
        # Compare close prices for common dates
        primary_subset = primary_df.loc[common_dates]
        secondary_subset = secondary_df.loc[common_dates]
        
        # Calculate percentage difference
        diff_pct = abs((primary_subset['close'] - secondary_subset['close']) / primary_subset['close'] * 100)
        
        # Log validation results
        avg_diff = diff_pct.mean()
        max_diff = diff_pct.max()
        
        logger.info("Data validation: %s overlapping candles" % len(common_dates))
        logger.info("Average difference: %.2f%%, Maximum difference: %.2f%%" % (avg_diff, max_diff))
        
        if max_diff > 5.0:  # More than 5% difference
            logger.warning("Large price discrepancy detected between data sources (max: %.2f%%)" % max_diff)
            
    def get_latest_candles(self, symbol: str, timeframe: str, limit: int = 100, 
                          prefer: str = 'hyperliquid') -> pd.DataFrame:
        """Get the most recent candles for a symbol.
        
        Args:
            symbol: Symbol to fetch
            timeframe: Timeframe (e.g., '1h')
            limit: Number of candles to fetch
            prefer: Preferred data source ('hyperliquid', 'coinbase')
            
        Returns:
            DataFrame with the most recent candles
        """
        # Convert symbol format if needed
        hl_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        cb_symbol = f"{symbol}/USD" if '/' not in symbol else symbol
        
        df = pd.DataFrame()
        
        if prefer == 'hyperliquid' and self.use_hyperliquid:
            df = self.hyperliquid.fetch_latest_candles(hl_symbol, timeframe, limit)
            if df.empty and self.use_coinbase:
                logger.info("Falling back to Coinbase for latest candles")
                df = self._get_coinbase_data(cb_symbol, timeframe, days=limit)
                if not df.empty:
                    df = df.tail(limit)
        elif prefer == 'coinbase' and self.use_coinbase:
            df = self._get_coinbase_data(cb_symbol, timeframe, days=limit)
            if not df.empty:
                df = df.tail(limit)
            if df.empty and self.use_hyperliquid:
                logger.info("Falling back to Hyperliquid for latest candles")
                df = self.hyperliquid.fetch_latest_candles(hl_symbol, timeframe, limit)
        
        return df
    
    def get_current_price(self, symbol: str, prefer: str = 'hyperliquid') -> float:
        """Get the current price for a symbol.
        
        Args:
            symbol: Symbol to fetch
            prefer: Preferred data source ('hyperliquid', 'coinbase')
            
        Returns:
            Current price
        """
        # Convert symbol format if needed
        hl_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        cb_symbol = f"{symbol}/USD" if '/' not in symbol else symbol
        
        price = 0.0
        
        if prefer == 'hyperliquid' and self.use_hyperliquid:
            # Get the latest candle from Hyperliquid
            df = self.hyperliquid.fetch_latest_candles(hl_symbol, '1m', 1)
            if not df.empty:
                price = df['close'].iloc[-1]
            elif self.use_coinbase:
                # Fall back to Coinbase
                price = self.coinbase.get_current_price(cb_symbol)
        elif prefer == 'coinbase' and self.use_coinbase:
            price = self.coinbase.get_current_price(cb_symbol)
            if price == 0.0 and self.use_hyperliquid:
                # Fall back to Hyperliquid
                df = self.hyperliquid.fetch_latest_candles(hl_symbol, '1m', 1)
                if not df.empty:
                    price = df['close'].iloc[-1]
        
        return price
