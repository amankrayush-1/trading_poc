"""
Sell 5 Strategy Implementation
This strategy implements the sell_5 trading logic with green candle analysis
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Sell5Strategy:
    """
    Sell 5 Strategy Class
    Implements the trading logic for the sell_5 strategy
    
    Strategy Logic:
    1. Wait till 9:30 AM
    2. Get first 15-minute candle (9:15-9:30 AM)
    3. Check if green candle and ((close - open) / open) > 0.001 and (high - close) > 2×(open - low)
       If yes: Place call spread immediately
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
        
        print(f"Sell5Strategy initialized with:")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the sell_5 strategy
        
        Strategy Logic:
        1. Wait till 9:30 AM
        2. Get first 15-minute candle (9:15-9:30 AM)
        3. Check if green candle and ((close - open) / open) > 0.001 and (high - close) > 2×(open - low)
        4. If yes: Place call spread immediately
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Sell 5 Strategy ===")
            
            # Calculate quantities
            total_quantity = self.number_of_lots * self.lot_size
            
            print(f"Total Quantity: {total_quantity} ({self.number_of_lots} lots × {self.lot_size})")
            
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
            condition_1 = percentage_rise > 0.001
            condition_2 = (h - c) > 2 * (o - l)
            
            print(f"\n15-Minute Candle Analysis:")
            print(f"  - Is Green (close > open): {is_green} ({c} > {o})")
            print(f"  - Percentage rise: {percentage_rise:.4f} ({percentage_rise * 100:.2f}%)")
            print(f"  - ((close - open) / open) > 0.001: {condition_1}")
            print(f"  - (high - close) > 2 × (open - low): {condition_2}")
            print(f"    ({h - c:.2f} > {2 * (o - l):.2f})")
            
            if is_green and condition_1 and condition_2:
                print("\n✓ All 15-minute candle conditions met! Placing Call Spread...")
                
                # Get spot price and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike + self.itm_points
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike: {itm_strike}")
                print(f"  - Quantity: {total_quantity}")
                
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
                    "trigger": "15min_candle",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "spot_price": spot_price,
                    "candle_data": first_15min,
                    "order_response": order_response
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
