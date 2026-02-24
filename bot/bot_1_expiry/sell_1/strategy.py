"""
Sell 1 Strategy Implementation
This strategy implements the sell_1 trading logic
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Sell1Strategy:
    """
    Sell 1 Strategy Class
    Implements the trading logic for the sell_1 strategy
    """
    
    def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any], strategy_config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            groww: GrowwAPI instance
            utils: Utils instance with helper methods
            config: Full configuration dictionary
            strategy_config: Strategy-specific configuration
        """
        self.groww = groww
        self.utils = utils
        self.config = config
        self.strategy_config = strategy_config
        
        # Extract common config values
        self.expiry = config.get('expiry')
        self.spread_gap = int(config.get('spread_gap', 200))
        self.exchange = config.get('exchange', 'nifty')
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        self.atr = float(config.get('atr', 40))
        
        # Extract strategy-specific config
        self.r1 = float(strategy_config.get('r1', 23000))
        
        print(f"Sell1Strategy initialized with:")
        print(f"  - R1: {self.r1}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the sell_1 strategy with time-based candle analysis
        
        Strategy Logic:
        1. Wait till 9:18 AM
        2. After 9:18 AM, get first 3-minute candle (9:15-9:18 AM)
        3. Check if candle is red with specific conditions:
           - Candle is red: open > close
           - (open - close) < (high - open + close - low)
           - 2 * (high - open) < (close - low)
           If all conditions met, place call spread with ITM
        4. If step 3 not satisfied, wait for 9:45 AM
        5. After 9:45 AM, get first 30-minute candle (9:15-9:45 AM)
        6. Check if candle is red and ((open - close) / open) > 0.001
           If condition met, place call spread with ITM
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n--- Executing Sell 1 Strategy ---")
            
            # Get exchange from config
            exchange = self.config.get('exchange', 'NSE').upper()
            trading_symbol = self.config.get('trading_symbol', 'NIFTY').upper()
            
            # Step 1: Wait till 9:18 AM
            current_time = datetime.now().time()
            time_9_18 = time(9, 18)
            
            if current_time < time_9_18:
                wait_seconds = (datetime.combine(datetime.today(), time_9_18) -
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"Waiting till 9:18 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:18 AM reached")
            
            # Step 2: Get first 3-minute candle (9:15-9:18 AM)
            print("\n--- Analyzing First 3-Minute Candle (9:15-9:18 AM) ---")
            first_3min = self.utils.get_first_3min_candle(exchange)
            
            if not first_3min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 3-minute candle"
                }
            
            o = first_3min['open']
            h = first_3min['high']
            l = first_3min['low']
            c = first_3min['close']
            
            print(f"First 3-min Candle: O={o}, H={h}, L={l}, C={c}")
            
            # Step 3: Check first 3-minute candle conditions
            is_red = o > c
            condition_1 = (o - c) < (h - o + c - l)
            condition_2 = 2 * (h - o) < (c - l)
            
            print(f"\n3-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red} ({o} > {c})")
            print(f"  - (open - close) < (high - open + close - low): {condition_1}")
            print(f"    ({o - c:.2f} < {h - o + c - l:.2f})")
            print(f"  - 2 × (high - open) < (close - low): {condition_2}")
            print(f"    ({2 * (h - o):.2f} < {c - l:.2f})")
            
            if is_red and condition_1 and condition_2:
                print("\n✓ All 3-minute candle conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, exchange)
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
                    exchange=exchange,
                    trading_symbol=trading_symbol,
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
                    "order_response": order_response
                }
            
            # Step 4: If 3-minute conditions not met, wait for 9:45 AM
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
            
            # Step 5: Get first 30-minute candle (9:15-9:45 AM)
            print("\n--- Analyzing First 30-Minute Candle (9:15-9:45 AM) ---")
            first_30min = self.utils.get_first_30min_candle(exchange)
            
            if not first_30min:
                return {
                    "status": "error",
                    "error": "Unable to fetch first 30-minute candle"
                }
            
            o_30 = first_30min['open']
            h_30 = first_30min['high']
            l_30 = first_30min['low']
            c_30 = first_30min['close']
            
            print(f"First 30-min Candle: O={o_30}, H={h_30}, L={l_30}, C={c_30}")
            
            # Step 6: Check 30-minute candle conditions
            is_red_30 = o_30 > c_30
            percentage_drop = (o_30 - c_30) / o_30
            condition_30min = percentage_drop > 0.001
            
            print(f"\n30-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red_30} ({o_30} > {c_30})")
            print(f"  - Percentage drop: {percentage_drop:.4f} ({percentage_drop * 100:.2f}%)")
            print(f"  - ((open - close) / open) > 0.001: {condition_30min}")
            
            if is_red_30 and condition_30min:
                print("\n✓ 30-minute candle conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, exchange)
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
                    exchange=exchange,
                    trading_symbol=trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "30min_candle",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "spot_price": spot_price,
                    "candle_data": first_30min,
                    "order_response": order_response
                }
            else:
                print("\n✗ 30-minute candle conditions not met. No trade placed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "30min_conditions_not_met",
                    "candle_data": first_30min
                }
                
        except Exception as e:
            print(f"✗ Error executing strategy: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
