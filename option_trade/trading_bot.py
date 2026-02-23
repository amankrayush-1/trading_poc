"""
Main trading bot orchestrator.
Follows Dependency Inversion Principle - depends on abstractions, not concretions.
"""
import time
from datetime import datetime
from typing import Optional, List
from growwapi import GrowwAPI

from option_trade.config import TradingConfig
from option_trade.data_fetcher import MarketDataFetcher, OHLCData
from option_trade.indicators import MultiEMACalculator
from option_trade.trading_strategy import EMATouchStrategy, SignalValidator, TradingSignal
from option_trade.order_executor import OrderExecutor


class TradingBot:
    """
    Main trading bot that orchestrates all components.
    Follows Dependency Inversion Principle and Single Responsibility Principle.
    """
    
    def __init__(self, config: TradingConfig):
        """
        Initialize trading bot with configuration.
        
        Args:
            config: TradingConfig instance
        """
        self.config = config
        
        # Initialize Groww API
        self.groww = GrowwAPI(config.access_token)
        
        # Initialize components (Dependency Injection)
        self.data_fetcher = MarketDataFetcher(
            self.groww,
            exchange=config.exchange,
            segment=config.segment_cash
        )
        
        self.ema_calculator = MultiEMACalculator(period=config.ema_period)
        
        self.strategy = EMATouchStrategy(
            call_spread_enabled=config.call_spread_enabled,
            put_spread_enabled=config.put_spread_enabled
        )
        
        self.signal_validator = SignalValidator(
            trading_start_time=config.trading_start_time
        )
        
        self.order_executor = OrderExecutor(
            self.groww,
            expiry=config.call_option,  # Using call_option as expiry
            spread_gap=config.spread_gap
        )
        
        # State management
        self.first_candle: Optional[OHLCData] = None
        self.historical_candles: List[OHLCData] = []
        self.trade_executed = False
    
    def initialize(self) -> bool:
        """
        Initialize the trading bot by fetching the first candle (9:15-9:30 AM).
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("=" * 80)
        print("Initializing Trading Bot")
        print("=" * 80)
        
        try:
            # Fetch first candle (9:15 AM to 9:30 AM)
            today = datetime.now()
            print(f"Fetching first candle for {today.strftime('%Y-%m-%d')}...")
            
            self.first_candle = self.data_fetcher.get_first_candle(
                trading_symbol=self.config.trading_symbol,
                date=today,
                start_time=self.config.first_candle_start,
                end_time=self.config.first_candle_end
            )
            
            if not self.first_candle:
                print("✗ Failed to fetch first candle")
                return False
            
            print(f"✓ First candle fetched: {self.first_candle}")
            
            # Initialize historical candles with first candle
            self.historical_candles = [self.first_candle]
            
            print("✓ Trading bot initialized successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error during initialization: {e}")
            return False
    
    def fetch_historical_candles(self) -> bool:
        """
        Fetch historical 15-minute candles to build EMA.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            today = datetime.now()
            
            # Fetch candles from 9:15 AM to current time
            start_time = f"{today.strftime('%Y-%m-%d')} {self.config.first_candle_start}"
            end_time = f"{today.strftime('%Y-%m-%d %H:%M:%S')}"
            
            candles = self.data_fetcher.get_historical_candles(
                trading_symbol=self.config.trading_symbol,
                start_time=start_time,
                end_time=end_time,
                interval_minutes=self.config.candle_interval
            )
            
            if candles:
                self.historical_candles = candles
                print(f"✓ Fetched {len(candles)} historical candles")
                return True
            else:
                print("⚠ No historical candles fetched")
                return False
                
        except Exception as e:
            print(f"✗ Error fetching historical candles: {e}")
            return False
    
    def update_current_candle(self) -> Optional[OHLCData]:
        """
        Fetch current 15-minute candle.
        
        Returns:
            Current OHLCData or None if error
        """
        try:
            current_candle = self.data_fetcher.get_current_15min_candle(
                self.config.trading_symbol
            )
            
            if current_candle:
                # Update historical candles if this is a new candle
                if not self.historical_candles or \
                   current_candle.timestamp != self.historical_candles[-1].timestamp:
                    self.historical_candles.append(current_candle)
                else:
                    # Update the last candle
                    self.historical_candles[-1] = current_candle
            
            return current_candle
            
        except Exception as e:
            print(f"✗ Error updating current candle: {e}")
            return None
    
    def check_trading_signal(self) -> Optional[TradingSignal]:
        """
        Check for trading signals based on current market conditions.
        
        Returns:
            TradingSignal or None if insufficient data
        """
        try:
            # Need at least EMA period + 1 candles
            if len(self.historical_candles) < self.config.ema_period + 1:
                print(f"⚠ Insufficient candles for EMA calculation: {len(self.historical_candles)}/{self.config.ema_period + 1}")
                return None
            
            # Calculate EMAs
            ema_values = self.ema_calculator.get_latest_emas(self.historical_candles)
            
            if not ema_values:
                print("⚠ Failed to calculate EMA values")
                return None
            
            # Get current candle
            current_candle = self.historical_candles[-1]
            
            # Generate signal
            signal = self.strategy.generate_signal(current_candle, ema_values)
            
            return signal
            
        except Exception as e:
            print(f"✗ Error checking trading signal: {e}")
            return None
    
    def check_exit_signal(self) -> Optional[TradingSignal]:
        """
        Check for exit signals to close positions.
        
        Returns:
            TradingSignal or None if insufficient data
        """
        try:
            # Need at least EMA period + 1 candles
            if len(self.historical_candles) < self.config.ema_period + 1:
                return None
            
            # Calculate EMAs
            ema_values = self.ema_calculator.get_latest_emas(self.historical_candles)
            
            if not ema_values:
                return None
            
            # Get current candle
            current_candle = self.historical_candles[-1]
            
            # Check exit signal
            exit_signal = self.strategy.check_exit_signal(current_candle, ema_values)
            
            return exit_signal
            
        except Exception as e:
            print(f"✗ Error checking exit signal: {e}")
            return None
    
    def execute_trade(self, signal: TradingSignal) -> bool:
        """
        Execute trade based on signal.
        
        Args:
            signal: TradingSignal object
            
        Returns:
            True if trade executed successfully, False otherwise
        """
        try:
            # Get current spot price
            spot_price = self.data_fetcher.get_ltp(self.config.trading_symbol)
            
            if not spot_price:
                print("✗ Failed to get spot price")
                return False
            
            # Get ATM strike
            strike_price = self.order_executor.get_atm_strike(spot_price)
            
            print(f"Spot Price: {spot_price:.2f}, ATM Strike: {strike_price}")
            
            # Execute based on signal type
            if signal.signal_type == TradingSignal.CALL_SPREAD:
                print(f"Executing CALL SPREAD at strike {strike_price}...")
                result = self.order_executor.place_call_spread(
                    strike_price=strike_price,
                    quantity=self.config.quantity
                )
            elif signal.signal_type == TradingSignal.PUT_SPREAD:
                print(f"Executing PUT SPREAD at strike {strike_price}...")
                result = self.order_executor.place_put_spread(
                    strike_price=strike_price,
                    quantity=self.config.quantity
                )
            else:
                return False
            
            if result['status'] == 'success':
                print(f"✓ Trade executed successfully: {result}")
                self.trade_executed = True
                return True
            else:
                print(f"✗ Trade execution failed: {result}")
                return False
                
        except Exception as e:
            print(f"✗ Error executing trade: {e}")
            return False
    
    def close_positions(self) -> bool:
        """
        Close all open positions.
        
        Returns:
            True if positions closed successfully, False otherwise
        """
        try:
            print("Closing all open positions...")
            result = self.order_executor.close_all_positions()
            
            if result['status'] == 'success':
                print(f"✓ Positions closed successfully")
                print(f"  Closed: {result['closed_count']}")
                print(f"  Failed: {result['failed_count']}")
                return True
            else:
                print(f"✗ Failed to close positions: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"✗ Error closing positions: {e}")
            return False
    
    def run(self, check_interval: int = 60):
        """
        Main trading loop.
        
        Args:
            check_interval: Interval in seconds between checks (default: 60)
        """
        print("\n" + "=" * 80)
        print("Starting Trading Bot")
        print("=" * 80)
        
        # Initialize
        if not self.initialize():
            print("✗ Initialization failed. Exiting.")
            return
        
        print(f"\nBot will check for signals every {check_interval} seconds")
        print(f"Trading allowed after {self.config.trading_start_time}")
        print(f"Strategy: EMA {self.config.ema_period} Touch")
        print(f"Call Spread: {'Enabled' if self.config.call_spread_enabled else 'Disabled'}")
        print(f"Put Spread: {'Enabled' if self.config.put_spread_enabled else 'Disabled'}")
        print("\n" + "=" * 80)
        
        try:
            while True:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{current_time}] Checking market conditions...")
                
                # Update historical candles
                self.fetch_historical_candles()
                
                # Update current candle
                current_candle = self.update_current_candle()
                
                if not current_candle:
                    print("⚠ Failed to fetch current candle")
                    time.sleep(check_interval)
                    continue
                
                print(f"Current Candle: {current_candle}")
                
                # If trade is executed, check for exit signal
                if self.trade_executed:
                    print("✓ Trade is active, checking for exit signal...")
                    
                    exit_signal = self.check_exit_signal()
                    
                    if exit_signal and exit_signal.signal_type == TradingSignal.EXIT_TRADE:
                        print(f"EXIT SIGNAL: {exit_signal.reason}")
                        if self.close_positions():
                            print("✓ Positions closed successfully")
                            # Reset trade_executed to allow new trades if needed
                            # self.trade_executed = False  # Uncomment if you want to allow re-entry
                        else:
                            print("✗ Failed to close positions")
                    else:
                        print("No exit signal, holding position")
                    
                    time.sleep(check_interval)
                    continue
                
                # Check for trading signal
                signal = self.check_trading_signal()
                
                if not signal:
                    print("⚠ No signal generated")
                    time.sleep(check_interval)
                    continue
                
                print(f"Signal: {signal}")
                
                # Validate signal
                is_valid, reason = self.signal_validator.validate_signal(signal, current_time)
                
                if not is_valid:
                    print(f"⚠ Signal not valid: {reason}")
                    time.sleep(check_interval)
                    continue
                
                # Execute trade
                print(f"✓ Valid signal detected: {signal.reason}")
                if self.execute_trade(signal):
                    print("✓ Trade executed successfully")
                    print("Bot will continue monitoring but won't execute more trades today")
                else:
                    print("✗ Trade execution failed")
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
        finally:
            print("\n" + "=" * 80)
            print("Trading Bot Stopped")
            print("=" * 80)