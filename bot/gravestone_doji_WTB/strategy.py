"""
Bot 4 Strategy Implementation
This strategy implements trading logic based on first 15-minute candle analysis and previous day high
"""

from typing import Dict, Any, Optional
from growwapi import GrowwAPI
from bot.utils import Utils
from datetime import datetime, time, timedelta
import time as time_module


class Bot4Strategy:
    """
    Bot 4 Strategy Class
    Implements the trading logic for bot_4 strategy
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
        self.otm_points = int(config.get('otm_points', 50))
        self.atr = float(config.get('atr', 46))
        
        print(f"Bot4Strategy initialized with:")
        print(f"  - Expiry to Trade: {self.expiry_to_trade}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - OTM Points: {self.otm_points}")
        print(f"  - ATR: {self.atr}")
    
    def is_doji_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if a candle is a doji candle (can be green or red)
        Doji: small body with wicks on both sides
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            
        Returns:
            bool: True if doji candle, False otherwise
        """
        o = candle['open']
        h = candle['high']
        l = candle['low']
        c = candle['close']
        
        if c == 0 or o == 0:
            return False
        
        # Calculate body and wicks
        body_size = abs(c - o)
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        total_wick = upper_wick + lower_wick
        
        # Doji: body is very small compared to total range
        total_range = h - l
        if total_range == 0:
            return False
        
        body_percentage = body_size / total_range
        
        # Doji if body is less than 10% of total range
        return body_percentage < 0.1
    
    def check_lower_wick_condition(self, candle: Dict[str, float]) -> bool:
        """
        Check if lower wick > 2 * upper wick
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            
        Returns:
            bool: True if condition met, False otherwise
        """
        o = candle['open']
        h = candle['high']
        l = candle['low']
        c = candle['close']
        
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        
        return lower_wick > 2 * upper_wick
    
    def get_previous_day_high(self) -> Optional[float]:
        """
        Get previous trading day's high price
        
        Returns:
            float: Previous day high or None if error
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
                previous_day_high = historical_response['candles'][0][2]
                print(f"Previous day high: {previous_day_high}")
                return previous_day_high
            else:
                print("Unable to fetch previous day high")
                return None
                
        except Exception as e:
            print(f"Error fetching previous day high: {e}")
            return None
    
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
    
    def monitor_spot_price_for_level_touch(self, target_level: float, end_time: time,
                                           level_name: str = "target level", direction: str = "upward") -> bool:
        """
        Monitor spot price to check if it touches the target level until end_time
        
        Args:
            target_level: Target price level to check against
            end_time: Time to stop monitoring
            level_name: Name of the level for logging
            direction: "upward" for >= check, "downward" for <= check
            
        Returns:
            bool: True if level touched, False otherwise
        """
        print(f"\n--- Monitoring Spot Price for {level_name} Touch (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"{level_name}: {target_level} (Direction: {direction})")
        
        while datetime.now().time() < end_time:
            # Check spot price every 2 seconds
            current_spot_price = self.utils.get_spot_price(self.exchange)
            
            if not current_spot_price:
                print("Unable to fetch spot price, retrying...")
                time_module.sleep(2)
                continue
            
            current_time = datetime.now().time()
            print(f"[{current_time.strftime('%H:%M:%S')}] Current Spot Price: {current_spot_price}")
            
            # Check if spot price touches or crosses the target level based on direction
            if direction == "upward":
                if current_spot_price >= target_level:
                    print(f"✓ Spot price touched {level_name}! (Spot: {current_spot_price} >= Level: {target_level})")
                    return True
                else:
                    print(f"✗ Level not touched yet (Spot: {current_spot_price} < Level: {target_level})")
            else:  # downward
                if current_spot_price <= target_level:
                    print(f"✓ Spot price touched {level_name}! (Spot: {current_spot_price} <= Level: {target_level})")
                    return True
                else:
                    print(f"✗ Level not touched yet (Spot: {current_spot_price} > Level: {target_level})")
            
            # Check if we've passed the end time
            if datetime.now().time() >= end_time:
                print(f"Reached end time {end_time.strftime('%H:%M:%S')} without level touch")
                break
            
            # Wait 2 seconds before next check
            time_module.sleep(2)
        
        return False
    
    def monitor_spot_price_for_two_levels(self, level1: float, level2: float, 
                                          end_time: time) -> Optional[str]:
        """
        Monitor spot price to check which level it touches first
        
        Args:
            level1: First target level (open + atr)
            level2: Second target level (close - 2*atr + 12.5)
            end_time: Time to stop monitoring
            
        Returns:
            str: 'level1' if level1 touched first, 'level2' if level2 touched first, None if neither
        """
        print(f"\n--- Monitoring Spot Price for Two Levels (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"Level 1 (open + atr): {level1}")
        print(f"Level 2 (close - 2*atr + 12.5): {level2}")
        
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
                print(f"✓ Spot price touched Level 1 (open + atr)! (Spot: {current_spot_price} >= Level: {level1})")
                return 'level1'
            
            # Check if spot price touches level2 (downward)
            if current_spot_price <= level2:
                print(f"✓ Spot price touched Level 2 (close - 2*atr + 12.5)! (Spot: {current_spot_price} <= Level: {level2})")
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
        Execute the bot_4 strategy
        
        Strategy Logic:
        Step 1: Wait until 9:30 AM and capture OHLC data of first 15-minute candle (9:15-9:30 AM)
        
        Case 1: previous day high < open of first 15 minute candle
                if first 15 minute candle is Doji (It can be green or red candle) and lower wick > 2 * upper wick
                execute trade: fetch atm strike - take 2 * otm_points and execute sell call spread with spread_gap
        
        Case 2: previous day high > open of first 15 minute candle
                execute trade only if below condition meet:
                if green Doji and lower wick > 2 * upper wick
                Wait till 2 PM IST and watch if spot price touches open of first 15 candle + atr
                execute trade: fetch atm strike - take 2 * otm_points and execute sell call spread with spread_gap
        
        Case 3: if first 15 candle close < first 15 candle open and open - close > atr
                watch spot price, spot price will either first touch open + atr or close - 2 * atr + 12.5
                if spot price touches open + atr: fetch atm strike - take 1 * otm_points then execute sell call spread with number_of_lots/2 and if spot price touches open + 2 * atr: fetch atm strike - take 2 * otm_points then again execute sell call spread with number_of_lots/2
                if spot price touches close - atr + 12.5: fetch atm strike + take 1 * otm_points then execute sell put spread with number_of_lots/2 and if spot price touches close - 2 * atr + 12.5: fetch atm strike + take 2 * otm_points then again execute sell put spread with number_of_lots/2
        
        Returns:
            Dictionary with execution results
        """
        try:
            print("\n=== Executing Bot 4 Strategy ===")
            
            # Step 1: Wait until 9:30 AM
            time_9_30 = time(9, 30)
            self.wait_until_time(time_9_30, "9:30 AM")
            
            # Get first 15-minute candle (9:15-9:30 AM)
            print("\n--- Step 1: Analyzing First 15-Minute Candle (9:15-9:30 AM) ---")
            first_15min = self.utils.get_first_15min_candle(self.exchange)
            
            if not first_15min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 15-minute candle"
                }
            
            o = first_15min['open']
            h = first_15min['high']
            l = first_15min['low']
            c = first_15min['close']
            
            print(f"First 15-min Candle: O={o}, H={h}, L={l}, C={c}")
            
            # Get previous day high
            print("\n--- Getting Previous Day High ---")
            prev_day_high = self.get_previous_day_high()
            
            if prev_day_high is None:
                return {
                    "status": "error",
                    "error": "Unable to fetch previous day high"
                }
            
            print(f"Previous Day High: {prev_day_high}")
            print(f"First 15-min Open: {o}")
            
            # Check candle characteristics
            is_doji = self.is_doji_candle(first_15min)
            lower_wick_condition = self.check_lower_wick_condition(first_15min)
            is_green = c > o
            is_red = c < o
            
            print(f"\nCandle Analysis:")
            print(f"  - Is Doji: {is_doji}")
            print(f"  - Lower wick > 2 * upper wick: {lower_wick_condition}")
            print(f"  - Is Green: {is_green}")
            print(f"  - Is Red: {is_red}")
            
            # Determine which case applies and execute ONLY that case
            # Case 1: previous day high < open of first 15 minute candle
            if prev_day_high < o:
                print("\n=== CASE 1: Previous Day High < First Candle Open ===")
                return self.execute_case1(first_15min, is_doji, lower_wick_condition)
            
            # Case 2: previous day high > open of first 15 minute candle
            elif prev_day_high > o:
                print("\n=== CASE 2: Previous Day High > First Candle Open ===")
                return self.execute_case2(first_15min, is_doji, is_green, lower_wick_condition)
            
            # Case 3: Check if close < open and open - close > atr (when prev_day_high == o or as fallback)
            else:
                print("\n=== Checking CASE 3 Conditions ===")
                if is_red and (o - c) > self.atr:
                    print(f"CASE 3: Close < Open and (Open - Close) > ATR")
                    print(f"  - Open - Close = {o - c}")
                    print(f"  - ATR = {self.atr}")
                    return self.execute_case3(first_15min)
                else:
                    print("No case conditions met. Stopping strategy execution.")
                    return {
                        "status": "success",
                        "action": "no_trade",
                        "reason": "no_case_conditions_met",
                        "candle_data": first_15min
                    }
            
        except Exception as e:
            print(f"✗ Error executing strategy: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_case1(self, first_15min: Dict[str, float], is_doji: bool,
                      lower_wick_condition: bool) -> Dict[str, Any]:
        """
        Execute Case 1: previous day high < open of first 15 minute candle
        If doji and lower wick > 2 * upper wick, execute sell call spread immediately
        
        Args:
            first_15min: First 15-minute candle data
            is_doji: Whether candle is doji
            lower_wick_condition: Whether lower wick > 2 * upper wick
            
        Returns:
            Dictionary with execution results
        """
        print("\n--- Case 1: Checking Conditions ---")
        print(f"  - Is Doji: {is_doji}")
        print(f"  - Lower wick > 2 * upper wick: {lower_wick_condition}")
        
        # Check if it's past 12 PM
        current_time = datetime.now().time()
        time_12_00_pm = time(12, 0)
        
        if current_time >= time_12_00_pm:
            print("✗ Already past 12 PM. Stopping bot (12 PM cutoff).")
            return {
                "status": "success",
                "action": "no_trade",
                "case": "case1",
                "reason": "past_12pm_cutoff",
                "first_candle": first_15min
            }
        
        if is_doji and lower_wick_condition:
            print("✓ All conditions met! Executing sell call spread")
            
            # Get current spot price and calculate strike
            current_spot_price = self.utils.get_spot_price(self.exchange)
            current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
            
            # ATM - 2 * otm_points for call spread
            strike_price = current_atm_strike - (2 * self.otm_points)
            total_quantity = self.number_of_lots * self.lot_size
            
            print(f"\nTrade Details:")
            print(f"  - Current Spot Price: {current_spot_price}")
            print(f"  - Current ATM Strike: {current_atm_strike}")
            print(f"  - Strike Price (ATM - 2*OTM): {strike_price}")
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
                "trigger": "prev_day_high_below_open_doji_lower_wick",
                "strike": strike_price,
                "quantity": total_quantity,
                "spot_price": current_spot_price,
                "first_candle": first_15min,
                "order_response": order_response
            }
        else:
            print("✗ Conditions not met. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "case": "case1",
                "reason": "conditions_not_met",
                "is_doji": is_doji,
                "lower_wick_condition": lower_wick_condition,
                "first_candle": first_15min
            }
    
    def execute_case2(self, first_15min: Dict[str, float], is_doji: bool,
                      is_green: bool, lower_wick_condition: bool) -> Dict[str, Any]:
        """
        Execute Case 2: previous day high > open of first 15 minute candle
        If green doji and lower wick > 2 * upper wick, wait till 2 PM and watch for open + atr touch
        If no trade by 12 PM, stop bot
        
        Args:
            first_15min: First 15-minute candle data
            is_doji: Whether candle is doji
            is_green: Whether candle is green
            lower_wick_condition: Whether lower wick > 2 * upper wick
            
        Returns:
            Dictionary with execution results
        """
        print("\n--- Case 2: Checking Conditions ---")
        print(f"  - Is Green: {is_green}")
        print(f"  - Is Doji: {is_doji}")
        print(f"  - Lower wick > 2 * upper wick: {lower_wick_condition}")
        
        if is_green and is_doji and lower_wick_condition:
            print("✓ All conditions met! Monitoring spot price till 2 PM (with 12 PM cutoff)")
            
            # Calculate target level: open + atr
            target_level = first_15min['open'] + self.atr
            print(f"\nTarget Level (open + atr): {first_15min['open']} + {self.atr} = {target_level}")
            
            # Monitor till 12 PM first (cutoff time)
            time_12_00_pm = time(12, 0)
            time_2_00_pm = time(14, 0)
            
            print("\n--- Monitoring till 12 PM (cutoff time) ---")
            level_touched_by_12pm = self.monitor_spot_price_for_level_touch(target_level, time_12_00_pm, "open + atr")
            
            if level_touched_by_12pm:
                print("✓ Level touched before 12 PM! Executing sell call spread")
                
                # Get current spot price and calculate strike
                current_spot_price = self.utils.get_spot_price(self.exchange)
                current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
                
                # ATM - 2 * otm_points for call spread
                strike_price = current_atm_strike - (2 * self.otm_points)
                total_quantity = self.number_of_lots * self.lot_size
                
                print(f"\nTrade Details:")
                print(f"  - Current Spot Price: {current_spot_price}")
                print(f"  - Current ATM Strike: {current_atm_strike}")
                print(f"  - Strike Price (ATM - 2*OTM): {strike_price}")
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
                    "case": "case2",
                    "trigger": "green_doji_lower_wick_level_touched",
                    "strike": strike_price,
                    "quantity": total_quantity,
                    "spot_price": current_spot_price,
                    "target_level": target_level,
                    "first_candle": first_15min,
                    "order_response": order_response
                }
            else:
                print("✗ Level not touched by 12 PM. Stopping bot (12 PM cutoff).")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "case": "case2",
                    "reason": "no_trade_by_12pm_cutoff",
                    "target_level": target_level,
                    "first_candle": first_15min
                }
        else:
            print("✗ Conditions not met. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "case": "case2",
                "reason": "conditions_not_met",
                "is_green": is_green,
                "is_doji": is_doji,
                "lower_wick_condition": lower_wick_condition,
                "first_candle": first_15min
            }
    
    def execute_case3(self, first_15min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute Case 3: close < open and open - close > atr
        Watch which level spot price touches FIRST: open + atr OR close - 2*atr + 12.5
        Then execute TWO sequential trades based on which direction
        If no trade by 12 PM, stop bot
        
        Args:
            first_15min: First 15-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        print("\n--- Case 3: Monitoring Two Initial Levels ---")
        
        o = first_15min['open']
        c = first_15min['close']
        
        # Calculate initial two levels to watch FIRST
        level1_call = o + self.atr  # open + atr (for call spread direction)
        level2_put = c - (2 * self.atr) + 12.5  # close - 2*atr + 12.5 (for put spread direction)
        
        print(f"Level 1 (open + atr): {o} + {self.atr} = {level1_call}")
        print(f"Level 2 (close - 2*atr + 12.5): {c} - 2*{self.atr} + 12.5 = {level2_put}")
        
        # Monitor till 12 PM (cutoff time) to see which level is touched FIRST
        time_12_00_pm = time(12, 0)
        level_touched = self.monitor_spot_price_for_two_levels(level1_call, level2_put, time_12_00_pm)
        
        if level_touched == 'level1':
            print("✓ Level 1 (open + atr) touched! Executing FIRST sell call spread")
            
            # Get current spot price and calculate strike for FIRST trade
            current_spot_price = self.utils.get_spot_price(self.exchange)
            current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
            
            # Calculate quantity for half lots
            half_quantity = int((self.number_of_lots / 2) * self.lot_size)
            
            print(f"\nTrade 1 Details (ATM - 1*OTM):")
            print(f"  - Current Spot Price: {current_spot_price}")
            print(f"  - Current ATM Strike: {current_atm_strike}")
            
            # Trade 1: ATM - 1 * otm_points (fetch atm strike - take 1 * otm_points)
            strike_price_1 = current_atm_strike - (1 * self.otm_points)
            print(f"  - Strike Price (ATM - 1*OTM): {strike_price_1}")
            print(f"  - Quantity: {half_quantity} (half lots)")
            print(f"  - Expiry: {self.expiry_to_trade}")
            
            order_response_1 = self.utils.place_call_spread(
                strike_price=strike_price_1,
                quantity=half_quantity,
                exchange=self.exchange,
                trading_symbol=self.trading_symbol,
                expiry=self.expiry_to_trade,
                spread_gap=self.spread_gap
            )
            
            # Now monitor for SECOND level: open + 2*atr
            level1_second = o + (2 * self.atr)
            print(f"\n--- Monitoring for Second Level (open + 2*atr): {level1_second} ---")
            
            level_touched_second = self.monitor_spot_price_for_level_touch(level1_second, time_12_00_pm, "open + 2*atr")
            
            if level_touched_second:
                print("✓ Second level (open + 2*atr) touched! Executing SECOND sell call spread")
                
                # Get current spot price and calculate strike for SECOND trade
                current_spot_price_2 = self.utils.get_spot_price(self.exchange)
                current_atm_strike_2 = self.utils.get_atm_strike(current_spot_price_2, self.exchange)
                
                print(f"\nTrade 2 Details (ATM - 2*OTM):")
                print(f"  - Current Spot Price: {current_spot_price_2}")
                print(f"  - Current ATM Strike: {current_atm_strike_2}")
                
                # Trade 2: ATM - 2 * otm_points (fetch atm strike - take 2 * otm_points)
                strike_price_2 = current_atm_strike_2 - (2 * self.otm_points)
                print(f"  - Strike Price (ATM - 2*OTM): {strike_price_2}")
                print(f"  - Quantity: {half_quantity} (half lots)")
                print(f"  - Expiry: {self.expiry_to_trade}")
                
                order_response_2 = self.utils.place_call_spread(
                    strike_price=strike_price_2,
                    quantity=half_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry_to_trade,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "two_call_spreads_placed",
                    "case": "case3",
                    "trigger": "both_call_levels_touched",
                    "trade1": {
                        "strike": strike_price_1,
                        "quantity": half_quantity,
                        "order_response": order_response_1
                    },
                    "trade2": {
                        "strike": strike_price_2,
                        "quantity": half_quantity,
                        "order_response": order_response_2
                    },
                    "spot_price": current_spot_price,
                    "level1_call": level1_call,
                    "level1_second": level1_second,
                    "first_candle": first_15min
                }
            else:
                print("✗ Second level not touched by 12 PM. Only first trade executed.")
                return {
                    "status": "success",
                    "action": "one_call_spread_placed",
                    "case": "case3",
                    "trigger": "only_first_call_level_touched",
                    "trade1": {
                        "strike": strike_price_1,
                        "quantity": half_quantity,
                        "order_response": order_response_1
                    },
                    "spot_price": current_spot_price,
                    "level1_call": level1_call,
                    "level1_second": level1_second,
                    "first_candle": first_15min
                }
        
        elif level_touched == 'level2':
            print("✓ Level 2 (close - 2*atr + 12.5) touched! Executing FIRST sell put spread")
            
            # Get current spot price and calculate strike for FIRST trade
            current_spot_price = self.utils.get_spot_price(self.exchange)
            current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
            
            # Calculate quantity for half lots
            half_quantity = int((self.number_of_lots / 2) * self.lot_size)
            
            print(f"\nTrade 1 Details (ATM + 1*OTM):")
            print(f"  - Current Spot Price: {current_spot_price}")
            print(f"  - Current ATM Strike: {current_atm_strike}")
            
            # Trade 1: ATM + 1 * otm_points (fetch atm strike + take 1 * otm_points)
            strike_price_1 = current_atm_strike + (1 * self.otm_points)
            print(f"  - Strike Price (ATM + 1*OTM): {strike_price_1}")
            print(f"  - Quantity: {half_quantity} (half lots)")
            print(f"  - Expiry: {self.expiry_to_trade}")
            
            order_response_1 = self.utils.place_put_spread(
                strike_price=strike_price_1,
                quantity=half_quantity,
                exchange=self.exchange,
                trading_symbol=self.trading_symbol,
                expiry=self.expiry_to_trade,
                spread_gap=self.spread_gap
            )
            
            # Now monitor for SECOND level: close - atr + 12.5
            # Note: First level was close - 2*atr + 12.5, second level is close - atr + 12.5 (less extreme)
            level2_second = c - self.atr + 12.5
            print(f"\n--- Monitoring for Second Level (close - atr + 12.5): {level2_second} ---")
            
            level_touched_second = self.monitor_spot_price_for_level_touch(level2_second, time_12_00_pm, "close - atr + 12.5", "downward")
            
            if level_touched_second:
                print("✓ Second level (close - atr + 12.5) touched! Executing SECOND sell put spread")
                
                # Get current spot price and calculate strike for SECOND trade
                current_spot_price_2 = self.utils.get_spot_price(self.exchange)
                current_atm_strike_2 = self.utils.get_atm_strike(current_spot_price_2, self.exchange)
                
                print(f"\nTrade 2 Details (ATM + 2*OTM):")
                print(f"  - Current Spot Price: {current_spot_price_2}")
                print(f"  - Current ATM Strike: {current_atm_strike_2}")
                
                # Trade 2: ATM + 2 * otm_points (fetch atm strike + take 2 * otm_points)
                strike_price_2 = current_atm_strike_2 + (2 * self.otm_points)
                print(f"  - Strike Price (ATM + 2*OTM): {strike_price_2}")
                print(f"  - Quantity: {half_quantity} (half lots)")
                print(f"  - Expiry: {self.expiry_to_trade}")
                
                order_response_2 = self.utils.place_put_spread(
                    strike_price=strike_price_2,
                    quantity=half_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry_to_trade,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "two_put_spreads_placed",
                    "case": "case3",
                    "trigger": "both_put_levels_touched",
                    "trade1": {
                        "strike": strike_price_1,
                        "quantity": half_quantity,
                        "order_response": order_response_1
                    },
                    "trade2": {
                        "strike": strike_price_2,
                        "quantity": half_quantity,
                        "order_response": order_response_2
                    },
                    "spot_price": current_spot_price,
                    "level2_put": level2_put,
                    "level2_second": level2_second,
                    "first_candle": first_15min
                }
            else:
                print("✗ Second level not touched by 12 PM. Only first trade executed.")
                return {
                    "status": "success",
                    "action": "one_put_spread_placed",
                    "case": "case3",
                    "trigger": "only_first_put_level_touched",
                    "trade1": {
                        "strike": strike_price_1,
                        "quantity": half_quantity,
                        "order_response": order_response_1
                    },
                    "spot_price": current_spot_price,
                    "level2_put": level2_put,
                    "level2_second": level2_second,
                    "first_candle": first_15min
                }
        
        else:
            print("✗ Neither level touched by 12 PM. Stopping bot (12 PM cutoff).")
            return {
                "status": "success",
                "action": "no_trade",
                "case": "case3",
                "reason": "no_trade_by_12pm_cutoff",
                "level1_call": level1_call,
                "level2_put": level2_put,
                "first_candle": first_15min
            }
