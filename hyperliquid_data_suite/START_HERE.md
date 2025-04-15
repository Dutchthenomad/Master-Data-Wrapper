# Start Here: Hyperliquid Data Collection Suite

Welcome to the Hyperliquid Data Collection Suite! This guide is designed for users of all levels to quickly set up and start collecting data from the Hyperliquid API. Whether you're building a trading bot, conducting blockchain analysis, or monitoring market trends, this suite provides a reliable, modular foundation.

## Step 1: Installation

### Prerequisites
- Python 3.8 or higher
- `pip` for installing dependencies
- Access to Hyperliquid API (no API key required for public data endpoints as of v1.0.0)

### Install from GitHub (Recommended)
Once the package is hosted, install directly from the repository:
```bash
pip install git+https://github.com/yourusername/hyperliquid-data-suite.git
```

### Local Installation
If you have cloned the repository or downloaded the source:
```bash
git clone https://github.com/yourusername/hyperliquid-data-suite.git
cd hyperliquid-data-suite
pip install .
```

### Verify Installation
Test that the suite is installed correctly:
```python
import hyperliquid_data_suite
print(hyperliquid_data_suite.__version__)  # Should print '1.0.0' or current version
```

## Step 2: Basic Usage

### Fetch Real-Time Market Data
The primary feature of this suite is fetching live market data for cryptocurrencies on Hyperliquid.

```python
from hyperliquid_data_suite.fetchers.market_data import fetch_market_data

# Default symbols are BTC, ETH, SOL
market_data = fetch_market_data()
for item in market_data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']} | Trend: {item['trend']}")

# Or specify custom symbols
custom_symbols = ["BTC", "ARB", "XRP"]
custom_data = fetch_market_data(custom_symbols)
for item in custom_data:
    print(f"{item['symbol']}: ${item['price']} | Change: {item['change']}% | Volume: {item['volume']} | Trend: {item['trend']}")
```

### Key Features
- **Parallel Fetching:** Data for multiple symbols is fetched concurrently for speed.
- **Caching:** Prevents redundant API calls by caching recent data (default: 30 seconds).
- **Fallbacks:** Returns dummy data if API is unavailable to prevent application crashes.

## Step 3: Configuration

Customize the suite's behavior by modifying settings in `config/settings.py`:
- **Cache Duration:** Adjust how long data is cached before refreshing.
- **Default Symbols:** Change the default list of symbols to fetch.
- **Logging Level:** Set to `DEBUG` for detailed logs or `INFO` for summaries.

Example:
```python
# In config/settings.py
CACHE_DURATION_SECONDS = 60  # Cache data for 1 minute
DEFAULT_SYMBOLS = ["BTC", "ETH", "ARB", "SOL", "XRP"]
```

## Step 4: Advanced Usage

### Expanding Data Scope
The suite is built to be extended. Add new fetchers or endpoints in the `fetchers/` directory for order book data, funding rates, or historical data as Hyperliquid API evolves.

### Integration with Analysis Tools
Use the fetched data for advanced blockchain analysis:
- Track wallet positions and calculate PnL by correlating market prices with transaction data.
- Detect market maker or manipulator behavior by analyzing volume and price anomalies.

## Step 5: Updating with Hyperliquid Changes

Hyperliquid's API may update over time. This suite is versioned to handle such changes:
1. Check the [GitHub repository](https://github.com/yourusername/hyperliquid-data-suite/releases) for new releases.
2. Update via pip: `pip install --upgrade git+https://github.com/yourusername/hyperliquid-data-suite.git`
3. Review version notes in `README.md` for breaking changes or new features.

## Troubleshooting

- **Import Errors:** Ensure the package is installed correctly and dependencies (e.g., `requests`) are up to date.
- **API Failures:** Check Hyperliquid API status if data fetching fails. The suite will fall back to dummy data.
- **Slow Fetching:** If parallel fetching isn't speeding up requests, verify your network connection or reduce `max_workers` in `fetchers/market_data.py`.

For detailed debugging, consult logs or refer to [CLAUDE.md](CLAUDE.md) for AI-assisted development tips.

## Next Steps

Explore the full capabilities by integrating this suite into your project. Whether for a Flask backend, a trading bot, or a research tool, the modular design ensures flexibility. Contribute to the project by submitting issues or pull requests on GitHub to keep it aligned with Hyperliquid updates.

*Note: Replace 'yourusername' with the actual GitHub username once hosted.*
