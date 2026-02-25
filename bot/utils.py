from growwapi import GrowwAPI

class Utils:

    def __init__(self, groww: GrowwAPI):
        self.groww = groww
    
    def _get_candle_interval_constant(self, interval_minutes: int) -> str:
        """
        Convert interval in minutes to Groww API candle interval constant
        
        Args:
            interval_minutes: Interval in minutes (e.g., 1, 3, 5, 15, 30, 60, 1440)
            
        Returns:
            str: Groww API candle interval constant
        """
        interval_map = {
            1: self.groww.CANDLE_INTERVAL_MIN_1,
            2: self.groww.CANDLE_INTERVAL_MIN_2,
            3: self.groww.CANDLE_INTERVAL_MIN_3,
            5: self.groww.CANDLE_INTERVAL_MIN_5,
            10: self.groww.CANDLE_INTERVAL_MIN_10,
            15: self.groww.CANDLE_INTERVAL_MIN_15,
            30: self.groww.CANDLE_INTERVAL_MIN_30,
            60: self.groww.CANDLE_INTERVAL_HOUR_1,
            240: self.groww.CANDLE_INTERVAL_HOUR_4,
            1440: self.groww.CANDLE_INTERVAL_DAY,
            10080: self.groww.CANDLE_INTERVAL_WEEK,
        }
        
        if interval_minutes not in interval_map:
            raise ValueError(f"Unsupported interval: {interval_minutes} minutes. Supported: {list(interval_map.keys())}")
        
        return interval_map[interval_minutes]
    
    def get_spot_price(self, exchange: str) -> float:
        exchange_upper = exchange.upper()
        
        if exchange_upper == 'NSE':
            # Get NIFTY 50 LTP
            exchange_trading_symbol = "NSE_NIFTY"
            ltp_response = self.groww.get_ltp(
                segment=self.groww.SEGMENT_CASH,
                exchange_trading_symbols=exchange_trading_symbol
            )
            # Response format: {'NSE_NIFTY': 25581.75}
            return ltp_response[exchange_trading_symbol]
        
        elif exchange_upper == 'BSE':
            # Get SENSEX LTP
            exchange_trading_symbol = "BSE_SENSEX"
            ltp_response = self.groww.get_ltp(
                segment=self.groww.SEGMENT_CASH,
                exchange_trading_symbols=exchange_trading_symbol
            )
            # Response format: {'BSE_SENSEX': 85000.00}
            return ltp_response[exchange_trading_symbol]
        
        else:
            raise ValueError(f"Unsupported exchange: {exchange}. Supported exchanges: NSE, BSE")

    def get_candle(self, exchange: str, interval_minutes: int) -> dict:
        """
        Get OHLC candle data for the specified exchange and interval
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            interval_minutes: Candle interval in minutes (e.g., 3, 15)
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error
            
        Note: Fetches the most recent completed candle using historical data API
        """
        try:
            from datetime import datetime, timedelta
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Calculate time range for the most recent candle
            now = datetime.now()
            # Get data for last hour to ensure we have the latest candle
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Fetch historical candle data
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self._get_candle_interval_constant(interval_minutes)
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the most recent candle (last one in the list)
                candle = historical_response['candles'][-1]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for {trading_symbol} on {exchange}")
                return None
                
        except Exception as e:
            print(f"Error fetching {interval_minutes}-min candle data: {e}")
            return None
    
    def get_3min_candle(self, exchange: str) -> dict:
        """
        Get 3-minute OHLC candle data for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys
        """
        return self.get_candle(exchange, interval_minutes=3)
    
    def get_15min_candle(self, exchange: str) -> dict:
        """
        Get 15-minute OHLC candle data for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys
        """
        return self.get_candle(exchange, interval_minutes=15)
    
    def get_nifty_15min_candle(self) -> dict:
        """
        Get 15-minute OHLC candle data for NIFTY (backward compatibility)
        Returns: dict with 'open', 'high', 'low', 'close', 'volume' keys
        """
        return self.get_15min_candle('NSE')
    
    def get_first_3min_candle(self, exchange: str) -> dict:
        """
        Get the first 3-minute candle (9:15 AM to 9:18 AM IST) for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error/not available
        """
        try:
            from datetime import datetime, time
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Get current date and time
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            
            # Check if current time is after 9:18 AM
            first_candle_end = time(9, 18)
            
            # If before 9:18 AM, the first 3-min candle is not yet complete
            if current_time < first_candle_end:
                print(f"First 3-min candle not yet complete. Current time: {current_time.strftime('%H:%M:%S')}")
                return None
            
            # Format times for the first 3 minutes of trading (9:15 AM to 9:18 AM IST)
            start_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:18:00"
            
            # Fetch historical candle data for the specific time range
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_3
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the first candle (9:15-9:18 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for {trading_symbol} on {current_datetime.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching first 3-min candle data: {e}")
            return None
    
    def get_first_15min_candle(self, exchange: str) -> dict:
        """
        Get the first 15-minute candle (9:15 AM to 9:30 AM IST) for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error/not available
        """
        try:
            from datetime import datetime, time
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Get current date and time
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            
            # Check if current time is after 9:30 AM
            first_candle_end = time(9, 30)
            
            # If before 9:30 AM, the first 15-min candle is not yet complete
            if current_time < first_candle_end:
                print(f"First 15-min candle not yet complete. Current time: {current_time.strftime('%H:%M:%S')}")
                return None
            
            # Format times for the first 15 minutes of trading (9:15 AM to 9:30 AM IST)
            start_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:30:00"
            
            # Fetch historical candle data for the specific time range
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the first candle (9:15-9:30 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for {trading_symbol} on {current_datetime.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching first 15-min candle data: {e}")
            return None
    
    def get_first_30min_candle(self, exchange: str) -> dict:
        """
        Get the first 30-minute candle (9:15 AM to 9:45 AM IST) for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error/not available
        """
        try:
            from datetime import datetime, time
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Get current date and time
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            
            # Check if current time is after 9:45 AM
            first_candle_end = time(9, 45)
            
            # If before 9:45 AM, the first 30-min candle is not yet complete
            if current_time < first_candle_end:
                print(f"First 30-min candle not yet complete. Current time: {current_time.strftime('%H:%M:%S')}")
                return None
            
            # Format times for the first 30 minutes of trading (9:15 AM to 9:45 AM IST)
            start_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:45:00"
            
            # Fetch historical candle data for the specific time range
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_30
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the first candle (9:15-9:45 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for {trading_symbol} on {current_datetime.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching first 30-min candle data: {e}")
            return None
    
    def get_second_15min_candle(self, exchange: str) -> dict:
        """
        Get the second 15-minute candle (9:30 AM to 9:45 AM IST) for the specified exchange
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error/not available
        """
        try:
            from datetime import datetime, time
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Get current date and time
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            
            # Check if current time is after 9:45 AM
            second_candle_end = time(9, 45)
            
            # If before 9:45 AM, the second 15-min candle is not yet complete
            if current_time < second_candle_end:
                print(f"Second 15-min candle not yet complete. Current time: {current_time.strftime('%H:%M:%S')}")
                return None
            
            # Format times for the second 15 minutes of trading (9:30 AM to 9:45 AM IST)
            start_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:30:00"
            end_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:45:00"
            
            # Fetch historical candle data for the specific time range
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the second candle (9:30-9:45 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for {trading_symbol} on {current_datetime.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching second 15-min candle data: {e}")
            return None


    def get_atm_strike(self, spot_price, exchange: str) -> float:
        """
        Calculate ATM (At The Money) strike price based on spot price and exchange
        
        Args:
            spot_price: Current spot price of the underlying
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            float - Nearest ATM strike price
            
        Strike price gaps:
            - NSE: 50 points (NIFTY, BANKNIFTY, etc.)
            - BSE: 100 points (SENSEX, etc.)
        """
        exchange_upper = exchange.upper()
        
        if exchange_upper == 'NSE':
            strike_gap = 50
        elif exchange_upper == 'BSE':
            strike_gap = 100
        else:
            raise ValueError(f"Unsupported exchange: {exchange}. Supported exchanges: NSE, BSE")
        
        return round(float(spot_price) / strike_gap) * strike_gap
    
    def get_ema_33_15min(self, exchange: str) -> dict:
        """
        Calculate EMA 33 for high, close, open, and low of 15-minute candles
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'ema_open', 'ema_high', 'ema_low', 'ema_close', 'candles_used' keys or None if error
            
        Note: EMA 33 requires at least 33 candles for accurate calculation.
              Fetches last 100 candles to ensure sufficient data.
        """
        try:
            from datetime import datetime, timedelta
            
            exchange_upper = exchange.upper()
            
            # Determine trading symbol based on exchange
            if exchange_upper == 'NSE':
                trading_symbol = 'NIFTY'
                exchange_const = self.groww.EXCHANGE_NSE
            elif exchange_upper == 'BSE':
                trading_symbol = 'SENSEX'
                exchange_const = self.groww.EXCHANGE_BSE
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
            
            # Calculate time range - get enough data for EMA 33 calculation
            # Fetch last 100 candles (15 min each = 1500 minutes = 25 hours of trading)
            now = datetime.now()
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            # Go back approximately 7 trading days to get 100 candles
            start_time = (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Fetch historical candle data
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{trading_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_CASH,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if not historical_response or 'candles' not in historical_response or len(historical_response['candles']) < 33:
                print(f"Insufficient candle data for EMA 33 calculation. Need at least 33 candles, got {len(historical_response.get('candles', []))}")
                return None
            
            candles = historical_response['candles']
            
            # Extract OHLC data
            # Candle format: [timestamp, open, high, low, close, volume]
            opens = [candle[1] for candle in candles]
            highs = [candle[2] for candle in candles]
            lows = [candle[3] for candle in candles]
            closes = [candle[4] for candle in candles]
            
            # Calculate EMA 33 for each OHLC component
            ema_open = self._calculate_ema(opens, period=33)
            ema_high = self._calculate_ema(highs, period=33)
            ema_low = self._calculate_ema(lows, period=33)
            ema_close = self._calculate_ema(closes, period=33)
            
            return {
                'ema_open': ema_open,
                'ema_high': ema_high,
                'ema_low': ema_low,
                'ema_close': ema_close,
                'candles_used': len(candles)
            }
            
        except Exception as e:
            print(f"Error calculating EMA 33 for 15-min candles: {e}")
            return None
    
    def _calculate_ema(self, data: list, period: int) -> float:
        """
        Calculate Exponential Moving Average (EMA) for given data
        
        Args:
            data: List of price values
            period: EMA period (e.g., 33)
            
        Returns:
            float: Current EMA value
            
        Formula:
            EMA = (Close - EMA(previous)) * multiplier + EMA(previous)
            where multiplier = 2 / (period + 1)
        """
        if len(data) < period:
            raise ValueError(f"Insufficient data for EMA {period}. Need at least {period} values, got {len(data)}")
        
        # Calculate multiplier
        multiplier = 2 / (period + 1)
        
        # Start with SMA (Simple Moving Average) for the first EMA value
        sma = sum(data[:period]) / period
        ema = sma
        
        # Calculate EMA for remaining values
        for i in range(period, len(data)):
            ema = (data[i] - ema) * multiplier + ema
        
        return ema

    def place_call_spread(self, strike_price: float, quantity: int, exchange: str,
                         trading_symbol: str, expiry: str, spread_gap: int):
        """
        Place a call spread order (buy higher strike, sell lower strike)
        
        Args:
            strike_price: ATM or base strike price (used directly, not calculated)
            quantity: Number of lots to trade
            exchange: Exchange name ('NSE' or 'BSE')
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX', 'BANKNIFTY')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            spread_gap: Gap between strikes (e.g., 200)
            
        Returns:
            dict with buy and sell order responses
        """
        exchange_upper = exchange.upper()
        
        # Determine exchange constant
        exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
        
        # Calculate strikes directly from provided strike_price
        buy_strike = int(strike_price + spread_gap)
        sell_strike = int(strike_price)
        
        # Generate option symbols
        buy_symbol = self._format_option_symbol(trading_symbol, expiry, buy_strike, 'CE')
        sell_symbol = self._format_option_symbol(trading_symbol, expiry, sell_strike, 'CE')
        
        # Buy higher strike (OTM)
        place_buy_order_response = self.groww.place_order(
            trading_symbol=buy_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )
        print(f"Buy Order: {buy_symbol} - {place_buy_order_response}")

        # Sell ATM strike
        place_sell_order_response = self.groww.place_order(
            trading_symbol=sell_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )
        print(f"Sell Order: {sell_symbol} - {place_sell_order_response}")
        
        return {
            'buy_order': place_buy_order_response,
            'sell_order': place_sell_order_response
        }

    def close_call_spread(self, strike_price: float, quantity: int, exchange: str,
                         trading_symbol: str, expiry: str, spread_gap: int):
        """
        Close a call spread position (reverse of place_call_spread)
        
        Args:
            strike_price: ATM or base strike price (used directly, not calculated)
            quantity: Number of lots to trade
            exchange: Exchange name ('NSE' or 'BSE')
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX', 'BANKNIFTY')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            spread_gap: Gap between strikes (e.g., 200)
            
        Returns:
            dict with buy and sell order responses
        """
        exchange_upper = exchange.upper()
        
        # Determine exchange constant
        exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
        
        # Calculate strikes directly from provided strike_price
        buy_strike = int(strike_price)
        sell_strike = int(strike_price + spread_gap)
        
        # Generate option symbols
        buy_symbol = self._format_option_symbol(trading_symbol, expiry, buy_strike, 'CE')
        sell_symbol = self._format_option_symbol(trading_symbol, expiry, sell_strike, 'CE')
        
        # Buy back ATM strike (close short position)
        place_buy_order_response = self.groww.place_order(
            trading_symbol=buy_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )
        print(f"Buy Order: {buy_symbol} - {place_buy_order_response}")

        # Sell higher strike (close long position)
        place_sell_order_response = self.groww.place_order(
            trading_symbol=sell_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )
        print(f"Sell Order: {sell_symbol} - {place_sell_order_response}")
        
        return {
            'buy_order': place_buy_order_response,
            'sell_order': place_sell_order_response
        }

    def place_put_spread(self, strike_price: float, quantity: int, exchange: str,
                        trading_symbol: str, expiry: str, spread_gap: int):
        """
        Place a put spread order (buy lower strike, sell higher strike)
        
        Args:
            strike_price: ATM or base strike price (used directly, not calculated)
            quantity: Number of lots to trade
            exchange: Exchange name ('NSE' or 'BSE')
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX', 'BANKNIFTY')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            spread_gap: Gap between strikes (e.g., 200)
            
        Returns:
            dict with buy and sell order responses
        """
        exchange_upper = exchange.upper()
        
        # Determine exchange constant
        exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
        
        # Calculate strikes directly from provided strike_price
        buy_strike = int(strike_price - spread_gap)
        sell_strike = int(strike_price)
        
        # Generate option symbols
        buy_symbol = self._format_option_symbol(trading_symbol, expiry, buy_strike, 'PE')
        sell_symbol = self._format_option_symbol(trading_symbol, expiry, sell_strike, 'PE')
        
        # Buy lower strike (OTM)
        place_buy_order_response = self.groww.place_order(
            trading_symbol=buy_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )
        print(f"Buy Order: {buy_symbol} - {place_buy_order_response}")

        # Sell ATM strike
        place_sell_order_response = self.groww.place_order(
            trading_symbol=sell_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )
        print(f"Sell Order: {sell_symbol} - {place_sell_order_response}")
        
        return {
            'buy_order': place_buy_order_response,
            'sell_order': place_sell_order_response
        }

    def close_put_spread(self, strike_price: float, quantity: int, exchange: str,
                        trading_symbol: str, expiry: str, spread_gap: int):
        """
        Close a put spread position (reverse of place_put_spread)
        
        Args:
            strike_price: ATM or base strike price (used directly, not calculated)
            quantity: Number of lots to trade
            exchange: Exchange name ('NSE' or 'BSE')
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX', 'BANKNIFTY')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            spread_gap: Gap between strikes (e.g., 200)
            
        Returns:
            dict with buy and sell order responses
        """
        exchange_upper = exchange.upper()
        
        # Determine exchange constant
        exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
        
        # Calculate strikes directly from provided strike_price
        buy_strike = int(strike_price)
        sell_strike = int(strike_price - spread_gap)
        
        # Generate option symbols
        buy_symbol = self._format_option_symbol(trading_symbol, expiry, buy_strike, 'PE')
        sell_symbol = self._format_option_symbol(trading_symbol, expiry, sell_strike, 'PE')
        
        # Buy back ATM strike (close short position)
        place_buy_order_response = self.groww.place_order(
            trading_symbol=buy_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_BUY,
        )
        print(f"Buy Order: {buy_symbol} - {place_buy_order_response}")

        # Sell lower strike (close long position)
        place_sell_order_response = self.groww.place_order(
            trading_symbol=sell_symbol,
            quantity=quantity,
            validity=self.groww.VALIDITY_DAY,
            exchange=exchange_const,
            segment=self.groww.SEGMENT_FNO,
            product=self.groww.PRODUCT_MIS,
            order_type=self.groww.ORDER_TYPE_MARKET,
            transaction_type=self.groww.TRANSACTION_TYPE_SELL,
        )
        print(f"Sell Order: {sell_symbol} - {place_sell_order_response}")
        
        return {
            'buy_order': place_buy_order_response,
            'sell_order': place_sell_order_response
        }

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
            positions_response = self.groww.get_positions_for_user()
            
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
    
    def _format_option_symbol(self, trading_symbol: str, expiry: str, strike: int, option_type: str) -> str:
        """
        Format option trading symbol from components
        
        Args:
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            strike: Strike price as integer
            option_type: 'CE' for call or 'PE' for put
            
        Returns:
            str: Option trading symbol (e.g., 'NIFTY2630225600CE')
            
        Note: The trading symbol format is SYMBOL + YYMDD + STRIKE + CE/PE
              For example: NIFTY2630225600CE = NIFTY + 26 (year) + 3 (March) + 02 (2nd) + 25600 + CE
        """
        from datetime import datetime
        
        # Parse expiry format
        # If expiry is in format '02Mar', convert to YYMDD format
        if len(expiry) <= 5 and '-' not in expiry:
            # Format: '02Mar' -> need to convert to YYMDD format
            day = expiry[:2]
            month_str = expiry[2:].upper()
            
            # Map month names to numbers (without leading zero)
            month_map = {
                'JAN': '1', 'FEB': '2', 'MAR': '3', 'APR': '4',
                'MAY': '5', 'JUN': '6', 'JUL': '7', 'AUG': '8',
                'SEP': '9', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            
            month = month_map.get(month_str, '1')
            year = '26'  # Assuming 2026
            
            # Format: YYMDD (e.g., 26302 for 2nd March 2026)
            expiry_code = f"{year}{month}{day}"
        elif '-' in expiry:
            # Format: '2026-03-02' -> extract YYMDD
            date_obj = datetime.strptime(expiry, '%Y-%m-%d')
            year = date_obj.strftime('%y')
            month = str(int(date_obj.strftime('%m')))  # Remove leading zero
            day = date_obj.strftime('%d')
            expiry_code = f"{year}{month}{day}"
        else:
            # Assume it's already in correct format
            expiry_code = expiry
        
        return f"{trading_symbol.upper()}{expiry_code}{strike}{option_type.upper()}"
    
    def get_option_strike_symbol(self, spot_price: float, exchange: str, trading_symbol: str,
                                  expiry: str, option_type: str, otm_points: int = 0) -> str:
        """
        Get the option trading symbol based on spot price and parameters
        
        Args:
            spot_price: Current spot price
            exchange: Exchange name ('NSE' or 'BSE')
            trading_symbol: Underlying symbol (e.g., 'NIFTY', 'SENSEX')
            expiry: Expiry date in format like '02Mar' or '2026-03-02'
            option_type: 'CE' for call or 'PE' for put
            otm_points: Points away from ATM (positive for OTM, negative for ITM)
            
        Returns:
            str: Option trading symbol (e.g., 'NIFTY2630225600CE')
            
        Note: The trading symbol format is SYMBOL + YYMDD + STRIKE + CE/PE
              For example: NIFTY2630225600CE = NIFTY + 26 (year) + 3 (March) + 02 (2nd) + 25600 + CE
        """
        from datetime import datetime
        
        atm_strike = self.get_atm_strike(spot_price, exchange)
        strike = int(atm_strike + otm_points)
        
        # Parse expiry format
        # If expiry is in format '02Mar', convert to YYMDD format
        if len(expiry) <= 5 and '-' not in expiry:
            # Format: '02Mar' -> need to convert to YYMDD format
            day = expiry[:2]
            month_str = expiry[2:].upper()
            
            # Map month names to numbers (without leading zero)
            month_map = {
                'JAN': '1', 'FEB': '2', 'MAR': '3', 'APR': '4',
                'MAY': '5', 'JUN': '6', 'JUL': '7', 'AUG': '8',
                'SEP': '9', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            
            month = month_map.get(month_str, '1')
            # Get current year dynamically
            year = datetime.now().strftime('%y')
            
            # Format: YYMDD (e.g., 26302 for 2nd March 2026)
            expiry_code = f"{year}{month}{day}"
        elif '-' in expiry:
            # Format: '2026-03-02' -> extract YYMDD
            date_obj = datetime.strptime(expiry, '%Y-%m-%d')
            year = date_obj.strftime('%y')
            month = str(int(date_obj.strftime('%m')))  # Remove leading zero
            day = date_obj.strftime('%d')
            expiry_code = f"{year}{month}{day}"
        else:
            # Assume it's already in correct format
            expiry_code = expiry
        
        return self._format_option_symbol(trading_symbol, expiry, strike, option_type)
    
    def get_first_option_15min_candle(self, option_symbol: str, exchange: str) -> dict:
        """
        Get the first 15-minute option candle (9:15 AM to 9:30 AM IST)
        
        Args:
            option_symbol: Option trading symbol (e.g., 'NIFTY28FEB24000CE')
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error/not available
        """
        try:
            from datetime import datetime, time
            
            exchange_upper = exchange.upper()
            exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
            
            # Get current date and time
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            
            # Check if current time is after 9:30 AM
            first_candle_end = time(9, 30)
            
            # If before 9:30 AM, the first 15-min candle is not yet complete
            if current_time < first_candle_end:
                print(f"First 15-min option candle not yet complete. Current time: {current_time.strftime('%H:%M:%S')}")
                return None
            
            # Format times for the first 15 minutes of trading (9:15 AM to 9:30 AM IST)
            start_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:15:00"
            end_time = f"{current_datetime.strftime('%Y-%m-%d')} 09:30:00"
            
            # Fetch historical candle data for the specific time range
            # groww_symbol format for options: 'NSE-NIFTY02Mar25550CE'
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{option_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_FNO,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the first candle (9:15-9:30 AM)
                candle = historical_response['candles'][0]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for option {option_symbol} on {current_datetime.strftime('%Y-%m-%d')}")
                return None
                
        except Exception as e:
            print(f"Error fetching first 15-min option candle data: {e}")
            return None
    
    def get_option_15min_candle(self, option_symbol: str, exchange: str) -> dict:
        """
        Get the most recent 15-minute OHLC candle data for an option
        
        Args:
            option_symbol: Option trading symbol (e.g., 'NIFTY28FEB24000CE')
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'open', 'high', 'low', 'close', 'volume' keys or None if error
        """
        try:
            from datetime import datetime, timedelta
            
            exchange_upper = exchange.upper()
            exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
            
            # Calculate time range for the most recent candle
            now = datetime.now()
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            start_time = (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Fetch historical candle data for option
            # groww_symbol format for options: 'NSE-NIFTY02Mar25550CE'
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{option_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_FNO,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if historical_response and 'candles' in historical_response and len(historical_response['candles']) > 0:
                # Get the most recent candle (last one in the list)
                candle = historical_response['candles'][-1]
                # Candle format: [timestamp, open, high, low, close, volume]
                return {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
            else:
                print(f"No candle data found for option {option_symbol}")
                return None
                
        except Exception as e:
            print(f"Error fetching option 15-min candle data: {e}")
            return None
    
    def get_option_ema_33_15min(self, option_symbol: str, exchange: str) -> dict:
        """
        Calculate EMA 33 for high, close, open, and low of 15-minute option candles
        
        Args:
            option_symbol: Option trading symbol (e.g., 'NIFTY28FEB24000CE')
            exchange: Exchange name ('NSE' or 'BSE')
            
        Returns:
            dict with 'ema_open', 'ema_high', 'ema_low', 'ema_close', 'candles_used' keys or None if error
        """
        try:
            from datetime import datetime, timedelta
            
            exchange_upper = exchange.upper()
            exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
            
            # Calculate time range - get enough data for EMA 33 calculation
            now = datetime.now()
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            # Go back approximately 10 days to get sufficient candles
            start_time = (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Fetch historical candle data
            # groww_symbol format for options: 'NSE-NIFTY02Mar25550CE'
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{option_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_FNO,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self.groww.CANDLE_INTERVAL_MIN_15
            )
            
            if not historical_response or 'candles' not in historical_response or len(historical_response['candles']) < 33:
                print(f"Insufficient candle data for EMA 33 calculation. Need at least 33 candles, got {len(historical_response.get('candles', []))}")
                return None
            
            candles = historical_response['candles']
            
            # Extract OHLC data
            # Candle format: [timestamp, open, high, low, close, volume]
            opens = [candle[1] for candle in candles]
            highs = [candle[2] for candle in candles]
            lows = [candle[3] for candle in candles]
            closes = [candle[4] for candle in candles]
            
            # Calculate EMA 33 for each OHLC component
            ema_open = self._calculate_ema(opens, period=33)
            ema_high = self._calculate_ema(highs, period=33)
            ema_low = self._calculate_ema(lows, period=33)
            ema_close = self._calculate_ema(closes, period=33)
            
            return {
                'ema_open': ema_open,
                'ema_high': ema_high,
                'ema_low': ema_low,
                'ema_close': ema_close,
                'candles_used': len(candles)
            }
            
        except Exception as e:
            print(f"Error calculating EMA 33 for option 15-min candles: {e}")
            return None
    
    def get_option_candles_in_range(self, option_symbol: str, exchange: str,
                                     start_time: str, end_time: str, interval_minutes: int = 15) -> list:
        """
        Get option candles within a specific time range
        
        Args:
            option_symbol: Option trading symbol (e.g., 'NIFTY28FEB24000CE')
            exchange: Exchange name ('NSE' or 'BSE')
            start_time: Start time in format 'YYYY-MM-DD HH:MM:SS'
            end_time: End time in format 'YYYY-MM-DD HH:MM:SS'
            interval_minutes: Candle interval in minutes (default: 15)
            
        Returns:
            list of candle dicts with 'timestamp', 'open', 'high', 'low', 'close', 'volume' keys
        """
        try:
            exchange_upper = exchange.upper()
            exchange_const = self.groww.EXCHANGE_NSE if exchange_upper == 'NSE' else self.groww.EXCHANGE_BSE
            
            # Fetch historical candle data
            # groww_symbol format for options: 'NSE-NIFTY02Mar25550CE'
            historical_response = self.groww.get_historical_candles(
                groww_symbol=f"{exchange_upper}-{option_symbol}",
                exchange=exchange_const,
                segment=self.groww.SEGMENT_FNO,
                start_time=start_time,
                end_time=end_time,
                candle_interval=self._get_candle_interval_constant(interval_minutes)
            )
            
            if not historical_response or 'candles' not in historical_response:
                print(f"No candle data found for option {option_symbol}")
                return []
            
            # Convert candles to dict format
            candles = []
            for candle in historical_response['candles']:
                candles.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            return candles
            
        except Exception as e:
            print(f"Error fetching option candles in range: {e}")
            return []
