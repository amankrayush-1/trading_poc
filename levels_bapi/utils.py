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

    def get_nifty_first_15min_candle(self) -> dict:
        """
        Get the first 15-minute candle (9:15 AM to 9:30 AM) for NIFTY.
        
        This method fetches historical candle data specifically for the first 15 minutes
        of the trading session using the get_historical_candle_data API.

        Returns:
            dict: Dictionary with 'open', 'high', 'low', 'close', 'volume' keys
                  or None if error occurs
        """
        try:
            from datetime import datetime, time
            
            # Get current date
            current_date = datetime.now()
            
            # Check if current time is after 9:30 AM
            current_time = datetime.now().time()
            first_candle_end = time(9, 30)
            
            # If before 9:30 AM, we can't get the first candle yet
            if current_time < first_candle_end:
                print(f"Market first 15-min candle not yet complete. Current time: {current_time}")
                return None
            
            # Format times for the first 15 minutes of trading (9:15 AM to 9:30 AM IST)
            start_time = f"{current_date.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_date.strftime('%Y-%m-%d')} 09:30:00"
            
            # Fetch historical candle data for the specific time range
            historical_response = self.groww.get_historical_candle_data(
                trading_symbol="NIFTY",
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                interval_in_minutes=15  # 15-minute interval
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the first candle (9:15-9:30 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4]
                }
            else:
                print(f"No candle data found for NIFTY on {current_date.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching first 15-min candle data: {e}")
            return None

    def get_previous_trading_day(self, reference_date=None):
        """
        Get the previous trading day (excluding weekends and holidays)
        
        Args:
            reference_date: datetime object or None (uses today if None)
            
        Returns:
            datetime: Previous trading day
        """
        from datetime import datetime, timedelta
        import csv
        
        # Use today if no reference date provided
        if reference_date is None:
            reference_date = datetime.now()
        
        # Convert to date if datetime
        if isinstance(reference_date, datetime):
            current_date = reference_date.date()
        else:
            current_date = reference_date
        
        # Load market holidays from CSV
        holidays = set()
        try:
            with open('bhavcopy/holiday.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse date in DD-MMM-YYYY format (e.g., 26-Feb-2025)
                    date_str = row['Date']
                    holiday_date = datetime.strptime(date_str, '%d-%b-%Y').date()
                    holidays.add(holiday_date)
        except Exception as e:
            print(f"Warning: Could not load holidays: {e}")
        
        # Start from previous day
        previous_day = current_date - timedelta(days=1)
        
        # Keep going back until we find a trading day
        while True:
            # Check if it's a weekend (Saturday=5, Sunday=6)
            if previous_day.weekday() >= 5:
                previous_day -= timedelta(days=1)
                continue
            
            # Check if it's a holiday
            if previous_day in holidays:
                previous_day -= timedelta(days=1)
                continue
            
            # Found a trading day
            return datetime.combine(previous_day, datetime.min.time())

    def get_ohlc_previous_trading_day(self):
        """
        Get OHLC data for the previous trading day for NIFTY
        
        This method:
        1. Finds the last trading day (excluding weekends and holidays)
        2. Fetches OHLC data for that day using historical candle data
        
        Returns:
            dict: Dictionary with 'date', 'open', 'high', 'low', 'close', 'volume' keys
                  or None if error occurs
        """
        try:
            from datetime import datetime
            
            # Get previous trading day
            prev_trading_day = self.get_previous_trading_day()
            
            print(f"Fetching OHLC for previous trading day: {prev_trading_day.strftime('%Y-%m-%d %A')}")
            
            # Format times for the entire trading session (9:15 AM to 3:30 PM IST)
            start_time = f"{prev_trading_day.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{prev_trading_day.strftime('%Y-%m-%d')} 15:30:00"
            
            # Fetch historical candle data for the entire day (1440 minutes = 1 day)
            historical_response = self.groww.get_historical_candle_data(
                trading_symbol="NIFTY",
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                interval_in_minutes=1440  # Daily candle
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the daily candle
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                
                result = {
                    'date': prev_trading_day.strftime('%Y-%m-%d'),
                    'day': prev_trading_day.strftime('%A'),
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
                
                print(f"✓ OHLC Data for {result['date']} ({result['day']}):")
                print(f"  Open:   {result['open']}")
                print(f"  High:   {result['high']}")
                print(f"  Low:    {result['low']}")
                print(f"  Close:  {result['close']}")
                print(f"  Volume: {result['volume']}")
                
                return result
            else:
                print(f"No candle data found for NIFTY on {prev_trading_day.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching previous trading day OHLC: {e}")
            import traceback
            traceback.print_exc()
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
