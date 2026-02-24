"""
Sell 2 Strategy Implementation
This strategy implements the sell_2 trading logic with R1 and R2 levels
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Sell2Strategy:
    """
    Sell 2 Strategy Class
    Implements the trading logic for the sell_2 strategy with dual resistance levels
    
    Strategy Logic:
    1. Wait till 9:18 AM
    2. Analyze first 3-minute candle (9:15-9:18 AM)
    3. If conditions met, place 50% order at R1, wait for R2 till 2 PM for remaining 50%
    4. If 3-min conditions not met, wait for 9:30 AM and analyze first 15-minute candle
    5. If 15-min conditions met, place 50% order at R1, wait for R2 till 2 PM for remaining 50%
    """
    
    def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any], strategy_config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            groww: GrowwAPI instance
            utils: Utils instance with helper methods
            config: Full configuration dictionary
            strategy_config: Strategy-specific configuration (must contain r1 and r2)
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
        
        # Extract strategy-specific config (R1 and R2 levels)
        self.r1 = float(strategy_config.get('r1', 23000))
        self.r2 = float(strategy_config.get('r2', 23500))
        
        # Validate R2 > R1
        if self.r2 <= self.r1:
            raise ValueError(f"R2 ({self.r2}) must be greater than R1 ({self.r1})")
        
        print(f"Sell2Strategy initialized with:")
        print(f"  - R1: {self.r1}")
        print(f"  - R2: {self.r2}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def _wait_for_r2_and_place_order(self, itm_strike: float, half_quantity: int, trigger: str) -> Dict[str, Any]:
        """
        Monitor spot price and place remaining 50% order when R2 is reached
        Monitors till 2 PM IST
        
        Args:
            itm_strike: ITM strike price
            half_quantity: 50% of total quantity
            trigger: What triggered the first order ('3min_candle' or '15min_candle')
            
        Returns:
            Dictionary with order placement results
        """
        from datetime import datetime, time
        import time as time_module
        
        print(f"\n--- Monitoring for R2 Level ({self.r2}) till 2 PM ---")
        
        time_2pm = time(14, 0)
        
        while True:
            current_time = datetime.now().time()
            
            # Check if 2 PM reached
            if current_time >= time_2pm:
                print(f"✗ 2 PM reached. R2 level not hit. No second order placed.")
                return {
                    "status": "timeout",
                    "message": "R2 not reached by 2 PM",
                    "r2_reached": False
                }
            
            # Get current spot price
            spot_price = self.utils.get_spot_price(self.exchange)
            print(f"[{current_time.strftime('%H:%M:%S')}] Spot: {spot_price}, R2: {self.r2}")
            
            # Check if R2 reached
            if spot_price >= self.r2:
                print(f"\n✓ R2 Level Reached! Spot: {spot_price} >= R2: {self.r2}")
                print(f"Placing remaining 50% Call Spread...")
                
                # Place second 50% order
                order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=half_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "second_50_placed",
                    "trigger": trigger,
                    "strike": itm_strike,
                    "quantity": half_quantity,
                    "spot_price": spot_price,
                    "r2_reached": True,
                    "order_response": order_response
                }
            
            # Wait 1 second before next check
            time_module.sleep(1)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the sell_2 strategy with R1 and R2 levels
        
        Strategy Logic:
        1. Wait till 9:18 AM
        2. Get first 3-minute candle (9:15-9:18 AM)
        3. Check if red candle and (open - close) > (high - open + close - low)
           If yes: Place 50% at R1, monitor for R2 till 2 PM for remaining 50%
        4. If step 3 not satisfied, wait for 9:30 AM
        5. Get first 15-minute candle (9:15-9:30 AM)
        6. Check if red candle and ((open - close) / open) > 0.001
           If yes: Place 50% at R1, monitor for R2 till 2 PM for remaining 50%
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Sell 2 Strategy ===")
            
            # Calculate quantities
            total_quantity = self.number_of_lots * self.lot_size
            half_quantity = (self.number_of_lots // 2) * self.lot_size
            
            print(f"Total Quantity: {total_quantity} ({self.number_of_lots} lots × {self.lot_size})")
            print(f"50% Quantity: {half_quantity} ({self.number_of_lots // 2} lots × {self.lot_size})")
            
            # Step 1: Wait till 9:18 AM
            current_time = datetime.now().time()
            time_9_18 = time(9, 18)
            
            if current_time < time_9_18:
                wait_seconds = (datetime.combine(datetime.today(), time_9_18) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"\nWaiting till 9:18 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:18 AM reached")
            
            # Step 2: Get first 3-minute candle (9:15-9:18 AM)
            print("\n--- Analyzing First 3-Minute Candle (9:15-9:18 AM) ---")
            first_3min = self.utils.get_first_3min_candle(self.exchange)
            
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
            condition_3min = (o - c) > (h - o + c - l)
            
            print(f"\n3-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red} ({o} > {c})")
            print(f"  - (open - close) > (high - open + close - low): {condition_3min}")
            print(f"    ({o - c:.2f} > {h - o + c - l:.2f})")
            
            if is_red and condition_3min:
                print("\n✓ 3-minute candle conditions met!")
                
                # Wait for spot price to reach R1 (monitor till 2 PM)
                print(f"\n--- Monitoring for R1 Level ({self.r1}) till 2 PM ---")
                
                time_2pm = time(14, 0)
                r1_reached = False
                
                while True:
                    current_time = datetime.now().time()
                    
                    # Check if 2 PM reached
                    if current_time >= time_2pm:
                        print(f"\n✗ 2 PM reached. R1 level not hit. No trade placed.")
                        return {
                            "status": "success",
                            "action": "no_trade",
                            "reason": "r1_not_reached_by_2pm",
                            "candle_data": first_3min
                        }
                    
                    spot_price = self.utils.get_spot_price(self.exchange)
                    print(f"[{current_time.strftime('%H:%M:%S')}] Spot: {spot_price}, R1: {self.r1}")
                    
                    if spot_price >= self.r1:
                        print(f"\n✓ R1 Level Reached! Spot: {spot_price} >= R1: {self.r1}")
                        r1_reached = True
                        break
                    
                    # Wait 1 second before next check
                    time_module.sleep(1)
                
                if not r1_reached:
                    return {
                        "status": "success",
                        "action": "no_trade",
                        "reason": "r1_not_reached",
                        "candle_data": first_3min
                    }
                
                # Calculate strikes
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nPlacing First 50% Call Spread...")
                print(f"Spot Price: {spot_price}")
                print(f"ATM Strike: {atm_strike}")
                print(f"ITM Strike: {itm_strike}")
                print(f"Quantity: {half_quantity} (50%)")
                
                # Place first 50% order
                first_order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=half_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                # Wait for R2 and place remaining 50%
                second_order_result = self._wait_for_r2_and_place_order(
                    itm_strike=itm_strike,
                    half_quantity=half_quantity,
                    trigger='3min_candle'
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "3min_candle",
                    "strike": itm_strike,
                    "total_quantity": total_quantity,
                    "first_50_quantity": half_quantity,
                    "second_50_quantity": half_quantity if second_order_result.get('r2_reached') else 0,
                    "spot_price_r1": spot_price,
                    "candle_data": first_3min,
                    "first_order": first_order_response,
                    "second_order": second_order_result
                }
            
            # Step 4: If 3-minute conditions not met, wait for 9:30 AM
            print("\n✗ 3-minute candle conditions not met. Waiting for 9:30 AM...")
            
            current_time = datetime.now().time()
            time_9_30 = time(9, 30)
            
            if current_time < time_9_30:
                wait_seconds = (datetime.combine(datetime.today(), time_9_30) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"Waiting till 9:30 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:30 AM reached")
            
            # Step 5: Get first 15-minute candle (9:15-9:30 AM)
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
            
            # Step 6: Check 15-minute candle conditions
            is_red_15 = o_15 > c_15
            percentage_drop = (o_15 - c_15) / o_15
            condition_15min = percentage_drop > 0.001
            
            print(f"\n15-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red_15} ({o_15} > {c_15})")
            print(f"  - Percentage drop: {percentage_drop:.4f} ({percentage_drop * 100:.2f}%)")
            print(f"  - ((open - close) / open) > 0.001: {condition_15min}")
            
            if is_red_15 and condition_15min:
                print("\n✓ 15-minute candle conditions met!")
                
                # Wait for spot price to reach R1 (monitor till 2 PM)
                print(f"\n--- Monitoring for R1 Level ({self.r1}) till 2 PM ---")
                
                time_2pm = time(14, 0)
                r1_reached = False
                
                while True:
                    current_time = datetime.now().time()
                    
                    # Check if 2 PM reached
                    if current_time >= time_2pm:
                        print(f"\n✗ 2 PM reached. R1 level not hit. No trade placed.")
                        return {
                            "status": "success",
                            "action": "no_trade",
                            "reason": "r1_not_reached_by_2pm",
                            "candle_data": first_15min
                        }
                    
                    spot_price = self.utils.get_spot_price(self.exchange)
                    print(f"[{current_time.strftime('%H:%M:%S')}] Spot: {spot_price}, R1: {self.r1}")
                    
                    if spot_price >= self.r1:
                        print(f"\n✓ R1 Level Reached! Spot: {spot_price} >= R1: {self.r1}")
                        r1_reached = True
                        break
                    
                    # Wait 1 second before next check
                    time_module.sleep(1)
                
                if not r1_reached:
                    return {
                        "status": "success",
                        "action": "no_trade",
                        "reason": "r1_not_reached",
                        "candle_data": first_15min
                    }
                
                # Calculate strikes
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nPlacing First 50% Call Spread...")
                print(f"Spot Price: {spot_price}")
                print(f"ATM Strike: {atm_strike}")
                print(f"ITM Strike: {itm_strike}")
                print(f"Quantity: {half_quantity} (50%)")
                
                # Place first 50% order
                first_order_response = self.utils.place_call_spread(
                    strike_price=itm_strike,
                    quantity=half_quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                # Wait for R2 and place remaining 50%
                second_order_result = self._wait_for_r2_and_place_order(
                    itm_strike=itm_strike,
                    half_quantity=half_quantity,
                    trigger='15min_candle'
                )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "15min_candle",
                    "strike": itm_strike,
                    "total_quantity": total_quantity,
                    "first_50_quantity": half_quantity,
                    "second_50_quantity": half_quantity if second_order_result.get('r2_reached') else 0,
                    "spot_price_r1": spot_price,
                    "candle_data": first_15min,
                    "first_order": first_order_response,
                    "second_order": second_order_result
                }
            else:
                print("\n✗ 15-minute candle conditions not met. No trade placed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "15min_conditions_not_met",
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
