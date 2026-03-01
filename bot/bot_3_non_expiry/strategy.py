"""
Bot 3 Non-Expiry Strategy Implementation
This strategy implements a complex trading logic based on first 15-minute candle analysis
"""

from typing import Dict, Any, Optional
from growwapi import GrowwAPI
from bot.utils import Utils
from datetime import datetime, time
import time as time_module


class Bot3Strategy:
    """
    Bot 3 Strategy Class
    Implements the trading logic for bot_3_non_expiry strategy
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
        self.expiry_to_check = config.get('expiry_to_check')
        self.spread_gap = int(config.get('spread_gap', 200))
        self.exchange = config.get('exchange', 'NSE')
        self.trading_symbol = config.get('trading_symbol', 'NIFTY')
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        self.otm_points = int(config.get('otm_points', 50))
        self.atr = float(config.get('atr', 45))
        
        print(f"Bot3Strategy initialized with:")
        print(f"  - Expiry to Trade: {self.expiry_to_trade}")
        print(f"  - Expiry to Check: {self.expiry_to_check}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - OTM Points: {self.otm_points}")
        print(f"  - ATR: {self.atr}")
    
    def is_red_bald_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if candle is red and it's a bald candle
        Condition: close < open AND abs((open - close) / open) > 0.001
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            
        Returns:
            bool: True if red bald candle, False otherwise
        """
        o = candle['open']
        c = candle['close']
        
        if o == 0:
            return False
        
        # Check if candle is red (close < open)
        if c >= o:
            return False
        
        # Check if it's a bald candle: abs((open - close) / open) > 0.001
        percentage_change = (o - c) / o
        return percentage_change > 0.001
    
    def is_green_bald_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if candle is green and it's a bald candle
        Condition: close > open AND (close - open) / close > 0.001
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            
        Returns:
            bool: True if green bald candle, False otherwise
        """
        o = candle['open']
        c = candle['close']
        
        if o == 0:
            return False
        
        # Check if candle is green (close > open)
        if c <= o:
            return False
        
        # Check if it's a bald candle: (close - open) / close > 0.001
        percentage_change = (c - o) / c
        return percentage_change > 0.001
    
    def is_doji_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if a candle is a doji candle
        Doji can be either:
        - Red candle: (abs(open - close) / open < 0.001) and ((open - close) < (high - open + close - low)) and (high - open) > (close - low)
        - Green candle: (abs(close - open) / close < 0.001) and ((close - open) < (high - close + open - low))
        
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
        
        # Check for red candle doji: close < open
        if c < o:
            body_percentage = abs(o - c) / o
            condition_1 = body_percentage < 0.001
            
            body_size = o - c
            upper_wick = h - o
            lower_wick = c - l
            condition_2 = body_size < (upper_wick + lower_wick)
            condition_3 = upper_wick > lower_wick
            
            if condition_1 and condition_2 and condition_3:
                return True
        
        # Check for green candle doji: open < close
        if o < c:
            body_percentage = abs(c - o) / c
            condition_1 = body_percentage < 0.001
            
            body_size = c - o
            upper_wick = h - c
            lower_wick = o - l
            condition_2 = body_size < (upper_wick + lower_wick)
            
            if condition_1 and condition_2:
                return True
        
        return False
    
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
    
    def monitor_spot_price_for_level_touch(self, target_level: float, end_time: time) -> bool:
        """
        Monitor spot price to check if it touches the target level until end_time
        
        Args:
            target_level: Target price level to check against
            end_time: Time to stop monitoring (e.g., 11:00 AM)
            
        Returns:
            bool: True if level touched, False otherwise
        """
        print(f"\n--- Monitoring Spot Price for Level Touch (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"Target Level X: {target_level}")
        
        while datetime.now().time() < end_time:
            # Check spot price every 30 seconds
            current_spot_price = self.utils.get_spot_price(self.exchange)
            
            if not current_spot_price:
                print("Unable to fetch spot price, retrying...")
                time_module.sleep(30)
                continue
            
            current_time = datetime.now().time()
            print(f"[{current_time.strftime('%H:%M:%S')}] Current Spot Price: {current_spot_price}")
            
            # Check if spot price touches or goes below the target level
            if current_spot_price <= target_level:
                print(f"✓ Spot price touched level X! (Spot: {current_spot_price} <= Level: {target_level})")
                return True
            else:
                print(f"✗ Level not touched yet (Spot: {current_spot_price} > Level: {target_level})")
            
            # Check if we've passed the end time
            if datetime.now().time() >= end_time:
                print(f"Reached end time {end_time.strftime('%H:%M:%S')} without level touch")
                break
            
            # Wait 30 seconds before next check
            time_module.sleep(2)
        
        return False
    
    def monitor_option_for_ema_touch(self, option_symbol: str, ema_high: float, end_time: time, stop_level: Optional[float] = None) -> Dict[str, Any]:
        """
        Monitor option 15-minute candles for EMA 33 high touch until end_time
        Also checks if spot price touches stop level (if provided)
        
        Args:
            option_symbol: Option trading symbol to monitor
            ema_high: EMA 33 high value to check against
            end_time: Time to stop monitoring (e.g., 12:00 PM)
            stop_level: Optional stop level - if spot price touches this, stop monitoring
            
        Returns:
            Dictionary with 'ema_touched' (bool) and 'stop_hit' (bool)
        """
        print(f"\n--- Monitoring Option {option_symbol} for EMA 33 Touch (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"EMA 33 High: {ema_high}")
        if stop_level:
            print(f"Stop Level: {stop_level} (will stop if spot price touches this level)")
        
        while datetime.now().time() < end_time:
            # Check stop level first if provided
            if stop_level:
                current_spot_price = self.utils.get_spot_price(self.exchange)
                if current_spot_price and current_spot_price <= stop_level:
                    print(f"\n✗ Stop level hit! Spot price {current_spot_price} <= Stop level {stop_level}")
                    print("Stopping trade monitoring - no trade will be placed")
                    return {"ema_touched": False, "stop_hit": True}
            
            # Wait for next 15-minute candle completion
            current_time = datetime.now()
            current_minute = current_time.minute
            
            # Calculate next 15-minute mark
            next_15min_mark = ((current_minute // 15) + 1) * 15
            if next_15min_mark >= 60:
                next_15min_mark = 0
                wait_time = (60 - current_minute) * 60 - current_time.second
            else:
                wait_time = (next_15min_mark - current_minute) * 60 - current_time.second
            
            if wait_time > 0:
                print(f"Waiting {wait_time:.0f} seconds for next 15-min option candle...")
                time_module.sleep(wait_time + 5)  # Add 5 seconds buffer
            
            # Check if we've passed the end time
            if datetime.now().time() >= end_time:
                print(f"Reached end time {end_time.strftime('%H:%M:%S')} without EMA touch")
                break
            
            # Get latest option 15-minute candle
            candle = self.utils.get_option_15min_candle(option_symbol, self.exchange)
            
            if not candle:
                print("Unable to fetch option 15-min candle, retrying...")
                continue
            
            print(f"\nOption candle: O={candle['open']}, H={candle['high']}, L={candle['low']}, C={candle['close']}")
            
            # Check if candle touches EMA 33 high
            if candle['high'] >= ema_high:
                print(f"✓ Option candle touched EMA 33 high! (High: {candle['high']} >= EMA: {ema_high})")
                return {"ema_touched": True, "stop_hit": False}
            else:
                print(f"✗ No EMA touch yet (High: {candle['high']} < EMA: {ema_high})")
        
        return {"ema_touched": False, "stop_hit": False}
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the bot_3_non_expiry strategy
        
        Strategy Logic:
        Step 1: Wait until 9:30 AM and capture OHLC data of first 15-minute candle (9:15-9:30 AM)
        Step 2: Check if candle is red and it's a bald candle: (open - close) / open > 0.001
        Step 3: If red bald candle, calculate X = close - 2*ATR + 12.5
        Step 4: Place put spread if spot price touches level X and wait till 11 AM, if doesn't get trade till 11 AM, stop execution
        Step 5: If not red bald candle, check if it's a green bald candle (close - open) / close > .001 or doji candle (either):
                - Red candle: (abs(open - close) / open < 0.001) and ((open - close) < (high - open + close - low)) and (high - open) > (close - low)
                - Green candle: (abs(close - open) / close < 0.001) and ((close - open) < (high - close + open - low))
        Step 6: Get 15-min candle OHLC of expiry_to_check OTM call option (ATM + otm_points)
                based on spot price (15-min candle closing price) - 9:15-9:30 AM candle specifically
        Step 7: Get EMA 33 OHLC of expiry_to_check OTM call option strike
        Step 8: First 15-min option close should be < EMA 33 low, if not stop trade execution
        Step 9: Monitor 15-min candles of options with EMA 33 applied till 12 PM
        Step 10: Enter trade when 15-min option candle touches EMA 33 high, sell call spread
                 at ITM (ATM + itm_points) based on spot price at that time with expiry_to_trade, if spot price have touched
                 (closing price of first 15 minute candle of spot price - 2*ATR + 12.5) then stop trade, don't take any trade
        Step 11: If first 15-min candle is neither bald nor doji, stop strategy execution
        
        Returns:
            Dictionary with execution results
        """
        try:
            print("\n=== Executing Bot 3 Non-Expiry Strategy ===")
            
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
            
            # Step 2: Check if candle is red and it's a bald candle
            print("\n--- Step 2: Checking Red Bald Candle Condition ---")
            is_red_bald = self.is_red_bald_candle(first_15min)
            
            percentage_change = (o - c) / o if o != 0 else 0
            is_red = c < o
            print(f"Is Red Candle (close < open): {is_red}")
            print(f"Bald Candle Check: (open - close) / open = {percentage_change:.6f}")
            print(f"Is Red Bald Candle (> 0.001): {is_red_bald}")
            
            if is_red_bald:
                # Step 3-4: Execute red bald candle strategy
                return self.execute_red_bald_candle_strategy(first_15min)
            
            # Step 5: Check if it's a green bald candle or doji candle
            print("\n--- Step 5: Checking Green Bald Candle or Doji Candle Condition ---")
            is_green_bald = self.is_green_bald_candle(first_15min)
            is_doji = self.is_doji_candle(first_15min)
            
            green_percentage_change = (c - o) / c if c != 0 else 0
            is_green = c > o
            print(f"Is Green Candle (close > open): {is_green}")
            print(f"Green Bald Candle Check: (close - open) / close = {green_percentage_change:.6f}")
            print(f"Is Green Bald Candle (> 0.001): {is_green_bald}")
            
            body_percentage = abs(c - o) / c if c != 0 else 0
            body_size = abs(c - o)
            upper_wick = h - max(o, c)
            lower_wick = min(o, c) - l
            total_wick = upper_wick + lower_wick
            
            print(f"\nDoji Candle Check:")
            print(f"  - Body percentage: {body_percentage:.6f} (should be < 0.001)")
            print(f"  - Body size: {body_size:.2f}")
            print(f"  - Total wick: {total_wick:.2f}")
            print(f"  - Body < Wick: {body_size < total_wick}")
            print(f"Is Doji Candle: {is_doji}")
            
            if is_green_bald or is_doji:
                # Execute green bald or doji candle strategy
                return self.execute_doji_candle_strategy(first_15min)
            
            # Step 11: Neither red bald, green bald, nor doji - stop execution
            print("\n--- Step 11: First candle is neither red bald, green bald, nor doji ---")
            print("✗ No trade conditions met. Stopping strategy execution.")
            
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "first_candle_no_conditions_met",
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
    
    def execute_red_bald_candle_strategy(self, first_15min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute strategy when first candle is a red bald candle
        
        Step 3: Calculate X = close - 2*ATR + 12.5
        Step 4: Place put spread if spot price touches level X and wait till 11 AM,
                if doesn't get trade till 11 AM, stop execution
        
        Args:
            first_15min: First 15-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        print("\n=== Executing Red Bald Candle Strategy ===")
        
        # Step 3: Calculate X = close - 2*ATR + 12.5
        print("\n--- Step 3: Calculating Target Level X ---")
        first_close = first_15min['close']
        target_level_x = first_close - (2 * self.atr) + 12.5
        
        print(f"First 15-min Candle Close: {first_close}")
        print(f"ATR from config: {self.atr}")
        print(f"Target Level X = close - 2*ATR + 12.5")
        print(f"Target Level X = {first_close} - 2*{self.atr} + 12.5 = {target_level_x}")
        
        # Step 4: Monitor spot price for level touch until 11 AM
        print("\n--- Step 4: Monitoring Spot Price for Level Touch (till 11 AM) ---")
        time_11_00 = time(11, 0)
        
        level_touched = self.monitor_spot_price_for_level_touch(target_level_x, time_11_00)
        
        if not level_touched:
            print("\n✗ Spot price did not touch level X before 11:00 AM. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "level_not_touched_before_11am",
                "target_level_x": target_level_x,
                "first_candle": first_15min
            }
        
        # Level touched - place put spread at ITM
        print("\n✓ Level touched! Placing Put Spread at ITM")
        
        # Get current spot price and calculate ITM strike for put spread
        current_spot_price = self.utils.get_spot_price(self.exchange)
        current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
        current_itm_strike = current_atm_strike - self.itm_points  # ITM for put is ATM - points
        total_quantity = self.number_of_lots * self.lot_size
        
        print(f"Current Spot Price: {current_spot_price}")
        print(f"Current ATM Strike: {current_atm_strike}")
        print(f"Current ITM Strike (Put): {current_itm_strike}")
        print(f"Quantity: {total_quantity}")
        print(f"Expiry to Trade: {self.expiry_to_trade}")
        
        # Place put spread at ITM
        order_response = self.utils.place_put_spread(
            strike_price=current_itm_strike,
            quantity=total_quantity,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_trade,
            spread_gap=self.spread_gap
        )
        
        return {
            "status": "success",
            "action": "put_spread_placed",
            "trigger": "red_bald_candle_level_touch",
            "strike": current_itm_strike,
            "quantity": total_quantity,
            "spot_price": current_spot_price,
            "target_level_x": target_level_x,
            "first_candle": first_15min,
            "order_response": order_response
        }
    
    def execute_doji_candle_strategy(self, first_15min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute strategy when first candle is a doji candle
        
        Steps:
        6. Get 15-minute candle OHLC of expiry_to_check OTM call option strike (ATM + otm_points)
           based on the spot price (15-minute candle closing price) - specifically 9:15-9:30 AM candle
        7. Get EMA 33 OHLC of expiry_to_check OTM call option strike based on the spot price
        8. First 15-minute option closing price (from step 6) should be less than EMA 33 low
           of options chart (from step 7), if not stop trade execution
        9. Monitor 15-minute candles of options expiry_to_check OTM call option strike and
           observe the option chart on a 15-minute timeframe with EMA 33 applied till 12 PM
        10. Enter the trade when the 15-minute option candle touches EMA 33 high, and sell a
            call spread at ITM (ATM + itm_points) based on spot price at that time with expiry_to_trade,
            if spot price have touched (closing price of first 15 minute candle of spot price - 2*ATR + 12.5)
            then stop trade, don't take any trade
        
        Args:
            first_15min: First 15-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        print("\n=== Executing Doji Candle Strategy ===")
        
        # Calculate stop level: first 15-min close - 2*ATR + 12.5
        first_close = first_15min['close']
        stop_level = first_close - (2 * self.atr) + 12.5
        print(f"\nStop Level Calculated: {first_close} - 2*{self.atr} + 12.5 = {stop_level}")
        print(f"If spot price touches {stop_level}, no trade will be placed")
        
        # Step 6: Get 15-minute candle OHLC of expiry_to_check OTM call option strike
        # based on the spot price (15-minute candle closing price) - 9:15-9:30 AM candle
        print("\n--- Step 6: Getting First 15-Min Option Candle (9:15-9:30 AM) ---")
        spot_price = first_15min['close']  # Use first 15-min closing price as spot
        atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
        otm_strike = atm_strike + self.otm_points
        
        option_symbol = self.utils.get_option_strike_symbol(
            spot_price=spot_price,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_check,
            option_type='CE',
            otm_points=self.otm_points
        )
        
        print(f"Spot Price (15-min close): {spot_price}")
        print(f"ATM Strike: {atm_strike}")
        print(f"OTM Strike: {otm_strike}")
        print(f"Option Symbol: {option_symbol}")
        
        # Get first 15-min option candle (9:15-9:30 AM) for the OTM call option
        option_candle = self.utils.get_first_option_15min_candle(option_symbol, self.exchange)
        
        if not option_candle:
            return {
                "status": "error",
                "error": f"Unable to fetch first 15-min option candle (9:15-9:30 AM) for {option_symbol}"
            }
        
        option_close = option_candle['close']
        print(f"First 15-min Option Close (9:15-9:30 AM): {option_close}")
        
        # Step 7: Get EMA 33 OHLC of expiry_to_check OTM call option strike
        print("\n--- Step 7: Calculating EMA 33 OHLC for Option Chart ---")
        ema_data = self.utils.get_option_ema_33_15min(option_symbol, self.exchange)
        
        if not ema_data:
            return {
                "status": "error",
                "error": f"Unable to calculate EMA 33 for option {option_symbol}"
            }
        
        ema_low = ema_data['ema_low']
        ema_high = ema_data['ema_high']
        
        print(f"EMA 33 Low: {ema_low}")
        print(f"EMA 33 High: {ema_high}")
        print(f"Candles used for EMA: {ema_data['candles_used']}")
        
        # Step 8: First 15-minute option closing price should be less than EMA 33 low
        print("\n--- Step 8: Validating Option Close < EMA 33 Low ---")
        print(f"First 15-min Option Close ({option_close}) < EMA 33 Low ({ema_low}): {option_close < ema_low}")
        
        if option_close >= ema_low:
            print("✗ First 15-min option close is NOT below EMA 33 low. Stopping trade execution.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "option_close_not_below_ema_low",
                "option_symbol": option_symbol,
                "option_close": option_close,
                "ema_low": ema_low,
                "first_candle": first_15min
            }
        
        print("✓ First 15-min option close is below EMA 33 low. Proceeding to monitor...")
        
        # Step 9: Monitor 15-minute candles of options and observe with EMA 33 till 12 PM
        # Also monitor spot price for stop level
        print("\n--- Step 9: Monitoring Option Candles for EMA 33 High Touch (till 12 PM) ---")
        time_12_00 = time(12, 0)
        
        monitor_result = self.monitor_option_for_ema_touch(option_symbol, ema_high, time_12_00, stop_level)
        
        # Check if stop level was hit
        if monitor_result["stop_hit"]:
            print("\n✗ Stop level hit! No trade will be placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "stop_level_hit",
                "option_symbol": option_symbol,
                "stop_level": stop_level,
                "first_candle": first_15min
            }
        
        # Check if EMA was touched
        if not monitor_result["ema_touched"]:
            print("\n✗ Option did not touch EMA 33 high before 12:00 PM. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "no_ema_touch_before_12pm",
                "option_symbol": option_symbol,
                "ema_high": ema_high,
                "first_candle": first_15min
            }
        
        # Step 10: Enter trade when 15-minute option candle touches EMA 33 high
        # Sell call spread with strike price of spot chart at that time with expiry_to_trade
        print("\n--- Step 10: Placing Call Spread at ITM (EMA Touch Detected) ---")
        
        # Get current spot price at time of entry and calculate ITM strike
        current_spot_price = self.utils.get_spot_price(self.exchange)
        current_atm_strike = self.utils.get_atm_strike(current_spot_price, self.exchange)
        current_itm_strike = current_atm_strike + self.itm_points
        total_quantity = self.number_of_lots * self.lot_size
        
        print(f"Current Spot Price: {current_spot_price}")
        print(f"Current ATM Strike: {current_atm_strike}")
        print(f"Current ITM Strike: {current_itm_strike}")
        print(f"Quantity: {total_quantity}")
        print(f"Expiry to Trade: {self.expiry_to_trade}")
        
        # Place call spread at ITM with strike price based on current spot chart
        order_response = self.utils.place_call_spread(
            strike_price=current_itm_strike,
            quantity=total_quantity,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_trade,
            spread_gap=self.spread_gap
        )
        
        return {
            "status": "success",
            "action": "call_spread_placed",
            "trigger": "doji_candle_ema_touch",
            "strike": current_itm_strike,
            "quantity": total_quantity,
            "spot_price": current_spot_price,
            "option_symbol_monitored": option_symbol,
            "ema_high": ema_high,
            "stop_level": stop_level,
            "first_candle": first_15min,
            "order_response": order_response
        }
