# Trading Bot Driver

This is the main driver/orchestrator for the trading bot system. It reads configuration, determines which strategy to execute, and runs it across **multiple accounts in parallel**.

## Structure

```
bot/
├── main.py              # Main driver class and entry point
├── config.json          # Configuration file (includes accounts)
├── config_reader.py     # Configuration reader utility
├── utils.py             # Common utilities (API helpers)
├── sell_1/              # Strategy: Sell 1
│   ├── __init__.py
│   └── strategy.py      # Sell1Strategy implementation
├── sell_2/              # Strategy: Sell 2 (to be implemented)
│   ├── __init__.py
│   └── strategy.py
└── README.md            # This file
```

## Configuration

The [`config.json`](config.json:1) file contains:

- **strategy**: The active strategy to execute (e.g., "sell_1", "sell_2")
- **accounts**: Array of account configurations with credentials
- **Strategy-specific configs**: Each strategy has its own configuration block
- **Common parameters**: expiry, spread_gap, exchange, number_of_lots, lot_size, itm_points, atr

Example:
```json
{
  "sell_1": {
    "r1": "23000"
  },
  "strategy": "sell_1",
  "expiry": "28NOV",
  "spread_gap": "200",
  "exchange": "nifty",
  "number_of_lots": "2",
  "lot_size": "65",
  "itm_points": "50",
  "atr": 40,
  "accounts": [
    {
      "name": "Account 1",
      "token": "your_groww_token_here",
      "enabled": true
    },
    {
      "name": "Account 2",
      "token": "your_groww_token_here",
      "enabled": true
    }
  ]
}
```

## Usage

### Running the Bot (Parallel Execution)

Execute strategy across all enabled accounts **in parallel**:

```bash
# From the project root directory
python -m bot.main
```

This will:
- Read all enabled accounts from [`config.json`](config.json:17)
- Execute the strategy on all accounts simultaneously using ThreadPoolExecutor
- Display results for each account as they complete

### Disabling Specific Accounts

Set `"enabled": false` for any account you want to skip:

```json
{
  "name": "Account 2",
  "token": "...",
  "enabled": false
}
```

## Parallel Execution

The bot uses Python's `concurrent.futures.ThreadPoolExecutor` to run strategies across multiple accounts in parallel:

- **Advantages**:
  - Faster execution when managing multiple accounts
  - All accounts execute simultaneously
  - Independent execution (one account's failure doesn't block others)

- **Thread Safety**:
  - Each account gets its own GrowwAPI instance
  - Each account gets its own Utils instance
  - No shared state between account executions

## Output Example

```
==================================================
Trading Bot - Starting (Parallel Mode)
==================================================
Active Strategy: sell_1
Strategy Config: {'r1': '23000'}

Found 2 enabled account(s)
==================================================

[Account 1] Starting strategy execution...
✓ Groww API initialized for Account 1's account
[Account 1] ✓ Strategy 'sell_1' loaded

[Account 2] Starting strategy execution...
✓ Groww API initialized for Account 2's account
[Account 2] ✓ Strategy 'sell_1' loaded

[Account 1] --- Executing Sell 1 Strategy ---
[Account 1] Current NIFTY Spot Price: 23150.5
[Account 1] ✓ Strategy execution completed

[Account 2] --- Executing Sell 1 Strategy ---
[Account 2] Current NIFTY Spot Price: 23150.5
[Account 2] ✓ Strategy execution completed

==================================================
EXECUTION SUMMARY
==================================================
✓ Account 1: SUCCESS - call_spread_placed
✓ Account 2: SUCCESS - call_spread_placed

✓ Bot execution completed successfully for all accounts
```

## Creating a New Strategy

To create a new strategy (e.g., "sell_3"):

1. **Create strategy directory**:
   ```bash
   mkdir bot/sell_3
   touch bot/sell_3/__init__.py
   ```

2. **Create strategy class** in `bot/sell_3/strategy.py`:
   ```python
   from typing import Dict, Any
   from growwapi import GrowwAPI
   from bot import Utils

   class Sell3Strategy:
       def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any], strategy_config: Dict[str, Any]):
           self.groww = groww
           self.utils = utils
           self.config = config
           self.strategy_config = strategy_config
           # Initialize your strategy parameters here
       
       def execute(self) -> Dict[str, Any]:
           # Implement your strategy logic here
           pass
   ```

3. **Import in [`main.py`](main.py:14)**:
   ```python
   from bot import Sell3Strategy
   ```

4. **Add to factory method** in [`main.py`](main.py:47):
   ```python
   elif strategy_name == "sell_3":
       return Sell3Strategy
   ```

5. **Add strategy config** to [`config.json`](config.json:1):
   ```json
   {
     "sell_3": {
       "param1": "value1",
       "param2": "value2"
     },
     "strategy": "sell_3"
   }
   ```

## Strategy Class Interface

All strategy classes must implement:

### Constructor
```python
def __init__(self, groww: GrowwAPI, utils: Utils, config: Dict[str, Any], strategy_config: Dict[str, Any])
```

### Execute Method
```python
def execute(self) -> Dict[str, Any]:
    """
    Execute the strategy logic
    
    Returns:
        Dictionary with execution results containing:
        - status: "success" or "error"
        - action: Description of action taken
        - Additional strategy-specific data
    """
```

### Optional: Close Positions Method
```python
def close_positions(self):
    """
    Close all open positions for this strategy
    """
```

## Available Utilities

The [`Utils`](utils.py:3) class provides common helper methods:

- `get_nifty_spot_price()`: Get current NIFTY spot price
- `get_nifty_15min_candle()`: Get 15-minute OHLC candle data
- `get_nifty_first_15min_candle()`: Get first 15-min candle (9:15-9:30 AM)
- `get_atm_strike(spot_price)`: Calculate ATM strike price
- `place_call_spread(strike_price, quantity)`: Place a call spread order
- `close_call_spread(strike_price, quantity)`: Close a call spread
- `place_put_spread(strike_price, quantity)`: Place a put spread order
- `close_put_spread(strike_price, quantity)`: Close a put spread
- `close_all_fno_trades()`: Close all open FNO positions

## Error Handling

The driver includes comprehensive error handling:
- Configuration file not found
- No accounts configured or enabled
- Strategy not found
- API initialization failures per account
- Strategy execution errors per account
- Individual account failures don't affect other accounts

All errors are logged with clear messages and stack traces.

## Security Notes

⚠️ **Important**: Store account credentials securely. Consider:
- Using environment variables instead of hardcoding in config.json
- Encrypting the config.json file
- Using a secrets management system
- Never committing credentials to version control
