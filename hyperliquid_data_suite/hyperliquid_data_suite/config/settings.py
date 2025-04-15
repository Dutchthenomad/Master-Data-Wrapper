"""
Configuration settings for the Hyperliquid Data Collection Suite.

Customize these settings to adjust the behavior of the data fetchers and other components.
"""

# Cache settings
CACHE_DURATION_SECONDS = 30  # How long to cache data before fetching fresh data

# Default symbols to fetch data for
DEFAULT_SYMBOLS = ["BTC", "ETH", "SOL"]

# Logging level
# Options: 'DEBUG' for detailed logs, 'INFO' for summaries, 'WARNING' or 'ERROR' for minimal output
LOGGING_LEVEL = "INFO"
