#!/usr/bin/env python3
"""
Utility module for logging in the Hyperliquid Data Collection Suite.

Provides shared logging configuration and helpers to ensure consistent logging across components.
"""

import logging

# Default logging configuration
def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging with a specified level for the entire suite.
    
    Args:
        level (str): Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR'). Defaults to 'INFO'.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger(__name__).info(f"Logging configured with level {level}")

# Helper to get a logger for a specific module
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module or component.
    
    Args:
        name (str): Name of the module or component (usually __name__).
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
