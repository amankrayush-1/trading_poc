"""
Sell 4 Strategy Implementation
This strategy implements the sell_4 trading logic with ATR-based levels
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Sell4Strategy:
    """
    Sell 4 Strategy Class
    Implements the trading logic for the sell_4 strategy with ATR-based entry levels
    
    Strategy Logic:
    1. Wait till 9:30 AM
    2. Get first 15-minute candle (9:15-9:30 AM)
    3. If green candle and ((close - open) / open) > 0.001:
       - Place 50% at (15min_close + 2×ATR)
       - Place 50% at (15min_close + 3×ATR)
       - Monitor till 2 PM IST
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
        self.exchange = config.get('exchange', 'NSE').upper()
        self.trading_symbol = config.get('trading_symbol', 'NIFTY').upper()
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        self.atr = float(config.get('atr', 40))
        
        print(f"Sell4Strategy initialized with:")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def _wait_for_level_and_place_order(self, target_level: float, itm_strike: float, 
                                        half_quantity: int, level_name: str) -> Dict[str, Any]:
        """
        Monitor spot price and place order when target level is reached
        Monitors till 2 PM IST
        
        Args:
            target_level: Target price level to reach
            itm_strike: ITM strike price
            half_quantity: 50% of total quantity
            level_name: Name of the level for logging (e.g., '2×ATR', '3×ATR')
            
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
                print(f"Placing 50% Call Spread...")
                
                # Place order
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
                    "action": f"{level_name}_order_placed",
                    "strike": itm_strike,
                    "quantity": half_quantity,
                    "spot_price": spot_price,
                    "target_level": target_level,
                    "level_reached": True,
                    "order_response": order_response
                }
            
            # Wait 1 second before next check
            time_module.sleep(1)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the sell_4 strategy with ATR-based levels
        
        Strategy Logic:
        1. Wait till 9:30 AM
        2. Get first 15-minute candle (9:15-9:30 AM)
        3. Check if green candle and ((close - open) / open) > 0.001
        4. If yes:
           - Calculate Level 1: 15min_close + 2×ATR
           - Calculate Level 2: 15min_close + 3×ATR
           - Place 50% at Level 1, 50% at Level 2
           - Monitor till 2 PM IST
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Sell 4 Strategy ===")
            
            # Calculate quantities
            total_quantity = self.number_of_lots * self.lot_size
            half_quantity = (self.number_of_lots // 2) * self.lot_size
            
            print(f"Total Quantity: {total_quantity} ({self.number_of_lots} lots × {self.lot_size})")
            print(f"50% Quantity: {half_quantity} ({self.number_of_lots // 2} lots × {self.lot_size})")
            
            # Step 1: Wait till 9:30 AM
            current_time = datetime.now().time()
            time_9_30 = time(9, 30)
            
            if current_time < time_9_30:
                wait_seconds = (datetime.combine(datetime.today(), time_9_30) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"\nWaiting till 9:30 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:30 AM reached")
            
            # Step 2: Get first 15-minute candle (9:15-9:30 AM)
            print("\n--- Analyzing First 15-Minute Candle (9:15-9:30 AM) ---")
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
            
            # Step 3: Check 15-minute candle conditions
            is_green = c > o
            percentage_rise = (c - o) / o
            condition_met = percentage_rise > 0.001
            
            print(f"\n15-Minute Candle Analysis:")
            print(f"  - Is Green (close > open): {is_green} ({c} > {o})")
            print(f"  - Percentage rise: {percentage_rise:.4f} ({percentage_rise * 100:.2f}%)")
            print(f"  - ((close - open) / open) > 0.001: {condition_met}")
            
            if is_green and condition_met:
                print("\n✓ 15-minute candle conditions met!")
                
                # Calculate ATR-based levels
                level_1 = c + (2 * self.atr)  # 15min_close + 2×ATR
                level_2 = c + (3 * self.atr)  # 15min_close + 3×ATR
                
                print(f"\nATR-Based Levels:")
                print(f"  - 15-min Close: {c}")
                print(f"  - ATR: {self.atr}")
                print(f"  - Level 1 (Close + 2×ATR): {level_1:.2f}")
                print(f"  - Level 2 (Close + 3×ATR): {level_2:.2f}")
                
                # Get current spot price and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike: {itm_strike}")
                
                # Wait for Level 1 (Close + 2×ATR) and place first 50%
                first_order_result = self._wait_for_level_and_place_order(
                    target_level=level_1,
                    itm_strike=itm_strike,
                    half_quantity=half_quantity,
                    level_name='2×ATR'
                )
                
                # If Level 1 reached, wait for Level 2 (Close + 3×ATR) and place second 50%
                second_order_result = None
                if first_order_result.get('level_reached'):
                    second_order_result = self._wait_for_level_and_place_order(
                        target_level=level_2,
                        itm_strike=itm_strike,
                        half_quantity=half_quantity,
                        level_name='3×ATR'
                    )
                
                return {
                    "status": "success",
                    "action": "call_spread_placed",
                    "trigger": "15min_candle_atr",
                    "strike": itm_strike,
                    "total_quantity": total_quantity,
                    "first_50_quantity": half_quantity if first_order_result.get('level_reached') else 0,
                    "second_50_quantity": half_quantity if second_order_result and second_order_result.get('level_reached') else 0,
                    "candle_data": first_15min,
                    "level_1": level_1,
                    "level_2": level_2,
                    "first_order": first_order_result,
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
