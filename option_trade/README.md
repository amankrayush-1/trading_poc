# Option Trading Bot

A clean, SOLID-principle-based automated trading bot for options trading using the Groww API.

## Features

- **Automated Trading**: Executes call/put spreads based on EMA 33 touch strategy
- **Clean Architecture**: Follows SOLID principles for maintainability and extensibility
- **Real-time Monitoring**: Continuously monitors 15-minute candles
- **Time-based Trading**: Only trades after 9:30 AM
- **First Candle Analysis**: Reads 9:15-9:30 AM candle for initial setup
- **Comprehensive Logging**: Detailed logs for debugging and analysis

## Architecture

The system follows SOLID principles with clear separation of concerns:

### Modules

1. **[`config.py`](config.py)** - Configuration management
   - Centralizes all configuration parameters
   - Loads settings from [`constant.py`](constant.py)

2. **[`data_fetcher.py`](data_fetcher.py)** - Market data retrieval
   - Fetches OHLC data from Groww API
   - Handles first candle (9:15-9:30 AM)
   - Retrieves historical and current candles

3. **[`indicators.py`](indicators.py)** - Technical indicators
   - EMA 33 calculation for open, high, low, close
   - Supports multiple price types

4. **[`trading_strategy.py`](trading_strategy.py)** - Trading logic
   - EMA touch strategy implementation
   - Signal generation and validation
   - Extensible strategy pattern

5. **[`order_executor.py`](order_executor.py)** - Order execution
   - Places call/put spreads
   - Manages positions
   - Closes all positions

6. **[`trading_bot.py`](trading_bot.py)** - Main orchestrator
   - Coordinates all components
   - Manages trading loop
   - State management

7. **[`logger.py`](logger.py)** - Logging system
   - File and console logging
   - Trade and signal logging
   - Debug information

8. **[`main.py`](main.py)** - Entry point
   - Initializes and runs the bot

## Trading Strategy

### EMA 33 Touch Strategy

1. **Initialization (9:15-9:30 AM)**:
   - Fetch the first 15-minute candle (9:15-9:30 AM)
   - Store as baseline

2. **Continuous Monitoring (After 9:30 AM)**:
   - Fetch 15-minute candles continuously
   - Calculate EMA 33 for open, high, low, close

3. **Entry Signal Generation**:
   - **Call Spread**: When candle low touches/crosses EMA 33 low
   - **Put Spread**: When candle high touches/crosses EMA 33 high

4. **Execution**:
   - Get current spot price
   - Calculate ATM strike
   - Execute spread based on signal type

5. **Exit Signal Generation**:
   - **Exit Trade**: When 15-minute candle closes above EMA 33 high
   - Automatically closes all open FNO positions
   - Protects profits and limits losses

### Call Spread
- Buy: ATM + spread_gap (OTM)
- Sell: ATM

### Put Spread
- Buy: ATM - spread_gap (OTM)
- Sell: ATM

## Configuration

Edit [`constant.py`](constant.py) to configure:

```python
call_option = '25N04'      # Option expiry
put_option = '25N04'       # Option expiry
spread_gap = 200           # Gap between strikes
call_spread = True         # Enable call spread
put_spread = False         # Enable put spread
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure [`requirements.txt`](../requirements.txt) contains:
```
pandas>=2.0.0
openpyxl>=3.1.0
growwapi>=1.5.0
```

## Usage

### Running the Bot

```bash
python -m option_trade.main
```

You will be prompted to enter your Groww API access token.

### Getting Access Token

1. Log in to Groww
2. Navigate to API settings
3. Generate access token
4. Copy and paste when prompted

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each class has one reason to change
- [`MarketDataFetcher`](data_fetcher.py:25) - only fetches data
- [`EMACalculator`](indicators.py:11) - only calculates EMA
- [`OrderExecutor`](order_executor.py:11) - only executes orders
- [`TradingLogger`](logger.py:13) - only handles logging

### Open/Closed Principle (OCP)
- [`TradingStrategy`](trading_strategy.py:23) is abstract base class
- New strategies can be added without modifying existing code
- [`EMATouchStrategy`](trading_strategy.py:40) extends base strategy

### Liskov Substitution Principle (LSP)
- Any [`TradingStrategy`](trading_strategy.py:23) implementation can replace another
- Strategies are interchangeable

### Interface Segregation Principle (ISP)
- Small, focused interfaces
- Classes only depend on methods they use

### Dependency Inversion Principle (DIP)
- [`TradingBot`](trading_bot.py:18) depends on abstractions (strategy interface)
- Dependencies injected via constructor
- Easy to test and modify

## File Structure

```
option_trade/
├── __init__.py
├── constant.py           # Configuration constants
├── config.py            # Configuration loader
├── data_fetcher.py      # Market data fetching
├── indicators.py        # Technical indicators
├── trading_strategy.py  # Trading strategies
├── order_executor.py    # Order execution
├── trading_bot.py       # Main bot orchestrator
├── logger.py           # Logging system
├── main.py             # Entry point
└── README.md           # This file
```

## Logging

Logs are stored in `logs/` directory:
- File: `trading_YYYYMMDD.log` (detailed)
- Console: Real-time updates (simplified)

## Safety Features

1. **Time Validation**: Only trades after 9:30 AM
2. **Single Trade**: Executes only one trade per day (configurable)
3. **Automatic Exit**: Closes positions when candle closes above EMA 33 high
4. **Error Handling**: Comprehensive error handling throughout
5. **Logging**: All actions logged for audit trail
6. **Position Management**: Tracks and manages all open positions

## Example Output

```
================================================================================
Option Trading Bot - Starting
================================================================================
Loading configuration...
Trading Symbol: NIFTY
EMA Period: 33
Spread Gap: 200
Call Spread: Enabled
Put Spread: Disabled
Trading Start Time: 09:30:00
Quantity: 50
Initializing trading bot...
Starting trading bot...
================================================================================
Initializing Trading Bot
================================================================================
Fetching first candle for 2026-01-15...
✓ First candle fetched: OHLC(O=23500.0, H=23550.0, L=23480.0, C=23520.0)
✓ Trading bot initialized successfully

[09:45:00] Checking market conditions...
✓ Fetched 3 historical candles
Current Candle: OHLC(O=23520.0, H=23560.0, L=23510.0, C=23540.0)
Signal: TradingSignal(CALL_SPREAD, Candle low (23510.00) touched/crossed EMA low (23515.00))
✓ Valid signal detected: Candle low (23510.00) touched/crossed EMA low (23515.00)
Spot Price: 23540.00, ATM Strike: 23550
Executing CALL SPREAD at strike 23550...
✓ Trade executed successfully

[10:00:00] Checking market conditions...
✓ Trade is active, checking for exit signal...
EXIT SIGNAL: Candle close (23650.00) above EMA high (23620.00)
Closing all open positions...
✓ Positions closed successfully
  Closed: 2
  Failed: 0
```

## Troubleshooting

### Common Issues

1. **Access Token Expired**
   - Generate new token from Groww
   - Update when prompted

2. **Insufficient Candles**
   - Wait for at least 33 candles (8+ hours of trading)
   - Bot will notify when ready

3. **API Rate Limits**
   - Bot includes delays between requests
   - Adjust `check_interval` if needed

## Extending the System

### Adding New Strategy

```python
from option_trade.trading_strategy import TradingStrategy, TradingSignal

class MyCustomStrategy(TradingStrategy):
    def generate_signal(self, current_candle, ema_values):
        # Your logic here
        return TradingSignal(...)
```

### Adding New Indicators

```python
from option_trade.indicators import EMACalculator

class RSICalculator:
    def calculate_rsi(self, candles):
        # Your RSI logic
        pass
```

## Disclaimer

This is an automated trading system. Use at your own risk. Always:
- Test thoroughly in paper trading mode
- Understand the strategy before deploying
- Monitor the bot regularly
- Have proper risk management in place

## License

This project is for educational purposes.

## Support

For issues or questions, please refer to:
- Groww API Documentation: https://groww.in/trade-api/docs/python-sdk
- Project repository issues