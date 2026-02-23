import sys
import time

from growwapi import GrowwAPI

from levels_bapi.utils import Utils
from spot_trade.constant import bald_size


class CallTrade:
    def __init__(self, groww: GrowwAPI):
        self.utils = Utils(groww)
        self.opened_first_trade = False
        self.opened_second_trade = False
        self.close_call_spreads_trade = False
        self.call_spread_strike_price_1 = None
        self.call_spread_quantity_1 = None
        self.call_spread_strike_price_2 = None
        self.call_spread_quantity_2 = None

    def call_spread(self):
        print("CALL Spread")
        self.get_levels()
        self.open_first_call_spread_trade()
        self.open_second_call_spread_trade()
        self.close_all_call_spreads_trades()

    def get_levels(self):
        '''
        Wait until 9:30 AM IST, then fetch the first 15-minute candle
        and calculate trade levels based on candle pattern
        '''
        from datetime import datetime, time as dt_time

        # Wait until 9:30 AM IST
        target_time = dt_time(9, 30, 0)  # 9:30:00 AM

        while True:
            current_time = datetime.now().time()

            if current_time >= target_time:
                print(f"✓ Market time reached: {current_time.strftime('%H:%M:%S')}")
                break

            time.sleep(1)  # Sleep for 1 second

        # Fetch the first 15-minute candle (9:15-9:30 AM)
        print("Fetching first 15-minute candle (9:15-9:30 AM)...")
        ohlc = self.utils.get_nifty_first_15min_candle()

        if not ohlc:
            print("✗ Failed to fetch first 15-minute candle")
            sys.exit(1)

        print(f"✓ First candle: Open={ohlc['open']}, High={ohlc['high']}, "
              f"Low={ohlc['low']}, Close={ohlc['close']}")

        # Check if it's a bald candle
        body_size = abs(ohlc['close'] - ohlc['open'])
        upper_wick = ohlc['high'] - max(ohlc['open'], ohlc['close'])
        lower_wick = min(ohlc['open'], ohlc['close']) - ohlc['low']
        total_wicks = upper_wick + lower_wick

        is_bald_candle = (body_size > bald_size) and (total_wicks < body_size)

        if is_bald_candle & ohlc['open'] < ohlc['close']:
            print(f"✓ Green Bald candle detected (Body: {body_size:.2f}, Wicks: {total_wicks:.2f})")
            last_dat
            self.trade_level = ohlc.get('close') - 2 * atr + 0.0005 * ohlc.get('close')
            self.sl_level = ohlc.get('close') - 3 * atr
            print(f"Trade Level: {self.trade_level:.2f}, SL Level: {self.sl_level:.2f}")
        else:
            print(f"✗ Not a bald candle (Body: {body_size:.2f}, Wicks: {total_wicks:.2f}) - Doji pattern detected")
            sys.exit(1)

    def open_first_call_spread_trade(self):
        while not self.opened_first_trade:
            spot_price = self.utils.get_nifty_spot_price()
            if not spot_price:
                continue
            print(f"Current Nifty Spot: {spot_price}")

            if spot_price >= call_spread_level_1:
                print(f"Sell trigger hit! Placing spread at {spot_price}")
                quantity = call_quantity_in_lots
                if call_spread_level_2:
                    quantity = quantity / 2
                atm_strike = self.utils.get_atm_strike(spot_price)
                print("Atm strike:", atm_strike)
                if quantity == 0:
                    print("quantity can't be zero")
                    exit(1)
                self.utils.place_call_spread(atm_strike, quantity * 65)
                self.opened_first_trade = True
                self.call_spread_strike_price_1 = atm_strike
                self.call_spread_quantity_1 = quantity

            # Sleep for 1 second before next check
            time.sleep(1)

    def open_second_call_spread_trade(self):
        if call_spread_level_2:
            while not self.opened_second_trade:
                spot_price = self.utils.get_nifty_spot_price()
                if not spot_price:
                    continue
                print(f"Current Nifty Spot: {spot_price}")

                if spot_price >= call_spread_level_2:
                    print(f"Sell trigger hit! Placing spread at {spot_price}")
                    quantity = call_quantity_in_lots / 2
                    atm_strike = self.utils.get_atm_strike(spot_price)
                    print("Atm strike:", atm_strike)
                    self.utils.place_call_spread(atm_strike, quantity * 65)
                    self.opened_second_trade = True
                    self.call_spread_strike_price_2 = atm_strike
                    self.call_spread_quantity_2 = quantity

                # Sleep for 1 second before next check
                time.sleep(1)

    def close_all_call_spreads_trades(self):
        """
        Close all call spread trades if 15-minute candle open or high is greater than call_sl_level
        """
        if self.opened_first_trade or self.opened_second_trade:
            while not self.close_call_spreads_trade:
                # Get 15-minute candle data
                candle_data = self.utils.get_nifty_15min_candle()

                if not candle_data:
                    print("Unable to fetch candle data, retrying...")
                    time.sleep(5)
                    continue

                candle_open = candle_data.get('open')
                candle_close = candle_data.get('close')

                print(f"15-min Candle - Open: {candle_open}, High: {candle_close}, SL Level: {call_sl_level}")

                # Check if candle open or high breaches the stop loss level
                if (candle_open and candle_open >= call_sl_level) or (candle_close and candle_close >= call_sl_level):
                    print(f"Stop Loss triggered! Candle Open: {candle_open}, High: {candle_close}")

                    # Close first trade if opened
                    if self.opened_first_trade:
                        print(f"Closing first call spread trade at strike {self.call_spread_strike_price_1}")
                        self.utils.close_call_spread(self.call_spread_strike_price_1, self.call_spread_quantity_1 * 65)

                    # Close second trade if opened
                    if self.opened_second_trade:
                        print(f"Closing second call spread trade at strike {self.call_spread_strike_price_2}")
                        self.utils.close_call_spread(self.call_spread_strike_price_2, self.call_spread_quantity_2 * 65)

                    self.close_call_spreads_trade = True
                    print("All call spread trades closed successfully")

                # Sleep for a reasonable interval before checking again (e.g., 30 seconds)
                # This prevents excessive API calls while still monitoring the candle
                time.sleep(30)
