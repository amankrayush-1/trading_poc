"""
Configuration module for option trading system.
Centralizes all configuration parameters.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TradingConfig:
    """Trading configuration parameters."""
    
    # Access token for Groww API
    access_token: str
    
    # Trading symbol
    trading_symbol: str = "NIFTY"
    
    # Option configuration from constant.py
    call_option: str = "25N04"
    put_option: str = "25N04"
    spread_gap: int = 200
    
    # Trading flags
    call_spread_enabled: bool = True
    put_spread_enabled: bool = False
    
    # Trading parameters
    quantity: int = 50
    ema_period: int = 33
    
    # Time constraints
    trading_start_time: str = "09:30:00"
    first_candle_start: str = "09:15:00"
    first_candle_end: str = "09:30:00"
    
    # Candle interval in minutes
    candle_interval: int = 15
    
    # Exchange and segment
    exchange: str = "NSE"
    segment_cash: str = "CASH"
    segment_fno: str = "FNO"


def load_config(access_token: str) -> TradingConfig:
    """
    Load trading configuration.
    
    Args:
        access_token: Groww API access token
        
    Returns:
        TradingConfig instance
    """
    # Import from constant.py
    try:
        from option_trade.constant import (
            call_option,
            put_option,
            spread_gap,
            call_spread,
            put_spread
        )
        
        return TradingConfig(
            access_token=access_token,
            call_option=call_option,
            put_option=put_option,
            spread_gap=spread_gap,
            call_spread_enabled=call_spread,
            put_spread_enabled=put_spread
        )
    except ImportError:
        # Return default config if constant.py is not available
        return TradingConfig(access_token=access_token)