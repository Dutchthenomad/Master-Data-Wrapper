#!/usr/bin/env python3
"""
Hyperliquid API Client for the Hyperliquid Data Collection Suite

This client provides methods for interacting with the Hyperliquid API,
focusing on data collection endpoints for market analysis and trading.
"""

import time
import requests
from typing import Dict, Any, List, Optional, Union
from master_data_collection.utils.logging import get_logger

logger = get_logger(__name__)

class HyperliquidClient:
    """Client for interacting with the Hyperliquid API."""
    
    def __init__(self, testnet: bool = False):
        """Initialize the Hyperliquid API client.
        
        Args:
            testnet (bool): If True, use testnet API endpoints. Default is False.
        """
        if testnet:
            self.base_url = "https://api.hyperliquid-testnet.xyz"
            self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws"
        else:
            self.base_url = "https://api.hyperliquid.xyz"
            self.ws_url = "wss://api.hyperliquid.xyz/ws"
        
        logger.info(f"Initialized HyperliquidClient with base URL: {self.base_url}")
    
    def get_market_stats(self, coin: str) -> Dict[str, Any]:
        """Get market statistics for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            
        Returns:
            Dict[str, Any]: Market statistics for the specified coin.
        """
        try:
            response = requests.post(
                f"{self.base_url}/info",
                json={"type": "metaAndAssetCtxs"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            universe = data[0].get("universe", [])
            asset_ctxs = data[1]
            
            # Find the coin in the universe
            coin_info = None
            for i, asset in enumerate(universe):
                if asset.get("name") == coin:
                    coin_info = asset_ctxs[i] if i < len(asset_ctxs) else None
                    break
            
            if not coin_info:
                logger.warning(f"Coin {coin} not found in market data")
                return {}
            
            logger.info(f"Successfully retrieved market stats for {coin}")
            return coin_info
        except Exception as e:
            logger.error(f"Error getting market stats for {coin}: {e}")
            return {}
    
    def get_all_markets(self) -> Dict[str, str]:
        """Get all market prices.
        
        Returns:
            Dict[str, str]: Dictionary mapping coin symbols to prices.
        """
        try:
            logger.info("Fetching all market prices")
            response = requests.post(
                f"{self.base_url}/info",
                json={"type": "allMids"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            response.raise_for_status()
            markets = response.json()
            logger.info(f"Successfully retrieved prices for {len(markets)} markets")
            return markets
        except Exception as e:
            logger.error(f"Error getting all markets: {e}")
            return {}
    
    def get_exchange_meta(self) -> Dict[str, Any]:
        """Get exchange metadata including asset information.
        
        Returns:
            Dict[str, Any]: Exchange metadata.
        """
        try:
            logger.info("Fetching exchange metadata")
            response = requests.post(
                f"{self.base_url}/info",
                json={"type": "meta"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            response.raise_for_status()
            meta = response.json()
            logger.info("Successfully retrieved exchange metadata")
            return meta
        except Exception as e:
            logger.error(f"Error getting exchange metadata: {e}")
            return {}
    
    def get_order_book(self, coin: str, format_response: bool = True) -> Union[Dict[str, List[Dict[str, Any]]], Dict]:
        """Get L2 order book for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            format_response (bool): If True, format the response into a more usable structure.
                                   If False, return the raw API response.
            
        Returns:
            Union[Dict[str, List[Dict[str, Any]]], Dict]: Order book with bids and asks.
        """
        try:
            logger.info(f"Fetching order book for {coin}")
            response = requests.post(
                f"{self.base_url}/info",
                json={
                    "type": "l2Book",
                    "coin": coin
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            response.raise_for_status()
            book_data = response.json()
            
            if not format_response:
                return book_data
            
            # Format the response based on the actual API structure
            # The API returns {"coin": "BTC", "time": timestamp, "levels": [[bids], [asks]]}
            levels = book_data.get("levels", [])
            bids = levels[0] if len(levels) > 0 else []
            asks = levels[1] if len(levels) > 1 else []
            
            formatted_book = {
                "bids": [{
                    "price": float(level["px"]),
                    "size": float(level["sz"]),
                    "count": level["n"]
                } for level in bids],
                "asks": [{
                    "price": float(level["px"]),
                    "size": float(level["sz"]),
                    "count": level["n"]
                } for level in asks]
            }
            
            logger.info(f"Successfully retrieved order book for {coin} with {len(formatted_book['bids'])} bids and {len(formatted_book['asks'])} asks")
            return formatted_book
        except Exception as e:
            logger.error(f"Error getting order book for {coin}: {e}")
            return {"bids": [], "asks": []} if format_response else {}
    
    def get_recent_trades(self, coin: str, limit: int = 100, format_response: bool = True) -> Union[List[Dict[str, Any]], List]:
        """Get recent trades for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            limit (int): Maximum number of trades to return. Default is 100.
            format_response (bool): If True, format the response into a more usable structure.
                                   If False, return the raw API response.
            
        Returns:
            Union[List[Dict[str, Any]], List]: List of recent trades.
        """
        try:
            logger.info(f"Fetching recent trades for {coin}")
            response = requests.post(
                f"{self.base_url}/info",
                json={
                    "type": "trades",
                    "coin": coin
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            response.raise_for_status()
            trades = response.json()
            
            if not format_response:
                return trades[:limit]
            
            # Format the response
            formatted_trades = [{
                "id": trade.get("tid", ""),
                "price": float(trade["px"]),
                "size": float(trade["sz"]),
                "side": "buy" if trade["side"] == "B" else "sell",
                "timestamp": trade["time"]
            } for trade in trades[:limit]]
            
            logger.info(f"Successfully retrieved {len(formatted_trades)} recent trades for {coin}")
            return formatted_trades
        except Exception as e:
            logger.error(f"Error getting recent trades for {coin}: {e}")
            return []
    
    def get_candle_data(self, coin: str, interval: str, start_time: Optional[int] = None, end_time: Optional[int] = None, lookback_days: int = 1) -> List[Dict[str, Any]]:
        """Get candle (OHLCV) data for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            interval (str): Time interval for candles (e.g., '1m', '1h').
            start_time (int, optional): Start time in milliseconds since epoch.
                                        If None, calculated based on lookback_days.
            end_time (int, optional): End time in milliseconds since epoch.
                                      If None, current time is used.
            lookback_days (int): Number of days to look back if start_time is not provided.
            
        Returns:
            List[Dict[str, Any]]: List of candle data.
        """
        try:
            # Calculate start and end times if not provided
            if end_time is None:
                end_time = int(time.time() * 1000)  # Current time in milliseconds
            
            if start_time is None:
                start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)  # lookback_days ago
            
            logger.info(f"Fetching candle data for {coin} with interval {interval} from {start_time} to {end_time}")
            response = requests.post(
                f"{self.base_url}/info",
                json={
                    "type": "candleSnapshot",
                    "req": {
                        "coin": coin,
                        "interval": interval,
                        "startTime": start_time,
                        "endTime": end_time
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            response.raise_for_status()
            candles = response.json()
            
            logger.info(f"Successfully retrieved {len(candles)} candles for {coin}")
            return candles
        except Exception as e:
            logger.error(f"Error getting candle data for {coin}: {e}")
            return []
    
    def get_funding_rate(self, coin: str) -> float:
        """Get the current funding rate for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            
        Returns:
            float: Current funding rate as a percentage.
        """
        try:
            logger.info(f"Fetching funding rate for {coin}")
            market_stats = self.get_market_stats(coin)
            
            if not market_stats:
                return 0.0
            
            funding_rate = float(market_stats.get("funding", {}).get("fundingRate", "0")) * 100
            logger.info(f"Successfully retrieved funding rate for {coin}: {funding_rate}%")
            return funding_rate
        except Exception as e:
            logger.error(f"Error getting funding rate for {coin}: {e}")
            return 0.0
    
    def get_open_interest(self, coin: str) -> Dict[str, float]:
        """Get the open interest for a specific coin.
        
        Args:
            coin (str): The cryptocurrency symbol (e.g., 'BTC').
            
        Returns:
            Dict[str, float]: Open interest data including long and short positions.
        """
        try:
            logger.info(f"Fetching open interest for {coin}")
            market_stats = self.get_market_stats(coin)
            
            if not market_stats:
                return {"long": 0.0, "short": 0.0, "total": 0.0}
            
            oi_long = float(market_stats.get("openInterest", {}).get("long", "0"))
            oi_short = float(market_stats.get("openInterest", {}).get("short", "0"))
            
            result = {
                "long": oi_long,
                "short": oi_short,
                "total": oi_long + oi_short
            }
            
            logger.info(f"Successfully retrieved open interest for {coin}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting open interest for {coin}: {e}")
            return {"long": 0.0, "short": 0.0, "total": 0.0}
