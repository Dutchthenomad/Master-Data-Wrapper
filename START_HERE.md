# Start Here: Master Data Collection System

Welcome to the Master Data Collection System! This guide is designed for users of all levels to quickly set up and start collecting blockchain data from multiple sources. Whether you're building a trading bot, conducting blockchain analysis, or monitoring market trends, this system provides a reliable, modular foundation with centralized data storage.

## Step 1: Installation

### Prerequisites
- Python 3.8 or higher
- `pip` for installing dependencies
- Dedicated storage drive for data (configured as F:\Master_Data by default)

### Local Installation
Clone the repository and install locally:
```bash
git clone https://github.com/yourusername/master-data-collection.git
cd master-data-collection
pip install -e .
```

### Verify Installation
Test that the system is installed correctly:
```python
import master_data_collection
print(master_data_collection.__version__)  # Should print '1.0.0' or current version
```

## Step 2: Data Storage Configuration

The system is configured to store all data in a structured format on a dedicated drive (F:\Master_Data by default). You can customize this location in the `config/settings.py` file:

```python
# In config/settings.py
DATA_DIR = "F:\\Master_Data"  # Change this to your preferred location
```

The system automatically creates the following directory structure:

```
F:\Master_Data\
├── market_data\     # For all cryptocurrency market data
│   ├── btc\15m\     # BTC data at 15-minute intervals
│   ├── eth\15m\     # ETH data at 15-minute intervals
│   └── sol\15m\     # SOL data at 15-minute intervals
├── wallet_data\     # For wallet tracking (future use)
├── analysis\        # For analysis results (future use)
└── logs\            # For system logs
```

## Step 3: Basic Usage

### Fetch Real-Time Market Data
The primary feature of this system is fetching live market data for cryptocurrencies.

```python
from master_data_collection.fetchers.market_data import fetch_market_data

# Default symbols are BTC, ETH, SOL
market_data = fetch_market_data()
for item in market_data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']}")

# Or specify custom symbols
custom_symbols = ["BTC", "ARB", "XRP"]
custom_data = fetch_market_data(custom_symbols)
for item in custom_data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']}")
```

### Fetch Historical Data with Cross-Validation
The system can fetch historical data from multiple sources with cross-validation.

```python
from master_data_collection.fetchers.data_integration import DataIntegration

# Initialize with both Hyperliquid and Coinbase sources
data = DataIntegration(use_coinbase=True, use_hyperliquid=True)

# Get historical data with cross-validation between sources
btc_data = data.get_historical_data("BTC", "1h", days=7, validate=True)
print(f"Fetched {len(btc_data)} hourly candles for BTC")
```

### Fetch and Save Historical Data
The system automatically saves fetched data to the configured data directory.

```python
from master_data_collection.fetchers.enhanced_hyperliquid_fetcher import EnhancedHyperliquidFetcher

# Initialize the enhanced Hyperliquid fetcher
fetcher = EnhancedHyperliquidFetcher()

# Fetch historical data for BTC with 15-minute timeframe for the past 7 days
# Data will be saved to F:\Master_Data\market_data\btc\15m\
btc_data = fetcher.fetch_historical_data("BTC", "15m", days_back=7, save_csv=True)
print(f"Fetched {len(btc_data)} 15-minute candles for BTC")
```

## Step 4: Configuration

Customize the system's behavior by modifying settings in `config/settings.py`:
- **Data Storage:** Change the location of the data directory.
- **Cache Duration:** Adjust how long data is cached before refreshing.
- **Default Symbols:** Change the default list of symbols to fetch.
- **Logging Level:** Set to `DEBUG` for detailed logs or `INFO` for summaries.

Example:
```python
# In config/settings.py
DATA_DIR = "D:\\Crypto_Data"  # Change data storage location
CACHE_DURATION_SECONDS = 60  # Cache data for 1 minute
DEFAULT_SYMBOLS = ["BTC", "ETH", "ARB", "SOL", "XRP"]
```

## Step 5: Advanced Usage

### Multi-Source Data Integration
The system can integrate data from multiple sources for more reliable analysis.

```python
from master_data_collection.fetchers.data_integration import DataIntegration

# Initialize with both Hyperliquid and Coinbase sources
data = DataIntegration(use_coinbase=True, use_hyperliquid=True)

# Get current price with source preference
btc_price_hl = data.get_current_price("BTC", prefer="hyperliquid")
btc_price_cb = data.get_current_price("BTC", prefer="coinbase")

print(f"BTC price from Hyperliquid: ${btc_price_hl}")
print(f"BTC price from Coinbase: ${btc_price_cb}")
print(f"Price difference: {abs(float(btc_price_hl) - float(btc_price_cb)) / float(btc_price_hl) * 100:.2f}%")
```

### Expanding Data Scope
The system is built to be extended. Add new fetchers or endpoints for additional data types as needed.

### Integration with Analysis Tools
Use the fetched data for advanced blockchain analysis:
- Track wallet positions and calculate PnL by correlating market prices with transaction data.
- Detect market maker or manipulator behavior by analyzing volume and price anomalies.
- Implement pattern recognition for suspicious trading activities.

## Troubleshooting

- **Import Errors:** Ensure the package is installed correctly and dependencies are up to date.
- **API Failures:** Check API status if data fetching fails. The system will fall back to dummy data.
- **Storage Errors:** Verify that the data storage drive is accessible and has sufficient space.
- **Slow Fetching:** If parallel fetching isn't speeding up requests, verify your network connection.

For detailed debugging, consult logs in the `F:\Master_Data\logs\` directory or refer to [CLAUDE.md](CLAUDE.md) for AI-assisted development tips.

## Next Steps

Explore the full capabilities by integrating this system into your project. Whether for a Flask backend, a trading bot, or a research tool, the modular design ensures flexibility. The centralized data storage structure provides a solid foundation for advanced blockchain analysis, including wallet tracking, market maker identification, and pattern recognition.
