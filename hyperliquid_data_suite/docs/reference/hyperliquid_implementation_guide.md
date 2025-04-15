# HyperLiquid Implementation Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Connection Setup](#connection-setup)
3. [Market Data Retrieval](#market-data-retrieval)
4. [Account Management](#account-management)
5. [Order Execution](#order-execution)
6. [WebSocket Implementation](#websocket-implementation)
7. [Common Issues and Solutions](#common-issues-and-solutions)

## Introduction

This guide provides practical implementation examples for interacting with the HyperLiquid API, focused on the needs of trading connectors. It complements the official API reference with concrete code examples and best practices.

## Connection Setup

### API Endpoints

```python
# Constants for API endpoints
MAINNET_BASE_URL = "https://api.hyperliquid.xyz"
TESTNET_BASE_URL = "https://api.hyperliquid-testnet.xyz"

MAINNET_WS_URL = "wss://api.hyperliquid.xyz/ws"
TESTNET_WS_URL = "wss://api.hyperliquid-testnet.xyz/ws"

# Example initialization in a connector class
def __init__(self, testnet=False):
    self.testnet = testnet
    if self.testnet:
        self.base_url = TESTNET_BASE_URL
        self.ws_url = TESTNET_WS_URL
    else:
        self.base_url = MAINNET_BASE_URL
        self.ws_url = MAINNET_WS_URL
```

### Authentication Setup

```python
import eth_account
import eth_utils
import json
from eth_account.messages import encode_defunct

class HyperliquidConnector:
    def __init__(self, wallet_address, private_key, testnet=False):
        self.wallet_address = wallet_address
        self.private_key = private_key
        # API endpoints setup as shown above
        
    def _sign_message(self, message):
        """Sign a message using the private key"""
        # Convert message to bytes and hash it
        message_bytes = message.encode('utf-8')
        message_hash = eth_utils.keccak(message_bytes)
        
        # Sign the hash
        signed_message = eth_account.Account.sign_message(
            encode_defunct(message_hash),
            private_key=self.private_key
        )
        
        # Return the signature as a hex string
        return signed_message.signature.hex()
```

## Market Data Retrieval

### Getting Exchange Metadata

```python
import requests

def get_exchange_meta(self):
    """Get exchange metadata including asset information"""
    response = requests.post(
        f"{self.base_url}/info",
        json={"type": "meta"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get metadata: {response.text}")
```

### Getting Asset Contexts (Market Data)

```python
def get_asset_contexts(self):
    """Get current market data for all assets"""
    response = requests.post(
        f"{self.base_url}/info",
        json={"type": "metaAndAssetCtxs"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        # data[0] contains universe metadata
        # data[1] contains asset contexts (market data)
        return data
    else:
        raise Exception(f"Failed to get asset contexts: {response.text}")
```

### Getting Market Prices

```python
def get_markets(self):
    """Get all market prices"""
    response = requests.post(
        f"{self.base_url}/info",
        json={"type": "allMids"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get markets: {response.text}")
```

### Getting Order Book Data

```python
def get_order_book(self, symbol):
    """Get L2 order book for a specific symbol"""
    response = requests.post(
        f"{self.base_url}/info",
        json={
            "type": "l2Book",
            "coin": symbol
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        book_data = response.json()
        # Format: [bids, asks]
        # Each side is a list of {px, sz, n} objects
        # where n is the number of orders at that price level
        bids = book_data[0]
        asks = book_data[1]
        
        return {
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
    else:
        raise Exception(f"Failed to get order book: {response.text}")
```

### Getting Recent Trades

```python
def get_recent_trades(self, symbol):
    """Get recent trades for a specific symbol"""
    response = requests.post(
        f"{self.base_url}/info",
        json={
            "type": "trades",
            "coin": symbol
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        trades = response.json()
        formatted_trades = [{
            "id": trade.get("tid", ""),
            "price": float(trade["px"]),
            "size": float(trade["sz"]),
            "side": "buy" if trade["side"] == "B" else "sell",
            "timestamp": trade["time"]
        } for trade in trades]
        
        return formatted_trades
    else:
        raise Exception(f"Failed to get recent trades: {response.text}")
```

## Account Management

### Getting Account Balance

```python
def get_account_balance(self):
    """Get account balance and positions"""
    response = requests.post(
        f"{self.base_url}/info",
        json={
            "type": "clearinghouseState",
            "user": self.wallet_address
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        account_data = response.json()
        return {
            "usdc_balance": float(account_data.get("crossMarginSummary", {}).get("accountValue", "0")),
            "positions": [{
                "symbol": position.get("coin", ""),
                "size": float(position.get("szi", "0")),
                "entry_price": float(position.get("entryPx", "0")),
                "liquidation_price": float(position.get("liquidationPx", "0")),
                "unrealized_pnl": float(position.get("unrealizedPnl", "0"))
            } for position in account_data.get("positions", [])]
        }
    else:
        raise Exception(f"Failed to get account balance: {response.text}")
```

### Getting Open Orders

```python
def get_open_orders(self, symbol=None):
    """Get open orders for a specific symbol or all symbols"""
    payload = {
        "type": "openOrders",
        "user": self.wallet_address
    }
    
    if symbol:
        payload["coin"] = symbol
    
    response = requests.post(
        f"{self.base_url}/info",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        orders = response.json()
        formatted_orders = [{
            "id": order.get("oid", 0),
            "symbol": order.get("coin", ""),
            "price": float(order.get("limitPx", "0")),
            "size": float(order.get("sz", "0")),
            "side": "buy" if order.get("side", "") == "B" else "sell",
            "timestamp": order.get("timestamp", 0)
        } for order in orders]
        
        return formatted_orders
    else:
        raise Exception(f"Failed to get open orders: {response.text}")
```

## Order Execution

### Placing a Limit Order

```python
def place_limit_order(self, symbol, side, price, size, post_only=False):
    """Place a limit order
    
    Args:
        symbol (str): Trading pair symbol (e.g., "BTC")
        side (str): Order side, "buy" or "sell"
        price (float): Limit price
        size (float): Order size
        post_only (bool): If True, order will be post-only (ALO)
    
    Returns:
        dict: Order response
    """
    # Get asset ID from symbol
    asset_id = self._get_asset_id(symbol)
    
    # Prepare order data
    order_data = {
        "a": asset_id,  # Asset ID
        "b": side.lower() == "buy",  # True for buy, False for sell
        "p": str(price),  # Price as string
        "s": str(size),  # Size as string
        "r": False,  # Reduce only flag
        "t": {
            "limit": {
                "tif": "Alo" if post_only else "Gtc"
            }
        }
    }
    
    # Prepare action data
    action = {
        "type": "order",
        "orders": [order_data],
        "grouping": "na"
    }
    
    # Sign and send the order
    return self._send_signed_action(action)
```

### Placing a Market Order

```python
def place_market_order(self, symbol, side, size):
    """Place a market order using IOC (Immediate or Cancel)
    
    Args:
        symbol (str): Trading pair symbol (e.g., "BTC")
        side (str): Order side, "buy" or "sell"
        size (float): Order size
    
    Returns:
        dict: Order response
    """
    # Get asset ID from symbol
    asset_id = self._get_asset_id(symbol)
    
    # Prepare order data
    order_data = {
        "a": asset_id,  # Asset ID
        "b": side.lower() == "buy",  # True for buy, False for sell
        "p": "0",  # Price doesn't matter for market orders
        "s": str(size),  # Size as string
        "r": False,  # Reduce only flag
        "t": {
            "limit": {
                "tif": "Ioc"  # Immediate or Cancel
            }
        }
    }
    
    # Prepare action data
    action = {
        "type": "order",
        "orders": [order_data],
        "grouping": "na"
    }
    
    # Sign and send the order
    return self._send_signed_action(action)
```

### Canceling Orders

```python
def cancel_order(self, symbol, order_id):
    """Cancel a specific order
    
    Args:
        symbol (str): Trading pair symbol (e.g., "BTC")
        order_id (int): Order ID to cancel
    
    Returns:
        dict: Cancel response
    """
    # Get asset ID from symbol
    asset_id = self._get_asset_id(symbol)
    
    # Prepare cancel data
    cancel_data = {
        "a": asset_id,  # Asset ID
        "o": order_id  # Order ID
    }
    
    # Prepare action data
    action = {
        "type": "cancel",
        "cancels": [cancel_data],
        "grouping": "na"
    }
    
    # Sign and send the cancel
    return self._send_signed_action(action)
```

### Signing and Sending Actions

```python
def _send_signed_action(self, action):
    """Sign and send an action to the exchange
    
    Args:
        action (dict): Action data
    
    Returns:
        dict: Response from the exchange
    """
    # Generate a nonce (current timestamp in milliseconds)
    nonce = int(time.time() * 1000)
    
    # Convert action to JSON string with no whitespace
    action_str = json.dumps(action, separators=(',', ':'))
    
    # Create the message to sign
    message = f"{self.wallet_address}:{nonce}:{action_str}"
    
    # Sign the message
    signature = self._sign_message(message)
    
    # Prepare the payload
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": self.wallet_address
    }
    
    # Send the request
    response = requests.post(
        f"{self.base_url}/exchange",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to execute action: {response.text}")
```

## WebSocket Implementation

### Connecting to WebSocket

```python
import asyncio
import websockets
import json

async def connect_websocket(self):
    """Connect to the HyperLiquid WebSocket API"""
    async with websockets.connect(self.ws_url) as websocket:
        # Subscribe to trades for BTC
        await websocket.send(json.dumps({
            "method": "subscribe",
            "subscription": {
                "type": "trades",
                "coin": "BTC"
            }
        }))
        
        # Subscribe to order book updates for BTC
        await websocket.send(json.dumps({
            "method": "subscribe",
            "subscription": {
                "type": "l2Book",
                "coin": "BTC"
            }
        }))
        
        # Set up heartbeat
        heartbeat_task = asyncio.create_task(self._send_heartbeats(websocket))
        
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                self._handle_websocket_message(data)
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            heartbeat_task.cancel()

async def _send_heartbeats(self, websocket):
    """Send heartbeat messages to keep the connection alive"""
    while True:
        try:
            await websocket.send(json.dumps({"method": "ping"}))
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        except Exception as e:
            print(f"Heartbeat error: {e}")
            break

def _handle_websocket_message(self, data):
    """Process incoming WebSocket messages"""
    channel = data.get("channel")
    
    if channel == "trades":
        self._process_trade_update(data.get("data", {}))
    elif channel == "l2Book":
        self._process_orderbook_update(data.get("data", {}))
    elif channel == "pong":
        # Heartbeat response, no action needed
        pass
    else:
        print(f"Unknown channel: {channel}")
```

## Common Issues and Solutions

### Authentication Issues

1. **Invalid Signature**: Ensure that the message being signed follows the exact format: `{wallet_address}:{nonce}:{action_json_without_whitespace}`.

2. **Nonce Issues**: Make sure your nonce is within 1 day of the current time and is larger than any previously used nonce.

3. **API Wallet Permissions**: Verify that your API wallet has the correct permissions for the actions you're trying to perform.

### Order Placement Issues

1. **Invalid Price/Size**: Check that your price and size values conform to the tick and lot size requirements for the asset.

2. **Insufficient Margin**: Ensure your account has enough margin to place the order.

3. **Post-Only Order Rejection**: If your post-only (ALO) order would immediately match, it will be rejected. Consider using a different price or order type.

### WebSocket Connection Issues

1. **Connection Timeouts**: Implement proper heartbeat messages to keep the connection alive.

2. **Rate Limiting**: Be aware of the rate limits for WebSocket connections and subscriptions.

3. **Error Handling**: Implement robust error handling and reconnection logic for WebSocket connections.

### Best Practices

1. **Batch Orders**: When possible, batch multiple orders together to reduce the number of API calls.

2. **Use Separate API Wallets**: For different trading processes or subaccounts, use separate API wallets to avoid nonce collisions.

3. **Implement Proper Error Handling**: Always handle API errors gracefully and implement appropriate retry logic.

4. **Monitor Rate Limits**: Be aware of the rate limits for different API endpoints and implement rate limiting in your code.

5. **Keep Track of Nonces**: Implement a reliable system for generating and tracking nonces to avoid issues with order placement.
