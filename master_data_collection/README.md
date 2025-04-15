# Hyperliquid Data Collection Suite

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/hyperliquid-data-suite/releases) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive, modular Python package for collecting data from the Hyperliquid API. Designed for developers and researchers working on blockchain analysis, market tracking, and trading systems, this suite provides real-time and historical data fetching with robust error handling and performance optimizations.

## Features

 
- **Multi-Source Data Collection:** Fetch data from both Hyperliquid and Coinbase with smart fallback and cross-validation.
- **Extended Historical Data:** Access up to 100+ weeks of historical data through Coinbase integration.
- **Real-Time Market Data:** Fetch live prices, volumes, and trends for multiple symbols with parallel processing.
- **Modular Design:** Easily integrate into existing projects or use as a standalone tool.
- **Reliability:** Includes caching, fallbacks, and detailed logging to ensure uninterrupted data collection.
- **Versioned for Updates:** Structured to adapt to Hyperliquid API changes with clear documentation for each release.
- **Advanced Analysis Ready:** Built to support wallet tracking, PnL calculations, and detection of market manipulation patterns.

## Installation

 

Once hosted on GitHub, you can install the suite via pip:

```bash
pip install git+https://github.com/yourusername/hyperliquid-data-suite.git
```

Alternatively, clone the repository and install locally:

```bash
git clone https://github.com/yourusername/hyperliquid-data-suite.git
cd hyperliquid-data-suite
pip install .
```

## Quick Start

 

See [START_HERE.md](START_HERE.md) for a step-by-step guide to setting up and using the suite.

## Documentation

 

- [START_HERE.md](START_HERE.md): Beginner-friendly guide to get started.
- [CLAUDE.md](CLAUDE.md): Detailed references for AI-assisted development and customization.
- [docs/reference/](docs/reference/): Official Hyperliquid API documentation.

## Usage Examples

 

### Basic Market Data

```python
from hyperliquid_data_suite.fetchers.market_data import fetch_market_data

# Fetch data for specific symbols
symbols = ["BTC", "ETH", "SOL"]
data = fetch_market_data(symbols)
for item in data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']}")
```

### Enhanced Data Collection with Multiple Sources

```python
from hyperliquid_data_suite.fetchers.data_integration import DataIntegration

# Initialize with both Hyperliquid and Coinbase sources
data = DataIntegration(use_coinbase=True, use_hyperliquid=True)

# Get historical data with cross-validation between sources
btc_data = data.get_historical_data("BTC", "1h", days=7, validate=True)
print(f"Fetched {len(btc_data)} hourly candles for BTC")

# Get long-term historical data (automatically uses Coinbase)
btc_yearly = data.get_historical_data("BTC", "1d", weeks=52)
print(f"Fetched {len(btc_yearly)} daily candles for the past year")
```

### Direct Coinbase Access for Extended History

```python
from hyperliquid_data_suite.clients.coinbase_client import CoinbaseClient

# Initialize Coinbase client
coinbase = CoinbaseClient()

# Get 2 years of weekly data
btc_data = coinbase.get_historical_data("BTC/USD", "1w", weeks=104)
print(f"Fetched {len(btc_data)} weekly candles spanning 2 years")
```

## Contributing

 

Contributions are welcome! Please submit issues and pull requests on the [GitHub repository](https://github.com/yourusername/hyperliquid-data-suite). Ensure updates account for Hyperliquid API changes and maintain backward compatibility where possible.

## License

 

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
