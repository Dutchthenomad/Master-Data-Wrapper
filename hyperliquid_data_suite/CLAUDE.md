# Claude (AI-Assisted Development) Guide for Hyperliquid Data Collection Suite

This document provides comprehensive references and guidance for AI coding assistants like Claude, as well as human developers working alongside AI tools, to understand, maintain, and extend the Hyperliquid Data Collection Suite. It includes architectural insights, customization tips, and update strategies to ensure the suite remains robust as Hyperliquid evolves.

## Table of Contents
- [Architectural Overview](#architectural-overview)
- [Core Components](#core-components)
- [Customization for AI Coders](#customization-for-ai-coders)
- [Handling Hyperliquid API Updates](#handling-hyperliquid-api-updates)
- [Debugging and Error Handling](#debugging-and-error-handling)
- [Versioning and Changelog](#versioning-and-changelog)
- [Future Development Goals](#future-development-goals)

## Architectural Overview

The Hyperliquid Data Collection Suite is designed with modularity, reliability, and scalability in mind. Its structure allows for easy integration into diverse projects (e.g., Flask backends, standalone scripts) while supporting advanced blockchain analysis goals such as wallet tracking and market manipulation detection.

- **Root Directory:** `hyperliquid_data_suite/`
  - **Config:** `config/` - Settings for cache duration, default symbols, logging levels.
  - **Fetchers:** `fetchers/` - Modules for different data types (e.g., market data, order books).
  - **Utils:** `utils/` - Shared utilities for logging, error handling, and data processing.
  - **Clients:** `clients/` - API client implementations (e.g., HyperliquidClient wrapper).
- **Key Design Principles:**
  - **Modularity:** Each component (fetcher, client) is independent for easy swapping or extension.
  - **Performance:** Parallel processing with `concurrent.futures` for API calls to minimize latency.
  - **Reliability:** Caching (in-memory), fallbacks, and detailed logging to prevent data loss or crashes.
- **Intended Use Cases:** Real-time market tickers, historical data analysis, trading bots, and blockchain forensics.

## Core Components

### 1. HyperliquidClient (clients/hyperliquid_client.py)
- **Purpose:** Direct interface to Hyperliquid API endpoints.
- **Key Methods:**
  - `get_market_stats(symbol)`: Fetches price, volume, and other stats for a symbol.
  - *(Future methods for order books, funding rates, etc., can be added here.)*
- **Notes for AI:** When extending, ensure rate limiting is respected (TBD based on Hyperliquid docs) and handle HTTP errors with retries.

### 2. Market Data Fetcher (fetchers/market_data.py)
- **Purpose:** High-level module to fetch and process real-time market data for multiple symbols.
- **Key Features:**
  - Parallel fetching with `ThreadPoolExecutor` for speed.
  - In-memory caching (30-second default) to reduce API load.
  - Historical price storage for change percentage calculations.
  - Fallback data if API fails.
- **Notes for AI:** Optimize `max_workers` based on system resources or API limits. Consider async alternatives (e.g., `aiohttp`) for even faster I/O if needed.

### 3. Configuration (config/settings.py)
- **Purpose:** Centralize user-configurable settings.
- **Key Variables:**
  - `CACHE_DURATION_SECONDS`: How long to cache data before refreshing.
  - `DEFAULT_SYMBOLS`: List of default cryptocurrencies to track.
- **Notes for AI:** When adding new settings, ensure backward compatibility or clear migration instructions in version updates.

## Customization for AI Coders

AI assistants like Claude can accelerate development with this suite by following these guidelines:

### Extending Data Types
- **Add New Fetchers:** Duplicate the structure of `fetchers/market_data.py` for new data types (e.g., `fetch_order_book.py`). Ensure parallel processing and caching are implemented similarly.
- **Update HyperliquidClient:** Add corresponding methods in `clients/hyperliquid_client.py` for new endpoints. Reference Hyperliquid API docs (link TBD) for parameters and response formats.
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
- **Blockchain Analysis:** Combine market data with wallet transaction data (external source) to calculate PnL or detect anomalies.
- **Example Code Snippet:**
  ```python
  from hyperliquid_data_suite.fetchers.market_data import fetch_market_data
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

## Handling Hyperliquid API Updates

Hyperliquid may update its API, requiring adjustments to this suite. Follow this process to maintain compatibility:

1. **Monitor Official Docs:** Check Hyperliquid API documentation (link TBD) or changelog for endpoint or response format changes.
2. **Update HyperliquidClient:** Modify `clients/hyperliquid_client.py` to match new API specs. Use version-specific logic if backward compatibility is needed:
   ```python
   def get_market_stats(self, symbol, version="1.0"):
       if version == "1.0":
           endpoint = "/v1/market-stats"
       else:  # Hypothetical v2.0
           endpoint = "/v2/market-stats"
       # Rest of the request logic
   ```
3. **Increment Suite Version:** Update `__version__` in the package and document changes in `README.md` under "Version History."
4. **Test Thoroughly:** Add test cases in `tests/` for new API behaviors.
5. **Notify Users:** Update GitHub release notes with migration instructions if breaking changes occur.
- **Notes for AI:** Proactively search for Hyperliquid API update announcements (e.g., via web search if docs are unavailable) when users report fetch errors. Suggest versioned code paths to handle transitions.

## Debugging and Error Handling

- **Common Issues:**
  - **Import Errors:** Verify `sys.path` includes the suite's root or dependencies are installed (`requests`, etc.).
  - **API Timeouts/Errors:** Check Hyperliquid API status. The suite falls back to dummy data, but AI can suggest retry mechanisms.
  - **Data Inconsistencies:** If fetched data lacks expected fields, update response parsing in `HyperliquidClient`.
- **Logging:** Logs are output at `INFO` level by default. Set to `DEBUG` in `config/settings.py` for detailed request/response info.
- **Notes for AI:** When debugging, prioritize viewing logs and recent API responses. Use `view_file` or `run_command` tools to inspect runtime behavior. Suggest adding temporary debug prints if needed, but remove them before final commits.

## Versioning and Changelog

- **Current Version:** 1.0.0 (Initial release with real-time market data fetching)
- **Changelog Format:**
  - `vX.Y.Z (Release Date): Description of changes, new features, bug fixes, and Hyperliquid API compatibility notes.`
- **Update Process for AI:**
  1. Increment version in `hyperliquid_data_suite/__init__.py` (e.g., `__version__ = '1.1.0'`).
  2. Add entry to `README.md` under "Version History."
  3. Document Hyperliquid API version or endpoint changes if applicable.

## Future Development Goals

Align future enhancements with the user's vision for advanced blockchain analysis:
- **Wallet Tracking:** Add fetchers for transaction or position data if Hyperliquid exposes such endpoints.
- **Market Maker Detection:** Implement anomaly detection logic on top of volume and price data (e.g., sudden volume spikes).
- **WebSocket Support:** Transition from polling to WebSocket for real-time updates with lower latency.
- **Historical Data:** If Hyperliquid provides historical endpoints, add fetchers for OHLCV data to support pattern recognition.
- **Notes for AI:** Propose incremental features based on user fatigue. Prioritize low-effort, high-impact additions (e.g., WebSocket over historical data if real-time is the focus).

## Final Notes for AI Coders

When assisting with this suite, always:
- Reference the user's long-term goals (e.g., blockchain analysis, wallet profiling).
- Use provided tools (e.g., `edit_file`, `run_command`) to implement changes directly rather than suggesting code.
- Be concise but thorough in explanations, focusing on how changes align with flawless operation and modularity.
- Save important context or decisions to memory using `create_memory` tool for future reference.

This suite is a living project. Ensure every update enhances its role as the 'poster child' of Hyperliquid data collection, maintaining the high standards set by initial development.

*Note: Replace placeholders like 'yourusername' or TBD links with actual values once the repository is hosted or Hyperliquid docs are linked.*
