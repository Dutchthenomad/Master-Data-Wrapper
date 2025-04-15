# Claude (AI-Assisted Development) Guide for Master Data Collection System

This document provides comprehensive references and guidance for AI coding assistants like Claude, as well as human developers working alongside AI tools, to understand, maintain, and extend the Master Data Collection System. It includes architectural insights, customization tips, and update strategies to ensure the system remains robust as blockchain APIs evolve.

## Table of Contents
- [Architectural Overview](#architectural-overview)
- [Core Components](#core-components)
- [Customization for AI Coders](#customization-for-ai-coders)
- [Handling API Updates](#handling-api-updates)
- [Debugging and Error Handling](#debugging-and-error-handling)
- [Versioning and Changelog](#versioning-and-changelog)
- [Future Development Goals](#future-development-goals)

## Architectural Overview

The Master Data Collection System is designed with modularity, reliability, and scalability in mind. Its structure allows for easy integration into diverse projects while supporting advanced blockchain analysis goals such as wallet tracking and market manipulation detection.

- **Root Directory:** `master_data_collection/`
  - **Config:** `config/` - Settings for cache duration, default symbols, logging levels, and data storage paths.
  - **Fetchers:** `fetchers/` - Modules for different data types (e.g., market data, order books).
  - **Utils:** `utils/` - Shared utilities for logging, error handling, and data processing.
  - **Clients:** `clients/` - API client implementations (e.g., HyperliquidClient, CoinbaseClient).
- **Key Design Principles:**
  - **Modularity:** Each component (fetcher, client) is independent for easy swapping or extension.
  - **Performance:** Parallel processing with `concurrent.futures` for API calls to minimize latency.
  - **Reliability:** Caching (in-memory), fallbacks, and detailed logging to prevent data loss or crashes.
  - **Centralized Data Storage:** All data is stored in a structured, cross-compatible format on a dedicated drive.
- **Intended Use Cases:** Real-time market tickers, historical data analysis, trading bots, and blockchain forensics.

## Core Components

### 1. Data Integration (fetchers/data_integration.py)
- **Purpose:** Unified data access with multiple source integration and validation.
- **Key Methods:**
  - `get_historical_data(symbol, timeframe, days, validate)`: Fetches historical data with cross-validation between sources.
  - `get_current_price(symbol, prefer)`: Gets the current price from multiple sources with preference option.
- **Notes for AI:** When extending, ensure data consistency across different sources and handle validation logic carefully.

### 2. Enhanced Hyperliquid Fetcher (fetchers/enhanced_hyperliquid_fetcher.py)
- **Purpose:** Fetch data from Hyperliquid with improved error handling and timestamp correction.
- **Key Features:**
  - Timestamp correction to handle API inconsistencies.
  - Robust error handling with retries.
  - Structured data storage in the centralized data directory.
- **Notes for AI:** Optimize batch sizes and retry logic based on API behavior.

### 3. Configuration (config/settings.py)
- **Purpose:** Centralize user-configurable settings and data storage paths.
- **Key Variables:**
  - `DATA_DIR`: Base directory for all data storage (F:\Master_Data by default).
  - `MARKET_DATA_DIR`, `WALLET_DATA_DIR`, `ANALYSIS_DIR`, `LOGS_DIR`: Structured data directories.
  - `CACHE_DURATION_SECONDS`: How long to cache data before refreshing.
  - `DEFAULT_SYMBOLS`: List of default cryptocurrencies to track.
- **Key Functions:**
  - `get_data_path(data_type, symbol, timeframe)`: Utility function to get the appropriate data directory path.
- **Notes for AI:** When adding new settings, ensure backward compatibility or clear migration instructions in version updates.

## Customization for AI Coders

AI assistants like Claude can accelerate development with this system by following these guidelines:

### Extending Data Types
- **Add New Fetchers:** Duplicate the structure of existing fetchers for new data types. Ensure parallel processing and caching are implemented similarly.
- **Update API Clients:** Add corresponding methods in client classes for new endpoints.
- **Example Task:**
  ```
  Task: Add support for fetching funding rates.
  Steps:
  1. In clients/hyperliquid_client.py, add get_funding_rate(symbol).
  2. In fetchers/, create funding_rate.py with parallel fetching.
  3. Update config/settings.py with DEFAULT_FUNDING_SYMBOLS if needed.
  4. Test with a script in tests/ directory.
  ```

### Performance Tuning
- **Adjust Parallelism:** Modify `max_workers` in `ThreadPoolExecutor` based on API rate limits or network constraints.
- **Caching Strategy:** Extend cache duration or implement persistent caching (e.g., Redis) for larger datasets.
- **Notes for AI:** Monitor API response times and errors to dynamically adjust fetch strategies. Use logging to track performance metrics.

### Integration with Analysis
- **Blockchain Analysis:** Combine market data with wallet transaction data to calculate PnL or detect anomalies.
- **Example Code Snippet:**
  ```python
  from master_data_collection.fetchers.market_data import fetch_market_data
  def analyze_wallet_pnl(wallet_transactions, symbols):
      market_data = fetch_market_data(symbols)
      prices = {item['symbol']: item['price'] for item in market_data}
      pnl = 0
      for tx in wallet_transactions:
          if tx['symbol'] in prices:
              value_change = (prices[tx['symbol']] - tx['entry_price']) * tx['amount']
              pnl += value_change
      return pnl
  ```
- **Notes for AI:** Ensure data consistency (timestamps, symbol formats) when merging with external datasets.

## Handling API Updates

API providers may update their endpoints, requiring adjustments to this system. Follow this process to maintain compatibility:

1. **Monitor Official Docs:** Check API documentation or changelog for endpoint or response format changes.
2. **Update API Clients:** Modify client classes to match new API specs. Use version-specific logic if backward compatibility is needed:
   ```python
   def get_market_stats(self, symbol, version="1.0"):
       if version == "1.0":
           endpoint = "/v1/market-stats"
       else:  # Hypothetical v2.0
           endpoint = "/v2/market-stats"
       # Rest of the request logic
   ```
3. **Increment System Version:** Update `__version__` in the package and document changes in `README.md` under "Version History."
4. **Test Thoroughly:** Add test cases for new API behaviors.
5. **Notify Users:** Update GitHub release notes with migration instructions if breaking changes occur.
- **Notes for AI:** Proactively search for API update announcements when users report fetch errors. Suggest versioned code paths to handle transitions.

## Debugging and Error Handling

- **Common Issues:**
  - **Import Errors:** Verify `sys.path` includes the system's root or dependencies are installed (`requests`, etc.).
  - **API Timeouts/Errors:** Check API status. The system falls back to dummy data, but AI can suggest retry mechanisms.
  - **Data Inconsistencies:** If fetched data lacks expected fields, update response parsing in client classes.
  - **Storage Errors:** Verify that the data storage drive (F:\Master_Data by default) is accessible and has sufficient space.
- **Logging:** Logs are output to both the console and a file in the logs directory. Set logging level to `DEBUG` in `config/settings.py` for detailed request/response info.
- **Notes for AI:** When debugging, prioritize viewing logs and recent API responses. Use `view_file` or `run_command` tools to inspect runtime behavior. Suggest adding temporary debug prints if needed, but remove them before final commits.

## Versioning and Changelog

- **Current Version:** 1.0.0 (Initial release with multi-source data collection and centralized storage)
- **Changelog Format:**
  - `vX.Y.Z (Release Date): Description of changes, new features, bug fixes, and API compatibility notes.`
- **Update Process for AI:**
  1. Increment version in `master_data_collection/__init__.py` (e.g., `__version__ = '1.1.0'`).
  2. Add entry to `README.md` under "Version History."
  3. Document API version or endpoint changes if applicable.

## Future Development Goals

Align future enhancements with the user's vision for advanced blockchain analysis:
- **Wallet Tracking:** Implement comprehensive tracking of individual wallet positions, PnL, and trading patterns.
- **Market Maker Detection:** Develop algorithms to identify wallets with high probability of being market makers or manipulators.
- **Pattern Recognition:** Implement detection of suspicious trading activities and market manipulation patterns.
- **WebSocket Support:** Transition from polling to WebSocket for real-time updates with lower latency.
- **Notes for AI:** Propose incremental features based on user fatigue. Prioritize low-effort, high-impact additions.

## Final Notes for AI Coders

When assisting with this system, always:
- Reference the user's long-term goals (e.g., blockchain analysis, wallet profiling).
- Use provided tools (e.g., `edit_file`, `run_command`) to implement changes directly rather than suggesting code.
- Be concise but thorough in explanations, focusing on how changes align with flawless operation and modularity.
- Save important context or decisions to memory using `create_memory` tool for future reference.

This system is a living project. Ensure every update enhances its role as a comprehensive blockchain data collection and analysis platform, maintaining the high standards set by initial development.
