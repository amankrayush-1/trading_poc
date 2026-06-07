"""
SOR (Sell on Rise) Strategy Implementation
This strategy implements trading logic based on first 30-minute candle analysis
"""

from typing import Dict, Any, Optional
from growwapi import GrowwAPI
from bot.utils import Utils
from datetime import datetime, time, timedelta
import time as time_module


class SORStrategy:
    """
    SOR (Sell on Rise) Strategy Class
    Implements the trading logic for SOR strategy
    """
    
    def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            groww: GrowwAPI instance
            utils: Utils instance with helper methods
            config: Full configuration dictionary
        """
        self.groww = groww
        self.utils = utils
        self.config = config
        
        # Extract config values
        self.expiry_to_trade = config.get('expiry_to_trade')
        self.spread_gap = int(config.get('spread_gap', 200))
        self.exchange = config.get('exchange', 'BSE')
        self.trading_symbol = config.get('trading_symbol', 'SENSEX')
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        self.atr = float(config.get('atr', 46))
        
        print(f"SORStrategy initialized with:")
        print(f"  - Expiry to Trade: {self.expiry_to_trade}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def get_previous_day_close(self) -> Optional[float]:
        """
        Get previous trading day's close price
        
        Returns:
            float: Previous day close or None if error
        """
        try:
            exchange_upper = self.exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange}")
            
            # Get previous trading day (skip weekends)
            today = datetime.now()
            days_back = 1
            if today.weekday() == 0:  # Monday
                days_back = 3
            elif today.weekday() == 6:  # Sunday
                days_back = 2
            
            previous_day = today - timedelta(days=days_back)
            
            # Get daily candle for previous day
            start_time = previous_day.strftime("%Y-%m-%d 09:15:00")
            end_time = previous_day.strftime("%Y-%m-%d 15:30:00")
            
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_DAY
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Candle format: [timestamp, open, high, low, close, volume]
                previous_day_close = historical_response['candles'][0][4]
                print(f"Previous day close: {previous_day_close}")
                return previous_day_close
            else:
                print("Unable to fetch previous day close")
                return None
                
        except Exception as e:
            print(f"Error fetching previous day close: {e}")
            return None
    
    def get_first_30min_candle(self) -> Optional[Dict[str, float]]:
        """
        Get first 30-minute candle (9:15-9:45 AM)
        
        Returns:
            Dictionary with OHLC data or None if error
        """
        try:
            exchange_upper = self.exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange}")
            
            # Get today's date
            today = datetime.now()
            start_time = today.strftime("%Y-%m-%d 09:15:00")
            end_time = today.strftime("%Y-%m-%d 09:45:00")
            
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_30_MINUTE
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Candle format: [timestamp, open, high, low, close, volume]
                candle = historical_response['candles'][0]
                return {
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4]
                }
            else:
                print("Unable to fetch first 30-minute candle")
                return None
                
        except Exception as e:
            print(f"Error fetching first 30-minute candle: {e}")
            return None
    
    def get_first_15min_candle(self) -> Optional[Dict[str, float]]:
        """
        Get first 15-minute candle (9:15-9:30 AM)
        
        Returns:
            Dictionary with OHLC data or None if error
        """
        return self.utils.get_first_15min_candle(self.exchange)
    
    def wait_until_time(self, target_time: time, description: str = "target time"):
        """
        Wait until a specific time is reached
        
        Args:
            target_time: Target time to wait for
            description: Description of what we're waiting for (for logging)
        """
        current_time = datetime.now().time()
        
        if current_time < target_time:
            wait_seconds = (datetime.combine(datetime.today(), target_time) -
                           datetime.combine(datetime.today(), current_time)).total_seconds()
            print(f"Waiting till {description}... (Current time: {current_time.strftime('%H:%M:%S')})")
            print(f"Will wait for {wait_seconds:.0f} seconds")
            time_module.sleep(wait_seconds)
            print(f"✓ {description} reached")
        else:
            print(f"Already past {description} (Current: {current_time.strftime('%H:%M:%S')})")
    
    def monitor_spot_price_for_two_levels(self, level1: float, level2: float, 
                                          end_time: time) -> Optional[str]:
        """
        Monitor spot price to check which level it touches first
        
        Args:
            level1: First target level (open - atr - 12.5) for call spread
            level2: Second target level (first 15min close - 2*atr + 12.5) for put spread
            end_time: Time to stop monitoring
            
        Returns:
            str: 'level1' if level1 touched first, 'level2' if level2 touched first, None if neither
        """
        print(f"\n--- Monitoring Spot Price for Two Levels (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"Level 1 (open - atr - 12.5): {level1}")
        print(f"Level 2 (first 15min close - 2*atr + 12.5): {level2}")
        
        while datetime.now().time() < end_time:
            # Check spot price every 2 seconds
            current_spot_price = self.utils.get_spot_price(self.exchange)
            
            if not current_spot_price:
                print("Unable to fetch spot price, retrying...")
                time_module.sleep(2)
                continue
            
            current_time = datetime.now().time()
            print(f"[{current_time.strftime('%H:%M:%S')}] Current Spot Price: {current_spot_price}")
            
            # Check if spot price touches level1 (upward)
            if current_spot_price >= level1:
                print(f"✓ Spot price touched Level 1 (open - atr - 12.5)! (Spot: {current_spot_price} >= Level: {level1})")
                return 'level1'
            
            # Check if spot price touches level2 (downward)
            if current_spot_price <= level2:
                print(f"✓ Spot price touched Level 2 (first 15min close - 2*atr + 12.5)! (Spot: {current_spot_price} <= Level: {level2})")
                return 'level2'
            
            print(f"✗ Neither level touched yet (Level1: {level1}, Spot: {current_spot_price}, Level2: {level2})")
            
            # Check if we've passed the end time
            if datetime.now().time() >= end_time:
                print(f"Reached end time {end_time.strftime('%H:%M:%S')} without any level touch")
                break
            
            # Wait 2 seconds before next check
            time_module.sleep(2)
        
        return None
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the SOR strategy
        
        Strategy Logic:
        1. Wait till 9:45 AM
        2. Check: current day Open > previous day close AND first 30 minute candle should be red
        
        Case 1: if spot price >= open - atr - 12.5, then execute call spread with ITM Strike
        Case 2: if spot price <= first 15 minute candle closing - 2 * atr + 12.5, then open put spread ITM strike
        
        After 12 PM, if level does not come, close trade.
        
        Returns:
            Dictionary with execution results
        """
        try:
            print("\n=== Executing SOR (Sell on Rise) Strategy ===")
            
            # Step 1: Wait until 9:45 AM
            time_9_45 = time(9, 45)
            self.wait_until_time(time_9_45, "9:45 AM")
            
            # Get first 30-minute candle (9:15-9:45 AM)
            print("\n--- Step 1: Analyzing First 30-Minute Candle (9:15-9:45 AM) ---")
            first_30min = self.get_first_30min_candle()
            
            if not first_30min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 30-minute candle"
                }
            
            current_day_open = first_30min['open']
            first_30min_close = first_30min['close']
            
            print(f"First 30-min Candle: O={current_day_open}, H={first_30min['high']}, L={first_30min['low']}, C={first_30min_close}")
            
            # Get previous day close
            print("\n--- Getting Previous Day Close ---")
            prev_day_close = self.get_previous_day_close()
            
            if prev_day_close is None:
                return {
                    "status": "error",
                    "error": "Unable to fetch previous day close"
                }
            
            print(f"Previous Day Close: {prev_day_close}")
            print(f"Current Day Open: {current_day_open}")
            
            # Check condition: current day Open > previous day close AND first 30 minute candle should be red
            is_red_candle = first_30min_close < current_day_open
            open_greater_than_prev_close = current_day_open > prev_day_close
            
            print(f"\nCondition Analysis:")
            print(f"  - Current Day Open > Previous Day Close: {open_greater_than_prev_close}")
            print(f"  - First 30-min Candle is Red: {is_red_candle}")
            
            if not (open_greater_than_prev_close and is_red_candle):
                print("\n✗ Entry conditions not met. No trade will be executed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "entry_conditions_not_met",
                    "open_greater_than_prev_close": open_greater_than_prev_close,
                    "is_red_candle": is_red_candle,
                    "first_30min_candle": first_30min
                }
            
            print("\n✓ Entry conditions met! Proceeding to monitor levels...")
            
            # Get first 15-minute candle for Case 2 calculation
            first_15min = self.get_first_15min_candle()
            if not first_15min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 15-minute candle"
                }
            
            first_15min_close = first_15min['close']
            print(f"First 15-min Candle Close: {first_15min_close}")
            
            # Calculate two levels
            level1_call = current_day_open - self.atr - 12.5  # Case 1: Call spread
            level2_put = first_15min_close - (2 * self.atr) + 12.5  # Case 2: Put spread
            
            print(f"\nLevel 1 (open - atr - 12.5): {current_day_open} - {self.atr} - 12.5 = {level1_call}")
            print(f"Level 2 (first 15min close - 2*atr + 12.5): {first_15min_close} - 2*{self.atr} + 12.5 = {level2_put}")
            
            # Monitor till 12 PM (cutoff time)
            time_12_00_pm = time(12, 0)
            level_touched = self.monitor_spot_price_for_two_levels(level1_call, level2_put, time_12_00_pm)
            
            if level_touched == 'level1':
                print("\n✓ Level 1 touched! Executing ITM call spread")
                return self.execute_call_spread(current_day_open, level1_call, first_30min)
            
            elif level_touched == 'level2':
                print("\n✓ Level 2 touched! Executing ITM put spread")
                return self.execute_put_spread(first_15min_close, level2_put, first_30min)
            
            else:
                print("\n✗ Neither level touched by 12 PM. No trade executed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "no_level_touched_by_12pm",
                    "level1_call": level1_call,
                    "level2_put": level2_put,
                    "first_30min_candle": first_30min
                }
            
        except Exception as e:
            print(f"✗ Error executing strategy: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_call_spread(self, current_day_open: float, level: float, 
                           first_30min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute ITM call spread
        
        Args:
            current_day_open: Current day open price
            level: Level that was touched
            first_30min: First 30-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        # Get current spot price and calculate ITM strike
        current_spot_price = self.utils.get_spot_price(self.exchange)
        current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
        
        # ITM strike: ATM + itm_points
        strike_price = current_atm_strike + self.itm_points
        total_quantity = self.number_of_lots * self.lot_size
        
        print(f"\nCall Spread Trade Details:")
        print(f"  - Current Spot Price: {current_spot_price}")
        print(f"  - Current ATM Strike: {current_atm_strike}")
        print(f"  - Strike Price (ATM + ITM): {strike_price}")
        print(f"  - Quantity: {total_quantity}")
        print(f"  - Expiry: {self.expiry_to_trade}")
        
        # Place call spread
        order_response = self.utils.place_call_spread(
            strike_price=strike_price,
            quantity=total_quantity,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_trade,
            spread_gap=self.spread_gap
        )
        
        return {
            "status": "success",
            "action": "call_spread_placed",
            "case": "case1",
            "trigger": "spot_price_above_open_minus_atr_minus_12.5",
            "strike": strike_price,
            "quantity": total_quantity,
            "spot_price": current_spot_price,
            "level": level,
            "first_30min_candle": first_30min,
            "order_response": order_response
        }
    
    def execute_put_spread(self, first_15min_close: float, level: float, 
                          first_30min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute ITM put spread
        
        Args:
            first_15min_close: First 15-minute candle close price
            level: Level that was touched
            first_30min: First 30-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        # Get current spot price and calculate ITM strike
        current_spot_price = self.utils.get_spot_price(self.exchange)
        current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
        
        # ITM strike: ATM - itm_points
        strike_price = current_atm_strike - self.itm_points
        total_quantity = self.number_of_lots * self.lot_size
        
        print(f"\nPut Spread Trade Details:")
        print(f"  - Current Spot Price: {current_spot_price}")
        print(f"  - Current ATM Strike: {current_atm_strike}")
        print(f"  - Strike Price (ATM - ITM): {strike_price}")
        print(f"  - Quantity: {total_quantity}")
        print(f"  - Expiry: {self.expiry_to_trade}")
        
        # Place put spread
        order_response = self.utils.place_put_spread(
            strike_price=strike_price,
            quantity=total_quantity,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_trade,
            spread_gap=self.spread_gap
        )
        
        return {
            "status": "success",
            "action": "put_spread_placed",
            "case": "case2",
            "trigger": "spot_price_below_first15min_close_minus_2atr_plus_12.5",
            "strike": strike_price,
            "quantity": total_quantity,
            "spot_price": current_spot_price,
            "level": level,
            "first_30min_candle": first_30min,
            "order_response": order_response
        }
