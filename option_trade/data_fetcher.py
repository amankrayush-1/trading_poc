"""
Data fetcher module for retrieving market data.
Follows Single Responsibility Principle - only handles data fetching.
"""
from datetime import datetime
from typing import Dict, List, Optional
from growwapi import GrowwAPI


class OHLCData:
    """Data class for OHLC candle data."""
    
    def __init__(self, timestamp: int, open: float, high: float, low: float, close: float, volume: float = 0):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def __repr__(self) -> str:
        return f"OHLC(O={self.open}, H={self.high}, L={self.low}, C={self.close})"


class MarketDataFetcher:
    """
    Responsible for fetching market data from Groww API.
    Implements Single Responsibility Principle.
    """
    
    def __init__(self, groww_api: GrowwAPI, exchange: str = "NSE", segment: str = "CASH"):
        """
        Initialize market data fetcher.
        
        Args:
            groww_api: Authenticated GrowwAPI instance
            exchange: Exchange name (default: NSE)
            segment: Market segment (default: CASH)
        """
        self.groww = groww_api
        self.exchange = exchange
        self.segment = segment
    
    def _get_candle_interval_constant(self, interval_minutes: int) -> str:
        """Convert interval in minutes to Groww API candle interval constant"""
        interval_map = {
            1: self.groww.CANDLE_INTERVAL_MIN_1,
            2: self.groww.CANDLE_INTERVAL_MIN_2,
            3: self.groww.CANDLE_INTERVAL_MIN_3,
            5: self.groww.CANDLE_INTERVAL_MIN_5,
            10: self.groww.CANDLE_INTERVAL_MIN_10,
            15: self.groww.CANDLE_INTERVAL_MIN_15,
            30: self.groww.CANDLE_INTERVAL_MIN_30,
            60: self.groww.CANDLE_INTERVAL_HOUR_1,
            240: self.groww.CANDLE_INTERVAL_HOUR_4,
            1440: self.groww.CANDLE_INTERVAL_DAY,
            10080: self.groww.CANDLE_INTERVAL_WEEK,
        }
        if interval_minutes not in interval_map:
            raise ValueError(f"Unsupported interval: {interval_minutes} minutes")
        return interval_map[interval_minutes]
    
    def get_ltp(self, trading_symbol: str) -> Optional[float]:
        """
        Get Last Traded Price for a symbol.
        
        Args:
            trading_symbol: Trading symbol (e.g., "NIFTY")
            
        Returns:
            Last traded price or None if error
        """
        try:
            ltp_response = self.groww.get_ltp(
                segment=self.segment,
                exchange_trading_symbols=f"{self.exchange}_{trading_symbol}"
            )
            return ltp_response.get(f"{self.exchange}_{trading_symbol}")
        except Exception as e:
            print(f"Error fetching LTP for {trading_symbol}: {e}")
            return None
    
    def get_first_candle(self, trading_symbol: str, date: datetime, 
                        start_time: str = "09:15:00", 
                        end_time: str = "09:30:00") -> Optional[OHLCData]:
        """
        Get the first 15-minute candle (9:15 AM to 9:30 AM).
        
        Args:
            trading_symbol: Trading symbol (e.g., "NIFTY")
            date: Date for which to fetch data
            start_time: Start time in HH:MM:SS format
            end_time: End time in HH:MM:SS format
            
        Returns:
            OHLCData object or None if error
        """
        try:
            start_datetime = f"{date.strftime('%Y-%m-%d')} {start_time}"
            end_datetime = f"{date.strftime('%Y-%m-%d')} {end_time}"
            
            response = self.groww.get_historical_candles(
                groww_symbol=f"{self.exchange}-{trading_symbol}",
                exchange=self.exchange,
                segment=self.segment,
                start_time=start_datetime,
                end_time=end_datetime,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if response and 'candles' in response and len(response['candles']) > 0:
                candle = response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return OHLCData(
                    timestamp=candle[0],
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=candle[5] if len(candle) > 5 else 0
                )
            return None
        except Exception as e:
            print(f"Error fetching first candle for {trading_symbol}: {e}")
            return None
    
    def get_historical_candles(self, trading_symbol: str, 
                              start_time: str, 
                              end_time: str,
                              interval_minutes: int = 15) -> List[OHLCData]:
        """
        Get historical candle data for a time range.
        
        Args:
            trading_symbol: Trading symbol (e.g., "NIFTY")
            start_time: Start time in 'YYYY-MM-DD HH:MM:SS' format
            end_time: End time in 'YYYY-MM-DD HH:MM:SS' format
            interval_minutes: Candle interval in minutes
            
        Returns:
            List of OHLCData objects
        """
        try:
            response = self.groww.get_historical_candles(
                groww_symbol=f"{self.exchange}-{trading_symbol}",
                exchange=self.exchange,
                segment=self.segment,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self._get_candle_interval_constant(interval_minutes)
            )
            
            candles = []
            if response and 'candles' in response:
                for candle in response['candles']:
                    candles.append(OHLCData(
                        timestamp=candle[0],
                        open=candle[1],
                        high=candle[2],
                        low=candle[3],
                        close=candle[4],
                        volume=candle[5] if len(candle) > 5 else 0
                    ))
            return candles
        except Exception as e:
            print(f"Error fetching historical candles for {trading_symbol}: {e}")
            return []
    
    def get_current_15min_candle(self, trading_symbol: str) -> Optional[OHLCData]:
        """
        Get current 15-minute OHLC candle.
        
        Args:
            trading_symbol: Trading symbol (e.g., "NIFTY")
            
        Returns:
            OHLCData object or None if error
        """
        try:
            ohlc_response = self.groww.get_ohlc(
                segment=self.segment,
                exchange_trading_symbols=f"{self.exchange}_{trading_symbol}",
                interval="15m"
            )
            
            if ohlc_response and f"{self.exchange}_{trading_symbol}" in ohlc_response:
                candle_data = ohlc_response[f"{self.exchange}_{trading_symbol}"]
                return OHLCData(
                    timestamp=int(datetime.now().timestamp()),
                    open=candle_data.get('open'),
                    high=candle_data.get('high'),
                    low=candle_data.get('low'),
                    close=candle_data.get('close')
                )
            return None
        except Exception as e:
            print(f"Error fetching current 15-min candle for {trading_symbol}: {e}")
            return None