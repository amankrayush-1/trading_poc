"""
Logging module for the trading system.
Follows Single Responsibility Principle - only handles logging.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class TradingLogger:
    """
    Centralized logging for the trading system.
    Implements Single Responsibility Principle.
    """
    
    def __init__(self, name: str = "TradingBot", log_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize trading logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler - detailed logs
        log_file = log_path / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler - simple logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)
    
    def log_trade(self, trade_type: str, strike: int, quantity: int, status: str, details: Optional[dict] = None):
        """
        Log trade execution details.
        
        Args:
            trade_type: Type of trade (CALL_SPREAD, PUT_SPREAD)
            strike: Strike price
            quantity: Quantity traded
            status: Trade status (success, failed)
            details: Additional trade details
        """
        message = f"TRADE: {trade_type} | Strike: {strike} | Qty: {quantity} | Status: {status}"
        if details:
            message += f" | Details: {details}"
        
        if status.lower() == 'success':
            self.info(message)
        else:
            self.error(message)
    
    def log_signal(self, signal_type: str, reason: str, is_valid: bool):
        """
        Log trading signal details.
        
        Args:
            signal_type: Type of signal
            reason: Reason for signal
            is_valid: Whether signal is valid
        """
        message = f"SIGNAL: {signal_type} | Reason: {reason} | Valid: {is_valid}"
        self.info(message)
    
    def log_candle(self, candle_data: dict):
        """
        Log candle data.
        
        Args:
            candle_data: Dictionary with OHLC data
        """
        message = f"CANDLE: O={candle_data.get('open'):.2f} H={candle_data.get('high'):.2f} " \
                 f"L={candle_data.get('low'):.2f} C={candle_data.get('close'):.2f}"
        self.debug(message)
    
    def log_ema(self, ema_values: dict):
        """
        Log EMA values.
        
        Args:
            ema_values: Dictionary with EMA values
        """
        message = f"EMA: Open={ema_values.get('ema_open'):.2f} High={ema_values.get('ema_high'):.2f} " \
                 f"Low={ema_values.get('ema_low'):.2f} Close={ema_values.get('ema_close'):.2f}"
        self.debug(message)
    
    def log_separator(self, char: str = "=", length: int = 80):
        """Log a separator line."""
        self.info(char * length)