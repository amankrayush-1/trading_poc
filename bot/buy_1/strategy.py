"""
Buy 1 Strategy Implementation
This strategy implements the buy_1 trading logic for put spreads
"""

from typing import Dict, Any
from growwapi import GrowwAPI
from bot.utils import Utils


class Buy1Strategy:
    """
    Buy 1 Strategy Class
    Implements the trading logic for the buy_1 strategy (put spreads)
    
    Strategy Logic:
    1. Wait till 9:30 AM
    2. Get first 15-minute candle (9:15-9:30 AM)
    3. If red candle and ((open - close) / open) > 0.001:
       Place put spread at level: 15min_close - 2×ATR + 0.0005×15min_close
       Wait till 2 PM IST
    4. If step 3 not satisfied, wait till 9:45 AM
    5. Get second 15-minute candle (9:30-9:45 AM)
    6. If first candle is red and second candle is green (both > 0.001):
       Place put spread at level: 15min_open - 2×ATR
       Wait till 2 PM IST
    7. If step 6 not satisfied, get first 30-minute candle (9:15-9:45 AM)
    8. If 30-min candle is green and ((close - open) / open) > 0.001:
       Place put spread at level: 15min_open - 2×ATR
       Wait till 2 PM IST
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
        
        print(f"Buy1Strategy initialized with:")
        print(f"  - Exchange: {self.exchange}")
        print(f"  - Trading Symbol: {self.trading_symbol}")
        print(f"  - Expiry: {self.expiry}")
        print(f"  - Spread Gap: {self.spread_gap}")
        print(f"  - Number of Lots: {self.number_of_lots}")
        print(f"  - Lot Size: {self.lot_size}")
        print(f"  - ITM Points: {self.itm_points}")
        print(f"  - ATR: {self.atr}")
    
    def _wait_for_level_and_place_put_spread(self, target_level: float, itm_strike: float, 
                                             quantity: int, level_name: str) -> Dict[str, Any]:
        """
        Monitor spot price and place put spread when target level is reached
        Monitors till 2 PM IST
        
        Args:
            target_level: Target price level to reach (spot must go below this)
            itm_strike: ITM strike price
            quantity: Quantity to trade
            level_name: Name of the level for logging
            
        Returns:
            Dictionary with order placement results
        """
        from datetime import datetime, time
        import time as time_module
        
        print(f"\n--- Monitoring for {level_name} Level ({target_level:.2f}) till 2 PM ---")
        print(f"Waiting for spot price to fall below {target_level:.2f}")
        
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
            
            # Check if target level reached (spot falls below target)
            if spot_price <= target_level:
                print(f"\n✓ {level_name} Level Reached! Spot: {spot_price:.2f} <= Target: {target_level:.2f}")
                print(f"Placing Put Spread...")
                
                # Place put spread order
                order_response = self.utils.place_put_spread(
                    strike_price=itm_strike,
                    quantity=quantity,
                    exchange=self.exchange,
                    trading_symbol=self.trading_symbol,
                    expiry=self.expiry,
                    spread_gap=self.spread_gap
                )
                
                return {
                    "status": "success",
                    "action": "put_spread_placed",
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
        Execute the buy_1 strategy
        
        Strategy Logic:
        1. Wait till 9:30 AM
        2. Get first 15-minute candle (9:15-9:30 AM)
        3. If red candle and ((open - close) / open) > 0.001:
           Place put spread at: 15min_close - 2×ATR + 0.0005×15min_close
        4. If not satisfied, wait till 9:45 AM
        5. Get second 15-minute candle (9:30-9:45 AM)
        6. If first is red and second is green (both > 0.001):
           Place put spread at: 15min_open - 2×ATR
        7. If not satisfied, get first 30-minute candle (9:15-9:45 AM)
        8. If 30-min is green and ((close - open) / open) > 0.001:
           Place put spread at: 15min_open - 2×ATR
        
        Returns:
            Dictionary with execution results
        """
        try:
            from datetime import datetime, time
            import time as time_module
            
            print("\n=== Executing Buy 1 Strategy ===")
            
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
            
            o_1 = first_15min['open']
            h_1 = first_15min['high']
            l_1 = first_15min['low']
            c_1 = first_15min['close']
            
            print(f"First 15-min Candle: O={o_1}, H={h_1}, L={l_1}, C={c_1}")
            
            # Step 3: Check first 15-minute candle conditions
            is_red_1 = o_1 > c_1
            percentage_drop_1 = (o_1 - c_1) / o_1
            condition_1 = percentage_drop_1 > 0.001
            
            print(f"\nFirst 15-Minute Candle Analysis:")
            print(f"  - Is Red (open > close): {is_red_1} ({o_1} > {c_1})")
            print(f"  - Percentage drop: {percentage_drop_1:.4f} ({percentage_drop_1 * 100:.2f}%)")
            print(f"  - ((open - close) / open) > 0.001: {condition_1}")
            
            if is_red_1 and condition_1:
                print("\n✓ First 15-minute candle conditions met!")
                
                # Calculate target level: close - 2×ATR + 0.0005×close
                target_level = c_1 - (2 * self.atr) + (0.0005 * c_1)
                
                print(f"\nTarget Level Calculation:")
                print(f"  - 15-min Close: {c_1}")
                print(f"  - ATR: {self.atr}")
                print(f"  - Target: {c_1} - 2×{self.atr} + 0.0005×{c_1}")
                print(f"  - Target Level: {target_level:.2f}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike - self.itm_points  # ITM for put is below ATM
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike (ATM - {self.itm_points}): {itm_strike}")
                
                # Wait for target level and place put spread
                order_result = self._wait_for_level_and_place_put_spread(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='Close-2×ATR+0.0005×Close'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "first_15min_red",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_15min,
                    "order_result": order_result
                }
            
            # Step 4: If first 15-min conditions not met, wait till 9:45 AM
            print("\n✗ First 15-minute candle conditions not met. Waiting for 9:45 AM...")
            
            current_time = datetime.now().time()
            time_9_45 = time(9, 45)
            
            if current_time < time_9_45:
                wait_seconds = (datetime.combine(datetime.today(), time_9_45) - 
                               datetime.combine(datetime.today(), current_time)).total_seconds()
                print(f"Waiting till 9:45 AM... (Current time: {current_time.strftime('%H:%M:%S')})")
                print(f"Will wait for {wait_seconds:.0f} seconds")
                time_module.sleep(wait_seconds)
                print("✓ 9:45 AM reached")
            
            # Step 5: Get second 15-minute candle (9:30-9:45 AM)
            print("\n--- Analyzing Second 15-Minute Candle (9:30-9:45 AM) ---")
            
            # Fetch candles from 9:30 to 9:45
            from datetime import datetime as dt
            current_date = dt.now()
            start_time = f"{current_date.strftime('%Y-%m-%d')} 09:30:00"
            end_time = f"{current_date.strftime('%Y-%m-%d')} 09:45:00"
            
            exchange_const = self.groww.EXCHANGE_NSE if self.exchange == 'NSE' else self.groww.EXCHANGE_BSE
            trading_symbol = 'NIFTY' if self.exchange == 'NSE' else 'SENSEX'
            
            historical_response = self.groww.get_historical_candle_data(
                trading_symbol=trading_symbol,
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                interval_in_minutes=15
            )
            
            if not historical_response or 'candles' not in historical_response or len(historical_response['candles']) == 0:
                return {
                    "status": "error",
                    "error": "Unable to fetch second 15-minute candle"
                }
            
            second_candle = historical_response['candles'][0]
            o_2 = second_candle[1]
            h_2 = second_candle[2]
            l_2 = second_candle[3]
            c_2 = second_candle[4]
            
            print(f"Second 15-min Candle: O={o_2}, H={h_2}, L={l_2}, C={c_2}")
            
            # Step 6: Check conditions - first red, second green
            is_green_2 = c_2 > o_2
            percentage_rise_2 = (c_2 - o_2) / o_2
            condition_2 = percentage_rise_2 > 0.001
            
            print(f"\nSecond 15-Minute Candle Analysis:")
            print(f"  - First candle is Red: {is_red_1}")
            print(f"  - Second candle is Green (close > open): {is_green_2} ({c_2} > {o_2})")
            print(f"  - Second percentage rise: {percentage_rise_2:.4f} ({percentage_rise_2 * 100:.2f}%)")
            print(f"  - ((close - open) / open) > 0.001: {condition_2}")
            
            if is_red_1 and condition_1 and is_green_2 and condition_2:
                print("\n✓ First red + Second green conditions met!")
                
                # Calculate target level: first_15min_open - 2×ATR
                target_level = o_1 - (2 * self.atr)
                
                print(f"\nTarget Level Calculation:")
                print(f"  - First 15-min Open: {o_1}")
                print(f"  - ATR: {self.atr}")
                print(f"  - Target: {o_1} - 2×{self.atr}")
                print(f"  - Target Level: {target_level:.2f}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike - self.itm_points  # ITM for put is below ATM
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike (ATM - {self.itm_points}): {itm_strike}")
                
                # Wait for target level and place put spread
                order_result = self._wait_for_level_and_place_put_spread(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='Open-2×ATR'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "first_red_second_green",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "first_candle": first_15min,
                    "second_candle": {
                        'open': o_2, 'high': h_2, 'low': l_2, 'close': c_2
                    },
                    "order_result": order_result
                }
            
            # Step 7: If conditions not met, get first 30-minute candle
            print("\n✗ First red + Second green conditions not met. Analyzing 30-minute candle...")
            
            print("\n--- Analyzing First 30-Minute Candle (9:15-9:45 AM) ---")
            first_30min = self.utils.get_first_30min_candle(self.exchange)
            
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
            
            # Step 8: Check 30-minute candle conditions
            is_green_30 = c_30 > o_30
            percentage_rise_30 = (c_30 - o_30) / o_30
            condition_30 = percentage_rise_30 > 0.001
            
            print(f"\n30-Minute Candle Analysis:")
            print(f"  - Is Green (close > open): {is_green_30} ({c_30} > {o_30})")
            print(f"  - Percentage rise: {percentage_rise_30:.4f} ({percentage_rise_30 * 100:.2f}%)")
            print(f"  - ((close - open) / open) > 0.001: {condition_30}")
            
            if is_green_30 and condition_30:
                print("\n✓ 30-minute green candle conditions met!")
                
                # Calculate target level: first_15min_open - 2×ATR
                target_level = o_1 - (2 * self.atr)
                
                print(f"\nTarget Level Calculation:")
                print(f"  - First 15-min Open: {o_1}")
                print(f"  - ATR: {self.atr}")
                print(f"  - Target: {o_1} - 2×{self.atr}")
                print(f"  - Target Level: {target_level:.2f}")
                
                # Get current spot and calculate strikes
                spot_price = self.utils.get_spot_price(self.exchange)
                atm_strike = self.utils.get_atm_strike(spot_price, self.exchange)
                itm_strike = atm_strike - self.itm_points  # ITM for put is below ATM
                
                print(f"\nStrike Calculation:")
                print(f"  - Current Spot: {spot_price}")
                print(f"  - ATM Strike: {atm_strike}")
                print(f"  - ITM Strike (ATM - {self.itm_points}): {itm_strike}")
                
                # Wait for target level and place put spread
                order_result = self._wait_for_level_and_place_put_spread(
                    target_level=target_level,
                    itm_strike=itm_strike,
                    quantity=total_quantity,
                    level_name='Open-2×ATR'
                )
                
                return {
                    "status": "success",
                    "action": order_result.get('action', 'no_trade'),
                    "trigger": "30min_green",
                    "strike": itm_strike,
                    "quantity": total_quantity,
                    "target_level": target_level,
                    "candle_data": first_30min,
                    "order_result": order_result
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
