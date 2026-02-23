"""
Sell 3 Strategy Implementation
This strategy implements the sell_3 trading logic with multiple conditional paths
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Sell3Strategy:
    """
    Sell 3 Strategy Class
    Implements the trading logic for the sell_3 strategy with R1 level and EMA 33
    
    Strategy Logic:
    1. Wait till 9:18 AM
    2. Get first 3-minute candle (9:15-9:18 AM)
    3. If red and 2×(high-open) < (close-low) and close < EMA33_high: Place call spread
    4. If not, wait till 9:45 AM
    5. Get first 15-minute candle
    6. If green and rise > 0.001: Place at 15min_close + ATR, wait till 2 PM
    7. If not, check green and open > R1 and specific conditions: Place call spread
    8. If not, check open < R1 and specific conditions: Place at R1, wait till 2 PM
    9. If not, wait till 10:15 AM
    10. Get first 60-minute candle
    11. If open > R1 and specific conditions: Place call spread
    """
    
    def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any], strategy_config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            groww: GrowwAPI instance
            utils: Utils instance with helper methods
            config: Full configuration dictionary
            strategy_config: Strategy-specific configuration (must contain r1)
        """
        self.groww = groww
        self.utils = utils
        self.config = config
        self.strategy_config = strategy_config
        
        # Extract common config values
        self.expiry = config.get('expiry')
        self.spread_gap = int(config.get('spread_gap', 200))
        self.exchange = config.get('exchange', 'NSE').upper()
        self.trading_symbol = config.get('trading_symbol', 'NIFTY').upper()
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        self.atr = float(config.get('atr', 40))
        
        # Extract strategy-specific config (R1 level)
        self.r1 = float(strategy_config.get('r1', 23000))
        
        print(f"Sell3Strategy initialized with:")
        print(f"  - R1: {self.r1}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def _wait_for_level_and_place_order(self, target_level: float, itm_strike: float, 
                                        quantity: int, level_name: str) -> Dict[str, Any]:
        """
        Monitor spot price and place order when target level is reached
        Monitors till 2 PM IST
        
        Args:
            target_level: Target price level to reach
            itm_strike: ITM strike price
            quantity: Quantity to trade
            level_name: Name of the level for logging
            
        Returns:
            Dictionary with order placement results
        """
        from datetime import datetime, time
        import time as time_module
        
        print(f"\n--- Monitoring for {level_name} Level ({target_level:.2f}) till 2 PM ---")
        
        time_2pm = time(14, 0)
        
        while True:
            current_time = datetime.now().time()
            
            # Check if 2 PM reached
            if current_time >= time_2pm:
                print(f"✗ 2 PM reached. {level_name} level not hit. Order not placed.")
                return {
                    "status": "timeout",
                    "message": f"{level_name} not reached by 2 PM",
                    "level_reached": False,
                    "target_level": target_level
                }
            
            # Get current spot price
            spot_price = self.utils.get_spot_price(self.exchange)
            print(f"[{current_time.strftime('%H:%M:%S')}] Spot: {spot_price:.2f}, Target ({level_name}): {target_level:.2f}")
            
            # Check if target level reached
            if spot_price >= target_level:
                print(f"\n✓ {level_name} Level Reached! Spot: {spot_price:.2f} >= Target: {target_level:.2f}")
                print(f"Placing Call Spread...")
                
                # Place order
                order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "strike": itm_strike,
                    "quantity": quantity,
                    "spot_price": spot_price,
                    "target_level": target_level,
                    "level_reached": True,
                    "order_response": order_response
                }
            
            # Wait 1 second before next check
            time_module.sleep(1)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the sell_3 strategy with multiple conditional paths
        
        Strategy Steps:
        Step 1: Wait till 9:18 AM
        Step 2: Get OHLC of first 3 minutes candle (9:15-9:18 AM)
        Step 3: If red (open > close) AND 2×(high-open) < (close-low) AND close < EMA33_high
                → Place call spread immediately
        Step 4: If Step 3 not satisfied, wait till 9:45 AM
        Step 5: Get OHLC of first 15 minutes candle (9:15-9:30 AM)
        Step 6: If green (close > open) AND ((close-open)/open) > 0.001
                → Place call spread at 15min_close + ATR, wait till 2 PM
        Step 7: If Step 6 not satisfied, check:
                Green AND (open > R1) AND (close-open) < (high-close+open-low) AND ((close-open)/open) < 0.001
                → Place call spread immediately
        Step 8: If Step 7 not satisfied, check:
                (open < R1) AND (close-open) < (high-close+open-low) AND (open-close) < (high-open+close-low)
                → Place call spread at R1, wait till 2 PM
        Step 9: If Step 8 not satisfied, wait till 10:15 AM
        Step 10: Get OHLC of first 60 minutes candle (9:15-10:15 AM)
        Step 11: If (open > R1) AND (close-open) < (high-close+open-low) AND ((close-open)/open) < 0.002
                 → Place call spread immediately
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Sell 3 Strategy ===")
            
            # Calculate quantities
            total_quantity = self.number_of_lots * self.lot_size
            
            print(f"Total Quantity: {total_quantity} ({self.number_of_lots} lots × {self.lot_size})")
            
            # ========== STEP 1: Wait till 9:18 AM ==========
            current_time = datetime.now().time()
            time_9_18 = time(9, 18)
            
            if current_time < time_9_18:
                wait_seconds = (datetime.combine(datetime.today(), time_9_18) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"\nWaiting till 9:18 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:18 AM reached")
            
            # ========== STEP 2: Get first 3-minute candle (9:15-9:18 AM) ==========
            print("\n--- Analyzing First 3-Minute Candle (9:15-9:18 AM) ---")
            first_3min = self.utils.get_first_3min_candle(self.exchange)
            
            if not first_3min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 3-minute candle"
                }
            
            o_3 = first_3min['open']
            h_3 = first_3min['high']
            l_3 = first_3min['low']
            c_3 = first_3min['close']
            
            print(f"First 3-min Candle: O={o_3}, H={h_3}, L={l_3}, C={c_3}")
            
            # Get EMA 33 high of 15-minute candles
            print("\n--- Fetching EMA 33 High of 15-Minute Candles ---")
            ema_data = self.utils.get_ema_33_15min(self.exchange)
            
            if not ema_data:
                return {
                    "status": "error",
                    "error": "Unable to fetch EMA 33 data"
                }
            
            ema_33_high = ema_data['ema_high']
            print(f"EMA 33 High: {ema_33_high:.2f}")
            
            # ========== STEP 3: Check 3-min candle conditions ==========
            # Conditions: red AND 2×(high-open) < (close-low) AND close < EMA33_high
            is_red_3 = o_3 > c_3
            condition_3a = 2 * (h_3 - o_3) < (c_3 - l_3)
            condition_3b = c_3 < ema_33_high
            
            print(f"\n3-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red_3} ({o_3} > {c_3})")
            print(f"  - 2 × (high - open) < (close - low): {condition_3a}")
            print(f"    ({2 * (h_3 - o_3):.2f} < {c_3 - l_3:.2f})")
            print(f"  - close < EMA 33 High: {condition_3b} ({c_3:.2f} < {ema_33_high:.2f})")
            
            if is_red_3 and condition_3a and condition_3b:
                print("\n✓ All 3-minute candle conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"Spot Price: {spot_price}")
                print(f"ATM Strike: {atm_strike}")
                print(f"ITM Strike: {itm_strike}")
                
                # Place call spread
                order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=total_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "3min_candle",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "spot_price": spot_price,
                    "candle_data": first_3min,
                    "ema_33_high": ema_33_high,
                    "order_response": order_response
                }
            
            # ========== STEP 4: Wait till 9:45 AM if Step 3 not satisfied ==========
            print("\n✗ 3-minute candle conditions not met. Waiting for 9:45 AM...")
            
            current_time = datetime.now().time()
            time_9_45 = time(9, 45)
            
            if current_time < time_9_45:
                wait_seconds = (datetime.combine(datetime.today(), time_9_45) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"Waiting till 9:45 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:45 AM reached")
            
            # ========== STEP 5: Get first 15-minute candle (9:15-9:30 AM) ==========
            print("\n--- Analyzing First 15-Minute Candle (9:15-9:30 AM) ---")
            first_15min = self.utils.get_first_15min_candle(self.exchange)
            
            if not first_15min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 15-minute candle"
                }
            
            o_15 = first_15min['open']
            h_15 = first_15min['high']
            l_15 = first_15min['low']
            c_15 = first_15min['close']
            
            print(f"First 15-min Candle: O={o_15}, H={h_15}, L={l_15}, C={c_15}")
            
            # ========== STEP 6: Check green candle with rise > 0.001 ==========
            # If yes: Place at 15min_close + ATR, wait till 2 PM
            is_green_15 = c_15 > o_15
            percentage_rise_15 = (c_15 - o_15) / o_15
            condition_6 = percentage_rise_15 > 0.001
            
            print(f"\n15-Minute Candle Analysis (Step 6):")
            print(f"  - Is Green (close > open): {is_green_15} ({c_15} > {o_15})")
            print(f"  - Percentage rise: {percentage_rise_15:.4f} ({percentage_rise_15 * 100:.2f}%)")
            print(f"  - ((close - open) / open) > 0.001: {condition_6}")
            
            if is_green_15 and condition_6:
                print("\n✓ Step 6 conditions met! Placing at 15min_close + ATR...")
                
                # Calculate target level: 15min_close + ATR
                target_level = c_15 + self.atr
                
                print(f"\nTarget Level Calculation:")
                print(f"  - 15-min Close: {c_15}")
                print(f"  - ATR: {self.atr}")
                print(f"  - Target: {c_15} + {self.atr} = {target_level:.2f}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike: {itm_strike}")
                
                # Wait for target level and place order
                order_result = self._wait_for_level_and_place_order(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='15min_close+ATR'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "15min_green_rise",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_15min,
                    "order_result": order_result
                }
            
            # ========== STEP 7: Check green, open > R1, and specific conditions ==========
            # Conditions: green AND open > R1 AND (close-open) < (high-close+open-low) AND rise < 0.001
            condition_7a = o_15 > self.r1
            condition_7b = (c_15 - o_15) < (h_15 - c_15 + o_15 - l_15)
            condition_7c = percentage_rise_15 < 0.001
            
            print(f"\n15-Minute Candle Analysis (Step 7):")
            print(f"  - Is Green: {is_green_15}")
            print(f"  - open > R1: {condition_7a} ({o_15} > {self.r1})")
            print(f"  - (close - open) < (high - close + open - low): {condition_7b}")
            print(f"    ({c_15 - o_15:.2f} < {h_15 - c_15 + o_15 - l_15:.2f})")
            print(f"  - ((close - open) / open) < 0.001: {condition_7c}")
            
            if is_green_15 and condition_7a and condition_7b and condition_7c:
                print("\n✓ Step 7 conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"Spot Price: {spot_price}")
                print(f"ATM Strike: {atm_strike}")
                print(f"ITM Strike: {itm_strike}")
                
                # Place call spread
                order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=total_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "15min_green_above_r1",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "spot_price": spot_price,
                    "candle_data": first_15min,
                    "order_response": order_response
                }
            
            # ========== STEP 8: Check open < R1 and specific conditions ==========
            # Conditions: open < R1 AND (close-open) < (high-close+open-low) AND (open-close) < (high-open+close-low)
            # If yes: Place at R1, wait till 2 PM
            condition_8a = o_15 < self.r1
            condition_8b = (c_15 - o_15) < (h_15 - c_15 + o_15 - l_15)
            condition_8c = (o_15 - c_15) < (h_15 - o_15 + c_15 - l_15)
            
            print(f"\n15-Minute Candle Analysis (Step 8):")
            print(f"  - open < R1: {condition_8a} ({o_15} < {self.r1})")
            print(f"  - (close - open) < (high - close + open - low): {condition_8b}")
            print(f"    ({c_15 - o_15:.2f} < {h_15 - c_15 + o_15 - l_15:.2f})")
            print(f"  - (open - close) < (high - open + close - low): {condition_8c}")
            print(f"    ({o_15 - c_15:.2f} < {h_15 - o_15 + c_15 - l_15:.2f})")
            
            if condition_8a and condition_8b and condition_8c:
                print("\n✓ Step 8 conditions met! Placing at R1...")
                
                # Target level is R1
                target_level = self.r1
                
                print(f"\nTarget Level: R1 = {target_level}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike: {itm_strike}")
                
                # Wait for R1 level and place order
                order_result = self._wait_for_level_and_place_order(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='R1'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "15min_below_r1",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_15min,
                    "order_result": order_result
                }
            
            # ========== STEP 9: Wait till 10:15 AM if Step 8 not satisfied ==========
            print("\n✗ 15-minute candle conditions not met. Waiting for 10:15 AM...")
            
            current_time = datetime.now().time()
            time_10_15 = time(10, 15)
            
            if current_time < time_10_15:
                wait_seconds = (datetime.combine(datetime.today(), time_10_15) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"Waiting till 10:15 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 10:15 AM reached")
            
            # ========== STEP 10: Get first 60-minute candle (9:15-10:15 AM) ==========
            print("\n--- Analyzing First 60-Minute Candle (9:15-10:15 AM) ---")
            
            # Fetch 60-minute candle
            from datetime import datetime as dt
            current_date = dt.now()
            start_time = f"{current_date.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_date.strftime('%Y-%m-%d')} 10:15:00"
            
            exchange_const = self.groww.EXCHANGE_NSE if self.exchange == 'NSE' else self.groww.EXCHANGE_BSE
            trading_symbol = 'NIFTY' if self.exchange == 'NSE' else 'SENSEX'
            
            historical_response = self.groww.get_historical_candle_data(
                trading_symbol=trading_symbol,
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                interval_in_minutes=60
            )
            
            if not historical_response or 'candles' not in historical_response or len(historical_response['candles']) == 0:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 60-minute candle"
                }
            
            candle_60 = historical_response['candles'][0]
            o_60 = candle_60[1]
            h_60 = candle_60[2]
            l_60 = candle_60[3]
            c_60 = candle_60[4]
            
            print(f"First 60-min Candle: O={o_60}, H={h_60}, L={l_60}, C={c_60}")
            
            # ========== STEP 11: Check 60-min candle conditions ==========
            # Conditions: open > R1 AND (close-open) < (high-close+open-low) AND rise < 0.002
            condition_11a = o_60 > self.r1
            condition_11b = (c_60 - o_60) < (h_60 - c_60 + o_60 - l_60)
            percentage_rise_60 = (c_60 - o_60) / o_60
            condition_11c = percentage_rise_60 < 0.002
            
            print(f"\n60-Minute Candle Analysis (Step 11):")
            print(f"  - open > R1: {condition_11a} ({o_60} > {self.r1})")
            print(f"  - (close - open) < (high - close + open - low): {condition_11b}")
            print(f"    ({c_60 - o_60:.2f} < {h_60 - c_60 + o_60 - l_60:.2f})")
            print(f"  - Percentage rise: {percentage_rise_60:.4f} ({percentage_rise_60 * 100:.2f}%)")
            print(f"  - ((close - open) / open) < 0.002: {condition_11c}")
            
            if condition_11a and condition_11b and condition_11c:
                print("\n✓ Step 11 conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"Spot Price: {spot_price}")
                print(f"ATM Strike: {atm_strike}")
                print(f"ITM Strike: {itm_strike}")
                
                # Place call spread
                order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=total_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "60min_above_r1",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "spot_price": spot_price,
                    "candle_data": {
                        'open': o_60, 'high': h_60, 'low': l_60, 'close': c_60
                    },
                    "order_response": order_response
                }
            else:
                print("\n✗ 60-minute candle conditions not met. No trade placed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "60min_conditions_not_met",
                    "candle_data": {
                        'open': o_60, 'high': h_60, 'low': l_60, 'close': c_60
                    }
                }
                
        except Exception as e:
            print(f"✗ Error executing strategy: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
