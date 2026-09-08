"""
Level Trading Strategy

Monitors 15-minute candles of the underlying spot price against a
pre-configured level for both the call side and the put side:

  - Call side: if a 15-min candle's high touches (>=) the call level but the
    candle closes below the call level, sell a call credit spread
    (sell the configured `call.strike` CE, buy a CE `call.spread_gap` points
    higher as hedge).
  - Put side: if a 15-min candle's low touches (<=) the put level but the
    candle closes above the put level, sell a put credit spread
    (sell the configured `put.strike` PE, buy a PE `put.spread_gap` points
    lower as hedge).

`call.strike` / `put.strike` must be the full Groww option trading symbol to
sell, e.g. "NIFTY26MAR2524200CE". The hedge leg is derived from it by
replacing just the strike digits, so no separate expiry handling is needed.

Only one trade is taken per run - as soon as either side triggers, the
strategy places the spread order and stops monitoring for the rest of the
day.
"""

import re
import time
from datetime import datetime, time as dtime
from typing import Any, Dict


MONTH_PATTERN = r'JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC'


class LevelTradingStrategy:

    MARKET_START = dtime(9, 15)
    LAST_ENTRY_CUTOFF = dtime(15, 15)
    POLL_INTERVAL_SECONDS = 15

    def __init__(self, groww, utils, config: Dict[str, Any]):
        self.groww = groww
        self.utils = utils
        self.config = config

        self.trading_symbol = str(config.get('trading_symbol', 'nifty'))
        self.exchange = str(config.get('exchange', 'nse'))
        self.number_of_lots = int(config.get('number_of_lots', 1))
        self.lot_size = int(config.get('lot_size', 65))
        self.quantity = self.number_of_lots * self.lot_size

        self.call_config = config.get('call', {})
        self.put_config = config.get('put', {})

        self.call_level = float(self.call_config['level'])
        self.call_spread_gap = int(self.call_config.get('spread_gap', 200))
        self.call_strike_symbol = self._require_symbol(self.call_config.get('strike'), 'call.strike')

        self.put_level = float(self.put_config['level'])
        self.put_spread_gap = int(self.put_config.get('spread_gap', 200))
        self.put_strike_symbol = self._require_symbol(self.put_config.get('strike'), 'put.strike')

    def _require_symbol(self, strike: Any, field_name: str) -> str:
        if not strike:
            raise ValueError(
                f"'{field_name}' must be the full option trading symbol to sell "
                f"(e.g. 'NIFTY26MAR2524200CE'), got: {strike!r}"
            )
        return str(strike).upper()

    def _parse_option_symbol(self, symbol: str) -> Dict[str, Any]:
        """Split a full option trading symbol like 'NIFTY26MAR2524200CE' into
        its underlying+expiry prefix, numeric strike, and option type, without
        needing to know how the expiry portion itself is encoded."""
        pattern = re.compile(
            rf'^(?P<prefix>{re.escape(self.trading_symbol.upper())}\d{{2}}(?:{MONTH_PATTERN})\d{{2}})'
            rf'(?P<strike>\d+)(?P<option_type>CE|PE)$'
        )
        match = pattern.match(symbol)
        if not match:
            raise ValueError(f"Unrecognized option symbol format: {symbol}")

        return {
            'prefix': match.group('prefix'),
            'strike': int(match.group('strike')),
            'option_type': match.group('option_type'),
        }

    def _build_symbol(self, prefix: str, strike: int, option_type: str) -> str:
        return f"{prefix}{strike}{option_type}"

    def _place_spread(self, sell_symbol: str, buy_symbol: str) -> Dict[str, Any]:
        exchange_const = self.groww.EXCHANGE_NSE if self.exchange.upper() == 'NSE' else self.groww.EXCHANGE_BSE

        buy_response = self.groww.place_order(
            trading_symbol=buy_symbol,
            quantity=self.quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )
        print(f"Buy Order: {buy_symbol} - {buy_response}")

        sell_response = self.groww.place_order(
            trading_symbol=sell_symbol,
            quantity=self.quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )
        print(f"Sell Order: {sell_symbol} - {sell_response}")

        return {'buy_order': buy_response, 'sell_order': sell_response}

    def _place_call_spread(self) -> Dict[str, Any]:
        parsed = self._parse_option_symbol(self.call_strike_symbol)
        buy_symbol = self._build_symbol(parsed['prefix'], parsed['strike'] + self.call_spread_gap, 'CE')
        return self._place_spread(sell_symbol=self.call_strike_symbol, buy_symbol=buy_symbol)

    def _place_put_spread(self) -> Dict[str, Any]:
        parsed = self._parse_option_symbol(self.put_strike_symbol)
        buy_symbol = self._build_symbol(parsed['prefix'], parsed['strike'] - self.put_spread_gap, 'PE')
        return self._place_spread(sell_symbol=self.put_strike_symbol, buy_symbol=buy_symbol)

    def _is_call_triggered(self, candle: Dict[str, Any]) -> bool:
        return candle['high'] >= self.call_level and candle['close'] < self.call_level

    def _is_put_triggered(self, candle: Dict[str, Any]) -> bool:
        return candle['low'] <= self.put_level and candle['close'] > self.put_level

    def execute(self) -> Dict[str, Any]:
        try:
            print(f"Call level: {self.call_level}, sell symbol: {self.call_strike_symbol}, spread_gap: {self.call_spread_gap}")
            print(f"Put level: {self.put_level}, sell symbol: {self.put_strike_symbol}, spread_gap: {self.put_spread_gap}")

            last_seen_timestamp = None

            while True:
                now = datetime.now()

                if now.time() < self.MARKET_START:
                    time.sleep(self.POLL_INTERVAL_SECONDS)
                    continue

                if now.time() >= self.LAST_ENTRY_CUTOFF:
                    print("⚠ Reached last-entry cutoff without a trade trigger. Stopping.")
                    return {"status": "success", "action": "no_trade", "reason": "cutoff_reached"}

                candle = self.utils.get_15min_candle(self.exchange)

                if candle and candle.get('timestamp') != last_seen_timestamp:
                    last_seen_timestamp = candle.get('timestamp')
                    print(f"New 15-min candle: {candle}")

                    if self._is_call_triggered(candle):
                        print(f"✓ Call level {self.call_level} touched and closed below. Placing call spread.")
                        order_result = self._place_call_spread()
                        return {
                            "status": "success",
                            "action": "call_spread_placed",
                            "trigger_candle": candle,
                            "sell_symbol": self.call_strike_symbol,
                            "order_result": order_result,
                        }

                    if self._is_put_triggered(candle):
                        print(f"✓ Put level {self.put_level} touched and closed above. Placing put spread.")
                        order_result = self._place_put_spread()
                        return {
                            "status": "success",
                            "action": "put_spread_placed",
                            "trigger_candle": candle,
                            "sell_symbol": self.put_strike_symbol,
                            "order_result": order_result,
                        }

                time.sleep(self.POLL_INTERVAL_SECONDS)

        except Exception as e:
            print(f"✗ Error in LevelTradingStrategy: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
