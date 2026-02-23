# Option Trading Bot - Implementation Summary

## Overview

A professional-grade automated trading bot for options trading using the Groww API. The system follows SOLID principles and implements a clean architecture for maintainability and extensibility.

## Key Features Implemented

### 1. **OHLC Data Fetching** ✅
- Fetches 9:15-9:30 AM first candle as baseline
- Retrieves historical 15-minute candles
- Updates current candle in real-time
- **Module**: [`data_fetcher.py`](data_fetcher.py)

### 2. **EMA 33 Calculation** ✅
- Calculates EMA 33 for open, high, low, and close prices
- Supports multiple price types
- Efficient calculation with proper SMA initialization
- **Module**: [`indicators.py`](indicators.py)

### 3. **Trading Strategy** ✅
- **Entry Logic**: Triggers when 15-min candle touches EMA 33 low (call spread) or high (put spread)
- **Exit Logic**: Closes positions when 15-min candle closes above EMA 33 high
- Extensible strategy pattern for adding new strategies
- **Module**: [`trading_strategy.py`](trading_strategy.py)

### 4. **Order Execution** ✅
- Places call spreads (buy OTM, sell ATM)
- Places put spreads (buy OTM, sell ATM)
- Automatic position closure
- ATM strike calculation
- **Module**: [`order_executor.py`](order_executor.py)

### 5. **Time-based Trading** ✅
- Only trades after 9:30 AM
- Validates trading time before execution
- **Module**: [`trading_strategy.py`](trading_strategy.py:99-143)

### 6. **Configuration Management** ✅
- Centralized configuration
- Reads from [`constant.py`](constant.py)
- Easy parameter adjustment
- **Module**: [`config.py`](config.py)

### 7. **Logging System** ✅
- File and console logging
- Trade execution logs
- Signal generation logs
- Debug information
- **Module**: [`logger.py`](logger.py)

### 8. **Error Handling** ✅
- Comprehensive try-catch blocks
- Graceful error recovery
- Detailed error messages
- **All modules**

## Architecture

### SOLID Principles Implementation

#### Single Responsibility Principle (SRP)
Each class has one clear responsibility:
- [`MarketDataFetcher`](data_fetcher.py:25) - Only fetches market data
- [`EMACalculator`](indicators.py:11) - Only calculates EMA
- [`OrderExecutor`](order_executor.py:11) - Only executes orders
- [`TradingLogger`](logger.py:13) - Only handles logging

#### Open/Closed Principle (OCP)
- [`TradingStrategy`](trading_strategy.py:25) is an abstract base class
- New strategies can be added without modifying existing code
- [`EMATouchStrategy`](trading_strategy.py:46) extends the base

#### Liskov Substitution Principle (LSP)
- Any [`TradingStrategy`](trading_strategy.py:25) implementation can replace another
- Strategies are fully interchangeable

#### Interface Segregation Principle (ISP)
- Small, focused interfaces
- Classes only depend on methods they use

#### Dependency Inversion Principle (DIP)
- [`TradingBot`](trading_bot.py:17) depends on abstractions
- Dependencies injected via constructor
- Easy to test and modify

## Module Structure

```
option_trade/
├── __init__.py                 # Package initialization
├── constant.py                 # User configuration
├── config.py                   # Configuration loader
├── data_fetcher.py            # Market data fetching
├── indicators.py              # Technical indicators (EMA)
├── trading_strategy.py        # Trading strategies
├── order_executor.py          # Order execution
├── trading_bot.py             # Main orchestrator
├── logger.py                  # Logging system
├── main.py                    # Entry point
├── test_bot.py                # Unit tests
├── README.md                  # User documentation
└── IMPLEMENTATION_SUMMARY.md  # This file
```

## Trading Flow

### 1. Initialization Phase
```
Start → Authenticate API → Fetch First Candle (9:15-9:30 AM) → Initialize Components
```

### 2. Trading Loop
```
Loop:
  ├─ Fetch Historical Candles
  ├─ Update Current Candle
  ├─ Calculate EMA 33 (O, H, L, C)
  │
  ├─ If No Position:
  │   ├─ Check Entry Signal
  │   ├─ Validate Time (>= 9:30 AM)
  │   └─ Execute Trade if Valid
  │
  └─ If Position Open:
      ├─ Check Exit Signal (Close > EMA High)
      └─ Close Position if Exit Signal
```

### 3. Entry Signals
- **Call Spread**: Candle Low ≤ EMA 33 Low
- **Put Spread**: Candle High ≥ EMA 33 High

### 4. Exit Signal
- **Exit**: Candle Close > EMA 33 High

## Configuration

Edit [`constant.py`](constant.py):
```python
call_option = '25N04'      # Option expiry
put_option = '25N04'       # Option expiry
spread_gap = 200           # Gap between strikes
call_spread = True         # Enable call spread
put_spread = False         # Enable put spread
```

## Usage

### Running the Bot
```bash
python -m option_trade.main
```

### Running Tests
```bash
python -m option_trade.test_bot
```

## Key Components

### 1. Data Fetcher ([`data_fetcher.py`](data_fetcher.py))
- **OHLCData**: Data class for candle information
- **MarketDataFetcher**: Fetches market data from Groww API
  - [`get_ltp()`](data_fetcher.py:42): Get last traded price
  - [`get_first_candle()`](data_fetcher.py:56): Get 9:15-9:30 AM candle
  - [`get_historical_candles()`](data_fetcher.py:99): Get historical data
  - [`get_current_15min_candle()`](data_fetcher.py:143): Get current candle

### 2. Indicators ([`indicators.py`](indicators.py))
- **EMACalculator**: Calculates EMA for single price type
  - [`calculate_ema()`](indicators.py:23): Calculate EMA from values
  - [`calculate_ema_from_candles()`](indicators.py:44): Calculate from OHLC
- **MultiEMACalculator**: Calculates EMA for all price types
  - [`calculate_all_emas()`](indicators.py:82): Calculate all EMAs
  - [`get_latest_emas()`](indicators.py:103): Get latest EMA values

### 3. Trading Strategy ([`trading_strategy.py`](trading_strategy.py))
- **TradingSignal**: Signal types (CALL_SPREAD, PUT_SPREAD, EXIT_TRADE, NO_SIGNAL)
- **TradingStrategy**: Abstract base class
- **EMATouchStrategy**: EMA touch implementation
  - [`generate_signal()`](trading_strategy.py:62): Generate entry signals
  - [`check_exit_signal()`](trading_strategy.py:99): Check exit conditions
- **SignalValidator**: Validates signals based on time

### 4. Order Executor ([`order_executor.py`](order_executor.py))
- **OrderExecutor**: Executes orders via Groww API
  - [`get_atm_strike()`](order_executor.py:26): Calculate ATM strike
  - [`place_call_spread()`](order_executor.py:35): Execute call spread
  - [`place_put_spread()`](order_executor.py:84): Execute put spread
  - [`close_all_positions()`](order_executor.py:133): Close all FNO positions

### 5. Trading Bot ([`trading_bot.py`](trading_bot.py))
- **TradingBot**: Main orchestrator
  - [`initialize()`](trading_bot.py:64): Initialize bot
  - [`fetch_historical_candles()`](trading_bot.py:103): Fetch historical data
  - [`update_current_candle()`](trading_bot.py:136): Update current candle
  - [`check_trading_signal()`](trading_bot.py:163): Check entry signals
  - [`check_exit_signal()`](trading_bot.py:195): Check exit signals
  - [`execute_trade()`](trading_bot.py:217): Execute trades
  - [`close_positions()`](trading_bot.py:267): Close positions
  - [`run()`](trading_bot.py:280): Main trading loop

## Safety Features

1. **Time Validation**: Only trades after 9:30 AM
2. **Automatic Exit**: Closes positions when candle closes above EMA 33 high
3. **Error Handling**: Comprehensive error handling throughout
4. **Logging**: All actions logged for audit trail
5. **Position Management**: Tracks and manages all open positions
6. **Single Trade Control**: Prevents multiple entries (configurable)

## Testing

The [`test_bot.py`](test_bot.py) includes tests for:
- EMA calculation accuracy
- Signal generation logic
- Signal validation (time-based)
- ATM strike calculation

## Future Enhancements

Potential improvements:
1. Add more exit strategies (stop-loss, target profit)
2. Implement trailing stop-loss
3. Add support for multiple symbols
4. Implement backtesting framework
5. Add risk management (position sizing)
6. Support for different option strategies (iron condor, butterfly, etc.)
7. Real-time notifications (email, SMS, Telegram)
8. Performance analytics and reporting

## Dependencies

```
pandas>=2.0.0
openpyxl>=3.1.0
growwapi>=1.5.0
```

## Disclaimer

This is an automated trading system. Use at your own risk. Always:
- Test thoroughly in paper trading mode
- Understand the strategy before deploying
- Monitor the bot regularly
- Have proper risk management in place
- Never risk more than you can afford to lose

## Support

For issues or questions:
- Groww API Documentation: https://groww.in/trade-api/docs/python-sdk
- Review the [`README.md`](README.md) for detailed usage instructions

---

**Implementation Date**: January 15, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅