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
    
    def is_bald_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if a candle is a bald candle
        Condition: abs(close - open) / open > 0.001
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            
        Returns:
            bool: True if bald candle, False otherwise
        """
        o = candle['open']
        c = candle['close']
        
        if o == 0:
            return False
        
        percentage_change = abs(c - o) / o
        return percentage_change > 0.001
    
    def is_doji_candle(self, candle: Dict[str, float]) -> bool:
        """
        Check if a candle is a doji candle
        Doji can be either:
        - Red candle: (abs(close - open) / close < 0.001) and ((close - open) < (high - close + open - low))
        - Green candle: (abs(open - close) / open < 0.001) and ((open - close) < (high - open + close - low))
        
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
            body_percentage = abs(c - o) / c
            condition_1 = body_percentage < 0.001
            
            body_size = c - o
            upper_wick = h - c
            lower_wick = o - l
            condition_2 = body_size < (upper_wick + lower_wick)
            
            if condition_1 and condition_2:
                return True
        
        # Check for green candle doji: open < close
        if o < c:
            body_percentage = abs(o - c) / o
            condition_1 = body_percentage < 0.001
            
            body_size = o - c
            upper_wick = h - o
            lower_wick = c - l
            condition_2 = body_size < (upper_wick + lower_wick)
            
            if condition_1 and condition_2:
                return True
        
        return False
    
    def is_strong_red_candle(self, candle: Dict[str, float], reference_level: float) -> bool:
        """
        Check if a candle is a strong red candle that closes below reference level X
        Conditions:
        1. Candle is bearish: open > close
        2. Real body > total wick length: (open - close) > (high - open + close - low)
        3. Candle closes below level X
        
        Args:
            candle: Candle dict with 'open', 'high', 'low', 'close' keys
            reference_level: Reference level X to compare against
            
        Returns:
            bool: True if strong red candle meeting all conditions
        """
        o = candle['open']
        h = candle['high']
        l = candle['low']
        c = candle['close']
        
        # Condition 1: Bearish candle
        is_bearish = o > c
        
        # Condition 2: Real body > total wick length
        real_body = o - c
        upper_wick = h - o
        lower_wick = c - l
        total_wick = upper_wick + lower_wick
        body_larger_than_wick = real_body > total_wick
        
        # Condition 3: Closes below reference level
        closes_below_x = c < reference_level
        
        return is_bearish and body_larger_than_wick and closes_below_x
    
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
    
    def monitor_for_strong_red_candle(self, reference_level: float, end_time: time) -> Optional[Dict[str, float]]:
        """
        Monitor 15-minute candles for a strong red candle until end_time
        
        Args:
            reference_level: Reference level X to check against
            end_time: Time to stop monitoring (e.g., 12:00 PM)
            
        Returns:
            Candle dict if strong red candle found, None otherwise
        """
        print(f"\n--- Monitoring for Strong Red Candle (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"Reference Level X: {reference_level}")
        
        while datetime.now().time() < end_time:
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
                print(f"Waiting {wait_time:.0f} seconds for next 15-min candle...")
                time_module.sleep(wait_time + 5)  # Add 5 seconds buffer
            
            # Check if we've passed the end time
            if datetime.now().time() >= end_time:
                print(f"Reached end time {end_time.strftime('%H:%M:%S')} without finding strong red candle")
                break
            
            # Get latest 15-minute candle
            candle = self.utils.get_15min_candle(self.exchange)
            
            if not candle:
                print("Unable to fetch 15-min candle, retrying...")
                continue
            
            print(f"\nAnalyzing candle: O={candle['open']}, H={candle['high']}, L={candle['low']}, C={candle['close']}")
            
            # Check if it's a strong red candle
            if self.is_strong_red_candle(candle, reference_level):
                print("✓ Strong red candle found!")
                return candle
            else:
                print("✗ Not a strong red candle, continuing to monitor...")
        
        return None
    
    def monitor_option_for_ema_touch(self, option_symbol: str, ema_high: float, end_time: time) -> bool:
        """
        Monitor option 15-minute candles for EMA 33 high touch until end_time
        
        Args:
            option_symbol: Option trading symbol to monitor
            ema_high: EMA 33 high value to check against
            end_time: Time to stop monitoring (e.g., 12:00 PM)
            
        Returns:
            bool: True if EMA touch detected, False otherwise
        """
        print(f"\n--- Monitoring Option {option_symbol} for EMA 33 Touch (until {end_time.strftime('%H:%M:%S')}) ---")
        print(f"EMA 33 High: {ema_high}")
        
        while datetime.now().time() < end_time:
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
                return True
            else:
                print(f"✗ No EMA touch yet (High: {candle['high']} < EMA: {ema_high})")
        
        return False
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the bot_3_non_expiry strategy
        
        Strategy Logic:
        Step 1: Wait until 9:30 AM and capture OHLC data of first 15-minute candle (9:15-9:30 AM)
        Step 2: Check if it's a bald candle: abs(close - open) / open > 0.001
        Step 3: If bald candle, calculate reference level X = (15-min close + high) / 2
        Step 4: Monitor subsequent 15-minute candles for strong red candle that:
                - Is bearish (open > close)
                - Real body > total wick: (open - close) > (high - open + close - low)
                - Closes below level X
        Step 5: When Step 4 conditions met, place call spread at ITM (ATM + itm_points).
                Monitor till 12:00 PM only.
        Step 6: If not bald candle, check if it's a doji candle (either):
                - Red candle: (abs(close - open) / close < 0.001) and ((close - open) < (high - close + open - low))
                - Green candle: (abs(open - close) / open < 0.001) and ((open - close) < (high - open + close - low))
        Step 7: Get 15-min candle OHLC of expiry_to_check OTM call option (ATM + otm_points)
                based on spot price (15-min candle closing price) - 9:15-9:30 AM candle specifically
        Step 8: Get EMA 33 OHLC of expiry_to_check OTM call option strike
        Step 9: First 15-min option close should be < EMA 33 low, if not stop trade execution
        Step 10: Monitor 15-min candles of options with EMA 33 applied till 12 PM
        Step 11: Enter trade when 15-min option candle touches EMA 33 high, sell call spread
                 at ITM (ATM + itm_points) based on spot price at that time with expiry_to_trade
        Step 12: If first 15-min candle is neither bald nor doji, stop strategy execution
        
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
            
            # Step 2: Check if it's a bald candle
            print("\n--- Step 2: Checking Bald Candle Condition ---")
            is_bald = self.is_bald_candle(first_15min)
            
            percentage_change = abs(c - o) / o if o != 0 else 0
            print(f"Bald Candle Check: abs(close - open) / open = {percentage_change:.6f}")
            print(f"Is Bald Candle (> 0.001): {is_bald}")
            
            if is_bald:
                # Step 3: Calculate reference level X and monitor for strong red candle
                return self.execute_bald_candle_strategy(first_15min)
            
            # Step 6: Check if it's a doji candle
            print("\n--- Step 6: Checking Doji Candle Condition ---")
            is_doji = self.is_doji_candle(first_15min)
            
            body_percentage = abs(c - o) / c if c != 0 else 0
            body_size = abs(c - o)
            upper_wick = h - max(o, c)
            lower_wick = min(o, c) - l
            total_wick = upper_wick + lower_wick
            
            print(f"Doji Candle Check:")
            print(f"  - Body percentage: {body_percentage:.6f} (should be < 0.001)")
            print(f"  - Body size: {body_size:.2f}")
            print(f"  - Total wick: {total_wick:.2f}")
            print(f"  - Body < Wick: {body_size < total_wick}")
            print(f"Is Doji Candle: {is_doji}")
            
            if is_doji:
                # Execute doji candle strategy
                return self.execute_doji_candle_strategy(first_15min)
            
            # Step 12: Neither bald nor doji - stop execution
            print("\n--- Step 12: First candle is neither bald nor doji ---")
            print("✗ No trade conditions met. Stopping strategy execution.")
            
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "first_candle_neither_bald_nor_doji",
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
    
    def execute_bald_candle_strategy(self, first_15min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute strategy when first candle is a bald candle
        
        Step 3: Calculate reference level X = (15-minute close + high) / 2
        Step 4: After 9:30 AM, monitor subsequent 15-minute candles and wait for strong red candle where:
                - Candle is bearish (open > close)
                - Real body > total wick: (open - close) > (high - open + close - low)
                - Candle closes below level X
        Step 5: When all conditions in Step 4 are met, place call spread at ITM and wait for
                Step 4 to be satisfied till 12:00 PM (monitor 15-min candles till 12 PM only)
        
        Args:
            first_15min: First 15-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        print("\n=== Executing Bald Candle Strategy ===")
        
        # Step 3: Calculate reference level X = (15-minute close + high) / 2
        c = first_15min['close']
        h = first_15min['high']
        reference_level_x = (c + h) / 2
        
        print(f"--- Step 3: Calculate Reference Level X ---")
        print(f"X = (15-min close + high) / 2 = ({c} + {h}) / 2 = {reference_level_x}")
        
        # Step 4: After 9:30 AM, monitor subsequent 15-minute candles for strong red candle
        print("\n--- Step 4: Monitoring Subsequent 15-Minute Candles for Strong Red Candle ---")
        time_12_00 = time(12, 0)
        
        strong_red_candle = self.monitor_for_strong_red_candle(reference_level_x, time_12_00)
        
        if not strong_red_candle:
            print("\n✗ No strong red candle found before 12:00 PM. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "no_strong_red_candle_before_12pm",
                "reference_level_x": reference_level_x,
                "first_candle": first_15min
            }
        
        # Step 5: Place call spread at ITM
        print("\n--- Step 5: Placing Call Spread at ITM ---")
        
        # Get current spot price and calculate ITM strike
        spot_price = self.utils.get_spot_price(self.exchange)
        atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
        itm_strike = atm_strike + self.itm_points
        total_quantity = self.number_of_lots * self.lot_size
        
        print(f"Spot Price: {spot_price}")
        print(f"ATM Strike: {atm_strike}")
        print(f"ITM Strike: {itm_strike}")
        print(f"Quantity: {total_quantity}")
        
        # Place call spread
        order_response = self.utils.place_call_spread(
            strike_price=itm_strike,
            quantity=total_quantity,
            exchange=self.exchange,
            trading_symbol=self.trading_symbol,
            expiry=self.expiry_to_trade,
            spread_gap=self.spread_gap
        )
        
        return {
            "status": "success",
            "action": "call_spread_placed",
            "trigger": "bald_candle_strong_red",
            "strike": itm_strike,
            "quantity": total_quantity,
            "spot_price": spot_price,
            "reference_level_x": reference_level_x,
            "first_candle": first_15min,
            "trigger_candle": strong_red_candle,
            "order_response": order_response
        }
    
    def execute_doji_candle_strategy(self, first_15min: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute strategy when first candle is a doji candle
        
        Steps:
        7. Get 15-minute candle OHLC of expiry_to_check OTM call option strike (ATM + otm_points)
           based on the spot price (15-minute candle closing price) - specifically 9:15-9:30 AM candle
        8. Get EMA 33 OHLC of expiry_to_check OTM call option strike based on the spot price
        9. First 15-minute option closing price (from step 7) should be less than EMA 33 low
           of options chart (from step 8), if not stop trade execution
        10. Monitor 15-minute candles of options expiry_to_check OTM call option strike and
            observe the option chart on a 15-minute timeframe with EMA 33 applied till 12 PM
        11. Enter the trade when the 15-minute option candle touches EMA 33 high, and sell a
            call spread at ITM (ATM + itm_points) based on spot price at that time with expiry_to_trade
        
        Args:
            first_15min: First 15-minute candle data
            
        Returns:
            Dictionary with execution results
        """
        print("\n=== Executing Doji Candle Strategy ===")
        
        # Step 7: Get 15-minute candle OHLC of expiry_to_check OTM call option strike
        # based on the spot price (15-minute candle closing price) - 9:15-9:30 AM candle
        print("\n--- Step 7: Getting First 15-Min Option Candle (9:15-9:30 AM) ---")
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
        
        # Step 8: Get EMA 33 OHLC of expiry_to_check OTM call option strike
        print("\n--- Step 8: Calculating EMA 33 OHLC for Option Chart ---")
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
        
        # Step 9: First 15-minute option closing price should be less than EMA 33 low
        print("\n--- Step 9: Validating Option Close < EMA 33 Low ---")
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
        
        # Step 10: Monitor 15-minute candles of options and observe with EMA 33 till 12 PM
        print("\n--- Step 10: Monitoring Option Candles for EMA 33 High Touch (till 12 PM) ---")
        time_12_00 = time(12, 0)
        
        ema_touched = self.monitor_option_for_ema_touch(option_symbol, ema_high, time_12_00)
        
        if not ema_touched:
            print("\n✗ Option did not touch EMA 33 high before 12:00 PM. No trade placed.")
            return {
                "status": "success",
                "action": "no_trade",
                "reason": "no_ema_touch_before_12pm",
                "option_symbol": option_symbol,
                "ema_high": ema_high,
                "first_candle": first_15min
            }
        
        # Step 11: Enter trade when 15-minute option candle touches EMA 33 high
        # Sell call spread with strike price of spot chart at that time with expiry_to_trade
        print("\n--- Step 11: Placing Call Spread at ITM (EMA Touch Detected) ---")
        
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
            "first_candle": first_15min,
            "order_response": order_response
        }
