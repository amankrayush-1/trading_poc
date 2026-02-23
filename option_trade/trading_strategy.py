"""
Trading strategy module.
Follows Open/Closed Principle - strategies can be extended without modification.
"""
from abc import ABC, abstractmethod
from typing import Optional
from option_trade.data_fetcher import OHLCData


class TradingSignal:
    """Represents a trading signal."""
    
    CALL_SPREAD = "CALL_SPREAD"
    PUT_SPREAD = "PUT_SPREAD"
    EXIT_TRADE = "EXIT_TRADE"
    NO_SIGNAL = "NO_SIGNAL"
    
    def __init__(self, signal_type: str, reason: str = ""):
        self.signal_type = signal_type
        self.reason = reason
    
    def __repr__(self) -> str:
        return f"TradingSignal({self.signal_type}, {self.reason})"


class TradingStrategy(ABC):
    """
    Abstract base class for trading strategies.
    Follows Open/Closed Principle - open for extension, closed for modification.
    """
    
    @abstractmethod
    def generate_signal(self, current_candle: OHLCData, ema_values: dict) -> TradingSignal:
        """
        Generate trading signal based on current candle and EMA values.
        
        Args:
            current_candle: Current OHLC candle
            ema_values: Dictionary with EMA values
            
        Returns:
            TradingSignal object
        """
        pass
    
    @abstractmethod
    def check_exit_signal(self, current_candle: OHLCData, ema_values: dict) -> TradingSignal:
        """
        Check if exit conditions are met.
        
        Args:
            current_candle: Current OHLC candle
            ema_values: Dictionary with EMA values
            
        Returns:
            TradingSignal object (EXIT_TRADE or NO_SIGNAL)
        """
        pass


class EMATouchStrategy(TradingStrategy):
    """
    Strategy that triggers when 15-min candle touches EMA 33 low.
    """
    
    def __init__(self, call_spread_enabled: bool = True, put_spread_enabled: bool = False):
        """
        Initialize EMA touch strategy.
        
        Args:
            call_spread_enabled: Whether call spread is enabled
            put_spread_enabled: Whether put spread is enabled
        """
        self.call_spread_enabled = call_spread_enabled
        self.put_spread_enabled = put_spread_enabled
    
    def generate_signal(self, current_candle: OHLCData, ema_values: dict) -> TradingSignal:
        """
        Generate signal when candle low touches or crosses below EMA 33 low.
        
        Logic:
        - If candle low <= EMA low and call spread enabled -> CALL_SPREAD
        - If candle high >= EMA high and put spread enabled -> PUT_SPREAD
        
        Args:
            current_candle: Current OHLC candle
            ema_values: Dictionary with 'ema_low', 'ema_high', etc.
            
        Returns:
            TradingSignal object
        """
        if not ema_values:
            return TradingSignal(TradingSignal.NO_SIGNAL, "No EMA values available")
        
        ema_low = ema_values.get('ema_low')
        ema_high = ema_values.get('ema_high')
        
        if ema_low is None or ema_high is None:
            return TradingSignal(TradingSignal.NO_SIGNAL, "EMA values not available")
        
        # Check if candle low touches or crosses below EMA low (bullish signal)
        if self.call_spread_enabled and current_candle.low <= ema_low:
            reason = f"Candle low ({current_candle.low:.2f}) touched/crossed EMA low ({ema_low:.2f})"
            return TradingSignal(TradingSignal.CALL_SPREAD, reason)
        
        # Check if candle high touches or crosses above EMA high (bearish signal)
        if self.put_spread_enabled and current_candle.high >= ema_high:
            reason = f"Candle high ({current_candle.high:.2f}) touched/crossed EMA high ({ema_high:.2f})"
            return TradingSignal(TradingSignal.PUT_SPREAD, reason)
        
        return TradingSignal(TradingSignal.NO_SIGNAL, "No EMA touch detected")
    
    def check_exit_signal(self, current_candle: OHLCData, ema_values: dict) -> TradingSignal:
        """
        Check if exit conditions are met.
        Exit when 15-minute candle closes above EMA 33 high.
        
        Args:
            current_candle: Current OHLC candle
            ema_values: Dictionary with EMA values
            
        Returns:
            TradingSignal object (EXIT_TRADE or NO_SIGNAL)
        """
        if not ema_values:
            return TradingSignal(TradingSignal.NO_SIGNAL, "No EMA values available")
        
        ema_high = ema_values.get('ema_high')
        
        if ema_high is None:
            return TradingSignal(TradingSignal.NO_SIGNAL, "EMA high not available")
        
        # Exit if candle close is above EMA high
        if current_candle.close > ema_high:
            reason = f"Candle close ({current_candle.close:.2f}) above EMA high ({ema_high:.2f})"
            return TradingSignal(TradingSignal.EXIT_TRADE, reason)
        
        return TradingSignal(TradingSignal.NO_SIGNAL, "No exit condition met")


class SignalValidator:
    """
    Validates trading signals based on time and other constraints.
    Follows Single Responsibility Principle.
    """
    
    def __init__(self, trading_start_time: str = "09:30:00"):
        """
        Initialize signal validator.
        
        Args:
            trading_start_time: Time after which trading is allowed (HH:MM:SS)
        """
        self.trading_start_time = trading_start_time
    
    def is_valid_time(self, current_time: str) -> bool:
        """
        Check if current time is after trading start time.
        
        Args:
            current_time: Current time in HH:MM:SS format
            
        Returns:
            True if trading is allowed, False otherwise
        """
        return current_time >= self.trading_start_time
    
    def validate_signal(self, signal: TradingSignal, current_time: str) -> tuple[bool, str]:
        """
        Validate if signal should be acted upon.
        
        Args:
            signal: TradingSignal object
            current_time: Current time in HH:MM:SS format
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if signal.signal_type == TradingSignal.NO_SIGNAL:
            return False, "No signal generated"
        
        if not self.is_valid_time(current_time):
            return False, f"Trading not allowed before {self.trading_start_time}"
        
        return True, "Signal is valid"