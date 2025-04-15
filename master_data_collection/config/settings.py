"""Configuration settings for the Master Data Collection System.

Customize these settings to adjust the behavior of the data fetchers and other components.
"""
import os
import logging
from typing import Optional

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data storage configuration - using dedicated data drive
DATA_DIR = "F:\\Master_Data"

# Structured data directories
MARKET_DATA_DIR = os.path.join(DATA_DIR, 'market_data')
WALLET_DATA_DIR = os.path.join(DATA_DIR, 'wallet_data')
ANALYSIS_DIR = os.path.join(DATA_DIR, 'analysis')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')

# Ensure all directories exist
for directory in [DATA_DIR, MARKET_DATA_DIR, WALLET_DATA_DIR, ANALYSIS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configure logging to use the logs directory
log_file = os.path.join(LOGS_DIR, 'master_data_collection.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'),
        logging.StreamHandler()
    ]
)

# Utility function to get data paths
def get_data_path(data_type: str, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> str:
    """Get the appropriate data directory path based on data type and parameters.
    
    Args:
        data_type: Type of data ('market', 'wallet', 'analysis')
        symbol: Optional cryptocurrency symbol (e.g., 'BTC')
        timeframe: Optional timeframe for market data (e.g., '1h')
        
    Returns:
        Path to the appropriate data directory
    """
    if data_type == 'market':
        base_dir = MARKET_DATA_DIR
    elif data_type == 'wallet':
        base_dir = WALLET_DATA_DIR
    elif data_type == 'analysis':
        base_dir = ANALYSIS_DIR
    else:
        base_dir = DATA_DIR
    
    if symbol:
        symbol_dir = os.path.join(base_dir, symbol.lower())
        os.makedirs(symbol_dir, exist_ok=True)
        
        if timeframe and data_type == 'market':
            timeframe_dir = os.path.join(symbol_dir, timeframe)
            os.makedirs(timeframe_dir, exist_ok=True)
            return timeframe_dir
        
        return symbol_dir
    
    return base_dir

# Cache settings
CACHE_DURATION_SECONDS = 30  # How long to cache data before fetching fresh data

# Default symbols to fetch data for
DEFAULT_SYMBOLS = ["BTC", "ETH", "SOL"]

# Logging level
# Options: 'DEBUG' for detailed logs, 'INFO' for summaries, 'WARNING' or 'ERROR' for minimal output
LOGGING_LEVEL = "INFO"

# File formats
DEFAULT_FILE_FORMAT = 'csv'  # Options: 'csv', 'parquet', 'json'

# Wallet tracking settings
MAX_WALLETS_TO_TRACK = 1000  # Maximum number of wallets to track
WALLET_HISTORY_DAYS = 90  # Number of days to keep wallet history

# Analysis settings
PATTERN_DETECTION_THRESHOLD = 0.75  # Threshold for pattern detection algorithms
ANOMALY_DETECTION_SENSITIVITY = 0.8  # Sensitivity for anomaly detection (0-1)
