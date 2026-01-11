from growwapi import GrowwAPI

from constant import expiry, spread_gap


class Utils:

    def __init__(self, groww: GrowwAPI):
        self.groww = groww

    def get_nifty_spot_price(self) -> float:
        ltp_response = self.groww.get_ltp(
            segment=self.groww.SEGMENT_CASH,
            exchange_trading_symbols="NSE_NIFTY"
        )
        return ltp_response['NSE_NIFTY']

    def get_nifty_15min_candle(self) -> dict:
        """
        Get 15-minute OHLC candle data for NIFTY
        Returns: dict with 'open', 'high', 'low', 'close' keys
        """
        try:
            ohlc_response = self.groww.get_ohlc(
                segment=self.groww.SEGMENT_CASH,
                exchange_trading_symbols="NSE_NIFTY",
                interval="15m"  # 15-minute interval
            )
            if ohlc_response and 'NSE_NIFTY' in ohlc_response:
                candle_data = ohlc_response['NSE_NIFTY']
                return {
                    'open': candle_data.get('open'),
                    'high': candle_data.get('high'),
                    'low': candle_data.get('low'),
                    'close': candle_data.get('close')
                }
        except Exception as e:
            print(f"Error fetching 15-min candle data: {e}")
        return None

    def get_atm_strike(self, spot_price):
        return round(float(spot_price) / 50) * 50

    def place_call_spread(self, strike_price, quantity):
        place_buy_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price + spread_gap}CE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )

        print(place_buy_order_response)

        place_sell_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price}CE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )

        print(place_sell_order_response)

    def close_call_spread(self, strike_price, quantity):
        place_buy_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price}CE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )

        print(place_buy_order_response)

        place_sell_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price + spread_gap}CE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )

        print(place_sell_order_response)

    def place_put_spread(self, strike_price, quantity):
        place_buy_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price - spread_gap}PE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )

        print(place_buy_order_response)

        place_sell_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price}PE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )

        print(place_sell_order_response)

    def close_put_spread(self, strike_price, quantity):
        place_buy_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price}PE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )

        print(place_buy_order_response)

        place_sell_order_response = self.groww.place_order(
            trading_symbol=f"NIFTY{expiry}{strike_price - spread_gap}PE",
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=self.groww.EXCHANGE_NSE,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )

        print(place_sell_order_response)

    def close_all_fno_trades(self):
        """
        Close all open FNO (Futures & Options) trades by squaring off positions
        This method:
        1. Fetches all open positions in FNO segment
        2. For each position, places a reverse order to close it
        3. Returns summary of closed positions
        """
        try:
            # Get all positions
            positions_response = self.groww.get_positions()
            
            if not positions_response or 'positions' not in positions_response:
                print("No positions found or unable to fetch positions")
                return {"status": "error", "message": "Unable to fetch positions"}
            
            positions = positions_response['positions']
            fno_positions = [pos for pos in positions if pos.get('segment') == self.groww.SEGMENT_FNO]
            
            if not fno_positions:
                print("No open FNO positions found")
                return {"status": "success", "message": "No FNO positions to close", "closed_count": 0}
            
            print(f"Found {len(fno_positions)} FNO position(s) to close")
            closed_positions = []
            failed_positions = []
            
            for position in fno_positions:
                try:
                    trading_symbol = position.get('trading_symbol')
                    net_quantity = position.get('net_quantity', 0)
                    
                    # Skip if net quantity is 0 (already squared off)
                    if net_quantity == 0:
                        print(f"Skipping {trading_symbol} - already squared off")
                        continue
                    
                    # Determine transaction type (reverse of current position)
                    # If net_quantity is positive (long position), we need to SELL
                    # If net_quantity is negative (short position), we need to BUY
                    if net_quantity > 0:
                        transaction_type = self.groww.TRANSACTION_TYPE_SELL
                        quantity = abs(net_quantity)
                    else:
                        transaction_type = self.groww.TRANSACTION_TYPE_BUY
                        quantity = abs(net_quantity)
                    
                    print(f"Closing position: {trading_symbol}, Quantity: {quantity}, Type: {transaction_type}")
                    
                    # Place order to close position
                    close_order_response = self.groww.place_order(
                        trading_symbol=trading_symbol,
                        quantity=quantity,
                        validity=self.groww.VALIDITY_DAY,
                        exchange=self.groww.EXCHANGE_NSE,
                        segment=self.groww.SEGMENT_FNO,
                        product=position.get('product', self.groww.PRODUCT_MIS),
                        order_type=self.groww.ORDER_TYPE_MARKET,
                        transaction_type=transaction_type,
                    )
                    
                    print(f"✓ Closed {trading_symbol}: {close_order_response}")
                    closed_positions.append({
                        'symbol': trading_symbol,
                        'quantity': quantity,
                        'response': close_order_response
                    })
                    
                except Exception as e:
                    print(f"✗ Failed to close {trading_symbol}: {e}")
                    failed_positions.append({
                        'symbol': trading_symbol,
                        'error': str(e)
                    })
            
            # Summary
            summary = {
                "status": "success",
                "total_positions": len(fno_positions),
                "closed_count": len(closed_positions),
                "failed_count": len(failed_positions),
                "closed_positions": closed_positions,
                "failed_positions": failed_positions
            }
            
            print(f"\n=== Summary ===")
            print(f"Total FNO positions: {summary['total_positions']}")
            print(f"Successfully closed: {summary['closed_count']}")
            print(f"Failed to close: {summary['failed_count']}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Error closing FNO trades: {e}"
            print(error_msg)
            return {"status": "error", "message": error_msg}
