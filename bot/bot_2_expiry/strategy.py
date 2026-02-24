"""
Bot 2 Strategy Implementation
Standalone trading bot with G1, G2, R1 level-based strategy
"""

from typing import Dict, Any
from growwapi import GrowwAPI

from bot.utils import Utils


# Add parent directory to path to import Utils
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils import Utils


class Bot2Strategy:
    """
    Bot 2 Strategy Class
    Implements trading logic with G1, G2, and R1 levels
    
    Strategy Steps:
    Step 1: Wait till 9:30 AM
    Step 2: Get OHLC of first 15 minute candle (9:15-9:30 AM)
    Step 3: Check if (abs(open - close) / open) > 0.001 (bald candle check)
            If condition is FALSE (not bald candle), stop execution
            If condition is TRUE (bald candle), proceed to next steps
    Step 4: If candle is green AND open < G1 AND open < G2 AND close < R1
            → Place call spread at (15min_close + R1) / 2 level, wait till 2 PM
    Step 5: If candle is RED AND close < G1 AND close < G2
            → Place call spread at G1 level, wait till 2 PM
    """
    
    def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            groww: GrowwAPI instance
            utils: Utils instance with helper methods
            config: Configuration dictionary with g1, g2, r1 levels
        """
        self.groww = groww
        self.utils = utils
        self.config = config
        
        # Extract config values
        self.g1 = float(config.get('g1'))
        self.g2 = float(config.get('g2'))
        self.r1 = float(config.get('r1'))
        self.expiry = config.get('expiry')
        self.spread_gap = int(config.get('spread_gap', 200))
        self.exchange = config.get('exchange', 'NSE').upper()
        self.trading_symbol = config.get('trading_symbol', 'NIFTY').upper()
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.itm_points = int(config.get('itm_points', 50))
        
        # Validate G1 < G2
        if self.g1 >= self.g2:
            raise ValueError(f"G1 ({self.g1}) must be less than G2 ({self.g2})")
        
        print(f"Bot2Strategy initialized with:")
        print(f"  - G1: {self.g1}")
        print(f"  - G2: {self.g2}")
        print(f"  - R1: {self.r1}")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
    
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
        Execute the bot_2_expiry strategy with G1, G2, R1 levels
        
        Strategy Steps:
        Step 1: Wait till 9:30 AM
        Step 2: Get OHLC of first 15 minute candle (9:15-9:30 AM)
        Step 3: Check if (abs(open - close) / open) > 0.001 (bald candle check)
                If condition is TRUE (bald candle), proceed to next steps
                If condition is FALSE (not bald candle), stop execution
        Step 4: If candle is green AND open < G1 AND open < G2 AND close < R1
                → Place call spread at (15min_close + R1) / 2 level, wait till 2 PM
        Step 5: If candle is RED AND close < G1 AND close < G2
                → Place call spread at G1 level, wait till 2 PM
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Bot 2 Strategy ===")
            
            # Calculate quantities
            total_quantity = self.number_of_lots * self.lot_size
            
            print(f"Total Quantity: {total_quantity} ({self.number_of_lots} lots × {self.lot_size})")
            print(f"Levels: G1={self.g1}, G2={self.g2}, R1={self.r1}")
            
            # ========== STEP 1: Wait till 9:30 AM ==========
            current_time = datetime.now().time()
            time_9_30 = time(9, 30)
            
            if current_time < time_9_30:
                wait_seconds = (datetime.combine(datetime.today(), time_9_30) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"\nWaiting till 9:30 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:30 AM reached")
            
            # ========== STEP 2: Get first 15-minute candle (9:15-9:30 AM) ==========
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
            
            # ========== STEP 3: Check if candle is bald ==========
            # Check: (abs(open - close) / open) > 0.001
            # If TRUE: candle is bald, proceed to next steps
            # If FALSE: candle is NOT bald, stop execution
            candle_body_percentage = abs(o - c) / o
            is_bald_candle = candle_body_percentage > 0.001
            
            print(f"\nStep 3 - Bald Candle Check:")
            print(f"  - Candle body percentage: {candle_body_percentage:.4f} ({candle_body_percentage * 100:.2f}%)")
            print(f"  - (abs(open - close) / open) > 0.001: {is_bald_candle}")
            
            if not is_bald_candle:
                print("\n✗ Candle is NOT bald (body <= 0.1%). Stopping execution.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "not_bald_candle",
                    "candle_data": first_15min,
                    "candle_body_percentage": candle_body_percentage
                }
            
            print("✓ Candle is bald (body > 0.1%). Proceeding with strategy...")
            
            # ========== STEP 4: Check green candle conditions ==========
            # Conditions: green AND open < G1 AND open < G2 AND close < R1
            is_green = c > o
            condition_4a = o < self.g1
            condition_4b = o < self.g2
            condition_4c = c < self.r1
            
            print(f"\nStep 4 - Green Candle Analysis:")
            print(f"  - Is Green (close > open): {is_green} ({c} > {o})")
            print(f"  - open < G1: {condition_4a} ({o} < {self.g1})")
            print(f"  - open < G2: {condition_4b} ({o} < {self.g2})")
            print(f"  - close < R1: {condition_4c} ({c} < {self.r1})")
            
            if is_green and condition_4a and condition_4b and condition_4c:
                print("\n✓ Step 4 conditions met! Placing at (15min_close + R1) / 2...")
                
                # Calculate target level: (15min_close + R1) / 2
                target_level = (c + self.r1) / 2
                
                print(f"\nTarget Level Calculation:")
                print(f"  - 15-min Close: {c}")
                print(f"  - R1: {self.r1}")
                print(f"  - Target: ({c} + {self.r1}) / 2 = {target_level:.2f}")
                
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
                    level_name='(Close+R1)/2'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "green_below_levels",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_15min,
                    "order_result": order_result
                }
            
            # ========== STEP 5: Check red candle conditions ==========
            # Conditions: RED AND close < G1 AND close < G2
            is_red = o > c
            condition_5a = c < self.g1
            condition_5b = c < self.g2
            
            print(f"\nStep 5 - Red Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red} ({o} > {c})")
            print(f"  - close < G1: {condition_5a} ({c} < {self.g1})")
            print(f"  - close < G2: {condition_5b} ({c} < {self.g2})")
            
            if is_red and condition_5a and condition_5b:
                print("\n✓ Step 5 conditions met! Placing at G1 level...")
                
                # Target level is G1
                target_level = self.g1
                
                print(f"\nTarget Level: G1 = {target_level}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike: {itm_strike}")
                
                # Wait for G1 level and place order
                order_result = self._wait_for_level_and_place_order(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='G1'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "red_below_levels",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_15min,
                    "order_result": order_result
                }
            else:
                print("\n✗ No conditions met. No trade placed.")
                return {
                    "status": "success",
                    "action": "no_trade",
                    "reason": "conditions_not_met",
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
