# Master Data Collection System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/master-data-collection/releases) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive, modular Python package for collecting and analyzing blockchain data from multiple sources. Designed for advanced blockchain analysis, market tracking, and trading systems, this system provides real-time and historical data fetching with robust error handling, performance optimizations, and a centralized data storage structure.

## Features

- **Multi-Source Data Collection:** Fetch data from both Hyperliquid and Coinbase with smart fallback and cross-validation.
- **Extended Historical Data:** Access up to 100+ weeks of historical data through Coinbase integration.
- **Real-Time Market Data:** Fetch live prices, volumes, and trends for multiple symbols with parallel processing.
- **Centralized Data Storage:** All data is stored in a structured, cross-compatible format on a dedicated drive.
- **Advanced Blockchain Analysis:** Built to support wallet tracking, PnL calculations, and detection of market manipulation patterns.
- **Modular Design:** Easily integrate into existing projects or use as a standalone tool.
- **Reliability:** Includes caching, fallbacks, and detailed logging to ensure uninterrupted data collection.

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/yourusername/master-data-collection.git
cd master-data-collection
pip install -e .
```

## Quick Start

See [START_HERE.md](START_HERE.md) for a step-by-step guide to setting up and using the system.

## Documentation

- [START_HERE.md](START_HERE.md): Beginner-friendly guide to get started.
- [CLAUDE.md](CLAUDE.md): Detailed references for AI-assisted development and customization.

## Usage Examples

### Basic Market Data

```python
from master_data_collection.fetchers.market_data import fetch_market_data

# Fetch data for specific symbols
symbols = ["BTC", "ETH", "SOL"]
data = fetch_market_data(symbols)
for item in data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']}")
```

### Enhanced Data Collection with Multiple Sources

```python
from master_data_collection.fetchers.data_integration import DataIntegration

# Initialize with both Hyperliquid and Coinbase sources
data = DataIntegration(use_coinbase=True, use_hyperliquid=True)

# Get historical data with cross-validation between sources
btc_data = data.get_historical_data("BTC", "1h", days=7, validate=True)
print(f"Fetched {len(btc_data)} hourly candles for BTC")

# Get long-term historical data (automatically uses Coinbase)
btc_yearly = data.get_historical_data("BTC", "1d", weeks=52)
print(f"Fetched {len(btc_yearly)} daily candles for the past year")
```

### Enhanced Hyperliquid Fetcher

```python
from master_data_collection.fetchers.enhanced_hyperliquid_fetcher import EnhancedHyperliquidFetcher

# Initialize the enhanced Hyperliquid fetcher
fetcher = EnhancedHyperliquidFetcher()

# Fetch historical data for BTC with 15-minute timeframe for the past 7 days
btc_data = fetcher.fetch_historical_data("BTC", "15m", days_back=7, save_csv=True)
print(f"Fetched {len(btc_data)} 15-minute candles for BTC")
```

## Data Storage Structure

The system uses a centralized data storage structure on a dedicated drive (F:\Master_Data by default) with the following organization:

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

This structured approach supports the advanced blockchain analysis goals, including:

1. **Tracking Positions of Individual Wallets:** The wallet_data directory stores wallet profiles, trade positions, and patterns.

2. **Identifying Market Makers/Manipulators:** The analysis directory stores results from algorithms that identify suspicious trading patterns.

3. **Pattern Recognition:** The structured market data provides the foundation for implementing pattern recognition algorithms.

## Contributing

Contributions are welcome! Please submit issues and pull requests on the GitHub repository. Ensure updates maintain backward compatibility where possible.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
