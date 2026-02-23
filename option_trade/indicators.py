"""
Technical indicators module.
Follows Single Responsibility Principle - only handles indicator calculations.
"""
from typing import List
from option_trade.data_fetcher import OHLCData


class EMACalculator:
    """
    Exponential Moving Average calculator.
    Implements Single Responsibility Principle.
    """
    
    def __init__(self, period: int = 33):
        """
        Initialize EMA calculator.
        
        Args:
            period: EMA period (default: 33)
        """
        self.period = period
        self.multiplier = 2 / (period + 1)
    
    def calculate_ema(self, values: List[float]) -> List[float]:
        """
        Calculate EMA for a list of values.
        
        Args:
            values: List of price values
            
        Returns:
            List of EMA values
        """
        if not values or len(values) < self.period:
            return []
        
        ema_values = []
        
        # Calculate initial SMA for the first EMA value
        sma = sum(values[:self.period]) / self.period
        ema_values.append(sma)
        
        # Calculate EMA for remaining values
        for i in range(self.period, len(values)):
            ema = (values[i] * self.multiplier) + (ema_values[-1] * (1 - self.multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_ema_from_candles(self, candles: List[OHLCData], price_type: str = 'close') -> List[float]:
        """
        Calculate EMA from OHLC candles.
        
        Args:
            candles: List of OHLCData objects
            price_type: Type of price to use ('open', 'high', 'low', 'close')
            
        Returns:
            List of EMA values
        """
        if price_type == 'open':
            values = [candle.open for candle in candles]
        elif price_type == 'high':
            values = [candle.high for candle in candles]
        elif price_type == 'low':
            values = [candle.low for candle in candles]
        else:  # default to close
            values = [candle.close for candle in candles]
        
        return self.calculate_ema(values)


class MultiEMACalculator:
    """
    Calculator for multiple EMAs (open, high, low, close).
    """
    
    def __init__(self, period: int = 33):
        """
        Initialize multi-EMA calculator.
        
        Args:
            period: EMA period (default: 33)
        """
        self.period = period
        self.ema_calculator = EMACalculator(period)
    
    def calculate_all_emas(self, candles: List[OHLCData]) -> dict:
        """
        Calculate EMA for open, high, low, and close prices.
        
        Args:
            candles: List of OHLCData objects
            
        Returns:
            Dictionary with 'ema_open', 'ema_high', 'ema_low', 'ema_close' keys
        """
        if not candles or len(candles) < self.period:
            return {
                'ema_open': [],
                'ema_high': [],
                'ema_low': [],
                'ema_close': []
            }
        
        return {
            'ema_open': self.ema_calculator.calculate_ema_from_candles(candles, 'open'),
            'ema_high': self.ema_calculator.calculate_ema_from_candles(candles, 'high'),
            'ema_low': self.ema_calculator.calculate_ema_from_candles(candles, 'low'),
            'ema_close': self.ema_calculator.calculate_ema_from_candles(candles, 'close')
        }
    
    def get_latest_emas(self, candles: List[OHLCData]) -> dict:
        """
        Get the latest EMA values for all price types.
        
        Args:
            candles: List of OHLCData objects
            
        Returns:
            Dictionary with latest EMA values or None if insufficient data
        """
        all_emas = self.calculate_all_emas(candles)
        
        if not all_emas['ema_close']:
            return None
        
        return {
            'ema_open': all_emas['ema_open'][-1],
            'ema_high': all_emas['ema_high'][-1],
            'ema_low': all_emas['ema_low'][-1],
            'ema_close': all_emas['ema_close'][-1]
        }