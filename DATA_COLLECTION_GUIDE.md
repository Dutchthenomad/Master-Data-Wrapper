# Hyperliquid Master API: Data Collection Guide

This guide provides a comprehensive overview of all the data types that can be collected using the Hyperliquid Master API, how the data is saved, and how to schedule regular data collection.

## Data Types and Storage Format

### Market Data

* **Real-time Market Prices**
  * **What it collects:** Current price, 24h change, volume, bid/ask spread
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\realtime\{date}.csv`
  * **Update frequency:** As requested (can be scheduled)
  * **Example use:** Track current market conditions across multiple assets

* **OHLCV Candle Data**
  * **What it collects:** Open, High, Low, Close, Volume for multiple timeframes
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\{timeframe}\{start_date}_to_{end_date}.csv`
  * **Timeframes available:** 1m, 5m, 15m, 1h, 4h, 1d
  * **Example use:** Technical analysis, backtesting strategies

* **Order Book Data**
  * **What it collects:** Full order book with price levels, sizes, and counts
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\orderbook\{timestamp}.csv`
  * **Depth:** Configurable (default: 20 levels)
  * **Example use:** Market microstructure analysis, liquidity assessment

* **Recent Trades**
  * **What it collects:** Trade price, size, side (buy/sell), timestamp
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\trades\{date}.csv`
  * **Limit:** Configurable (default: 100 most recent trades)
  * **Example use:** Execution analysis, volume profile studies

* **Funding Rates**
  * **What it collects:** Current and historical funding rates
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\funding\{date}.csv`
  * **Example use:** Funding arbitrage strategies, cost analysis

* **Open Interest**
  * **What it collects:** Total open interest and changes over time
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\open_interest\{date}.csv`
  * **Example use:** Market sentiment analysis, liquidity tracking

### Market Aggregates

* **Exchange-wide Statistics**
  * **What it collects:** Total volume, number of trades, active markets
  * **How it's saved:** `F:\Master_Data\market_data\exchange\stats\{date}.csv`
  * **Example use:** Exchange activity monitoring, market comparison

* **Cross-validated Price Data**
  * **What it collects:** Prices from multiple sources (Hyperliquid, Coinbase) with validation
  * **How it's saved:** `F:\Master_Data\market_data\{symbol}\validated\{date}.csv`
  * **Example use:** Arbitrage detection, reliable price reference

### Advanced Data (Future Expansion)

* **Wallet Tracking Data**
  * **What it collects:** Position changes, PnL, trading patterns for specific wallets
  * **How it's saved:** `F:\Master_Data\wallet_data\{wallet_address}\positions\{date}.csv`
  * **Example use:** Whale tracking, market maker identification

* **Market Analysis Results**
  * **What it collects:** Pattern detection results, anomaly scores, manipulation indicators
  * **How it's saved:** `F:\Master_Data\analysis\{analysis_type}\{date}.csv`
  * **Example use:** Automated alerts, trading signal generation

## Scheduling Regular Data Collection

The system includes built-in scheduling capabilities to collect data at regular intervals without manual intervention.

### Using the Scheduler Module

```python
from master_data_collection.utils.scheduler import DataCollectionScheduler

# Create a scheduler for collecting BTC, ETH, and SOL data every 15 minutes
scheduler = DataCollectionScheduler()

# Schedule OHLCV data collection
scheduler.schedule_ohlcv_collection(
    symbols=["BTC", "ETH", "SOL"],
    timeframes=["15m", "1h"],
    interval_minutes=15,  # Run every 15 minutes
    start_time="09:00",   # Optional start time
    end_time="17:00"      # Optional end time (24/7 if not specified)
)

# Schedule order book snapshots every 5 minutes
scheduler.schedule_orderbook_collection(
    symbols=["BTC", "ETH"],
    interval_minutes=5,
    depth=50  # Get 50 levels deep
)

# Start all scheduled tasks
scheduler.start()

# The scheduler runs in the background - your main program can continue
# or you can keep it running with:
scheduler.join()  # This will block until scheduler is stopped
```

### Using Cron Jobs (Alternative)

For production environments, you can use the included command-line tools with system schedulers like cron:

```bash
# Example crontab entry to collect data every 15 minutes
*/15 * * * * python -m master_data_collection.tools.collect_ohlcv --symbols BTC,ETH,SOL --timeframes 15m,1h

# Collect order book data every 5 minutes
*/5 * * * * python -m master_data_collection.tools.collect_orderbook --symbols BTC,ETH --depth 50
```

## CCXT Integration

Yes, the system includes CCXT integration for accessing additional exchanges beyond Hyperliquid and Coinbase. This provides a consistent interface for collecting data from hundreds of exchanges.

### Using CCXT for Data Collection

```python
from master_data_collection.clients.ccxt_client import CCXTClient

# Initialize CCXT client for Binance
ccxt_client = CCXTClient(exchange="binance")

# Fetch OHLCV data
btc_data = ccxt_client.get_historical_data(
    symbol="BTC/USDT",
    timeframe="1h",
    days=7
)

# Fetch order book
order_book = ccxt_client.get_order_book("BTC/USDT", limit=20)

# The data is automatically saved to the centralized storage location
# using the same directory structure as Hyperliquid data
```

### Supported CCXT Exchanges

The system supports all exchanges available in CCXT (100+ exchanges), including:

* Binance
* Bybit
* OKX
* Kraken
* Kucoin
* FTX
* And many more

## Data Consistency and Cross-Compatibility

All data is saved in standardized formats with consistent column names, timestamps, and units regardless of the source. This ensures that data from different sources can be easily combined and analyzed together.

* **CSV Format:** All data is saved in CSV format by default for maximum compatibility
* **Timestamps:** All timestamps are standardized to UTC
* **Symbol Naming:** Consistent symbol naming across all sources
* **Data Validation:** Automatic validation and error correction

This cross-compatibility makes it easy to switch between data sources or combine data from multiple sources without changing your analysis code.
