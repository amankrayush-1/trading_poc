"""
Test script for the option trading bot.
Tests individual components without executing real trades.
"""
from datetime import datetime
from option_trade.data_fetcher import OHLCData
from option_trade.indicators import MultiEMACalculator
from option_trade.trading_strategy import EMATouchStrategy, SignalValidator, TradingSignal


def test_ema_calculation():
    """Test EMA calculation with sample data."""
    print("\n" + "=" * 80)
    print("Testing EMA Calculation")
    print("=" * 80)
    
    # Create sample candles
    candles = []
    base_price = 23500
    
    for i in range(50):
        candle = OHLCData(
            timestamp=i,
            open=base_price + i * 10,
            high=base_price + i * 10 + 20,
            low=base_price + i * 10 - 20,
            close=base_price + i * 10 + 5
        )
        candles.append(candle)
    
    # Calculate EMA
    ema_calculator = MultiEMACalculator(period=33)
    ema_values = ema_calculator.get_latest_emas(candles)
    
    if ema_values:
        print(f"✓ EMA calculation successful")
        print(f"  EMA Open:  {ema_values['ema_open']:.2f}")
        print(f"  EMA High:  {ema_values['ema_high']:.2f}")
        print(f"  EMA Low:   {ema_values['ema_low']:.2f}")
        print(f"  EMA Close: {ema_values['ema_close']:.2f}")
        return True
    else:
        print("✗ EMA calculation failed")
        return False


def test_signal_generation():
    """Test signal generation with sample data."""
    print("\n" + "=" * 80)
    print("Testing Signal Generation")
    print("=" * 80)
    
    strategy = EMATouchStrategy(call_spread_enabled=True, put_spread_enabled=False)
    
    # Test case 1: Candle touches EMA low (should generate CALL_SPREAD signal)
    print("\nTest Case 1: Candle low touches EMA low")
    current_candle = OHLCData(
        timestamp=100,
        open=23500,
        high=23550,
        low=23480,  # Below EMA low
        close=23520
    )
    
    ema_values = {
        'ema_open': 23510,
        'ema_high': 23560,
        'ema_low': 23490,  # Candle low is below this
        'ema_close': 23530
    }
    
    signal = strategy.generate_signal(current_candle, ema_values)
    print(f"Signal: {signal}")
    
    if signal.signal_type == TradingSignal.CALL_SPREAD:
        print("✓ Correct signal generated (CALL_SPREAD)")
    else:
        print("✗ Incorrect signal")
    
    # Test case 2: No touch (should generate NO_SIGNAL)
    print("\nTest Case 2: No EMA touch")
    current_candle = OHLCData(
        timestamp=101,
        open=23500,
        high=23550,
        low=23500,  # Above EMA low
        close=23520
    )
    
    signal = strategy.generate_signal(current_candle, ema_values)
    print(f"Signal: {signal}")
    
    if signal.signal_type == TradingSignal.NO_SIGNAL:
        print("✓ Correct signal generated (NO_SIGNAL)")
    else:
        print("✗ Incorrect signal")


def test_signal_validation():
    """Test signal validation with time constraints."""
    print("\n" + "=" * 80)
    print("Testing Signal Validation")
    print("=" * 80)
    
    validator = SignalValidator(trading_start_time="09:30:00")
    
    # Test case 1: Valid time
    print("\nTest Case 1: Valid trading time (10:00:00)")
    signal = TradingSignal(TradingSignal.CALL_SPREAD, "Test signal")
    is_valid, reason = validator.validate_signal(signal, "10:00:00")
    print(f"Valid: {is_valid}, Reason: {reason}")
    
    if is_valid:
        print("✓ Signal correctly validated")
    else:
        print("✗ Signal incorrectly rejected")
    
    # Test case 2: Invalid time (before 9:30 AM)
    print("\nTest Case 2: Invalid trading time (09:00:00)")
    is_valid, reason = validator.validate_signal(signal, "09:00:00")
    print(f"Valid: {is_valid}, Reason: {reason}")
    
    if not is_valid:
        print("✓ Signal correctly rejected")
    else:
        print("✗ Signal incorrectly validated")
    
    # Test case 3: No signal
    print("\nTest Case 3: No signal")
    no_signal = TradingSignal(TradingSignal.NO_SIGNAL, "No signal")
    is_valid, reason = validator.validate_signal(no_signal, "10:00:00")
    print(f"Valid: {is_valid}, Reason: {reason}")
    
    if not is_valid:
        print("✓ No signal correctly rejected")
    else:
        print("✗ No signal incorrectly validated")


def test_atm_strike_calculation():
    """Test ATM strike price calculation."""
    print("\n" + "=" * 80)
    print("Testing ATM Strike Calculation")
    print("=" * 80)
    
    from option_trade.order_executor import OrderExecutor
    
    # Mock executor (without real API)
    class MockGroww:
        pass
    
    executor = OrderExecutor(MockGroww(), expiry="25N04", spread_gap=200)
    
    test_cases = [
        (23567.50, 23550),
        (23525.00, 23550),
        (23574.99, 23550),
        (23575.00, 23600),
        (23500.00, 23500),
    ]
    
    all_passed = True
    for spot_price, expected_strike in test_cases:
        calculated_strike = executor.get_atm_strike(spot_price)
        status = "✓" if calculated_strike == expected_strike else "✗"
        print(f"{status} Spot: {spot_price:.2f} -> ATM: {calculated_strike} (Expected: {expected_strike})")
        if calculated_strike != expected_strike:
            all_passed = False
    
    if all_passed:
        print("\n✓ All ATM strike calculations passed")
    else:
        print("\n✗ Some ATM strike calculations failed")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Option Trading Bot - Component Tests")
    print("=" * 80)
    
    try:
        test_ema_calculation()
        test_signal_generation()
        test_signal_validation()
        test_atm_strike_calculation()
        
        print("\n" + "=" * 80)
        print("All Tests Completed")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()