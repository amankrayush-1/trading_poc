# Bot 4 - Trading Strategy

## Overview

Bot 4 implements a sophisticated trading strategy based on the first 15-minute candle analysis and previous day's high. The strategy has three distinct cases that determine trade execution based on market conditions.

## Strategy Logic

### Step 1: Initial Setup
- Wait until 9:30 AM IST
- Capture OHLC data of first 15-minute candle (9:15-9:30 AM)
- Get previous trading day's high

### Case 1: Previous Day High < First Candle Open

**Conditions:**
- Previous day high < open of first 15-minute candle
- First 15-minute candle is Doji (can be green or red)
- Lower wick > 2 * upper wick

**Action:**
- Execute sell put spread
- Strike: ATM - 2 * otm_points
- Spread gap: As configured

### Case 2: Previous Day High > First Candle Open

**Conditions:**
- Previous day high > open of first 15-minute candle
- First 15-minute candle is green Doji
- Lower wick > 2 * upper wick
- Spot price touches (open + atr) before 2 PM IST

**Action:**
- Monitor spot price until 2 PM IST
- If spot price touches (open + atr):
  - Execute sell call spread
  - Strike: ATM + 2 * otm_points
  - Spread gap: As configured

### Case 3: Red Candle with Large Body

**Conditions:**
- First 15-minute candle: close < open
- Open - close > atr
- Spot price touches one of two levels first

**Levels to Monitor:**
1. Level 1 (upward): open + atr
2. Level 2 (downward): close - 2*atr + 12.5

**Actions:**
- If Level 1 touched first:
  - Execute sell call spread
  - Strike: ATM + 2 * otm_points
  
- If Level 2 touched first:
  - Execute sell put spread
  - Strike: ATM - 2 * otm_points

## Configuration

The strategy uses `config.json` with the following parameters:

```json
{
  "expiry_to_trade": "5MAR",
  "spread_gap": "200",
  "trading_symbol": "sensex",
  "exchange": "bse",
  "number_of_lots": "1",
  "lot_size": "65",
  "otm_points": "50",
  "atr": "46",
  "accounts": [...]
}
```

### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `expiry_to_trade` | Option expiry date | "5MAR" |
| `spread_gap` | Gap between buy and sell strikes | "200" |
| `trading_symbol` | Underlying symbol | "sensex" or "nifty" |
| `exchange` | Exchange name | "bse" or "nse" |
| `number_of_lots` | Number of lots to trade | "1" |
| `lot_size` | Lot size for the instrument | "65" |
| `otm_points` | Points away from ATM | "50" |
| `atr` | Average True Range value | "46" |

### Account Configuration

Multiple accounts can be configured with individual settings:

```json
"accounts": [
  {
    "name": "Account 1",
    "token": "your_api_token",
    "secret": "your_api_secret",
    "enabled": true,
    "number_of_lots": "1"
  }
]
```

## File Structure

```
bot/bot_4/
├── __init__.py
├── config.json          # Configuration file
├── config_reader.py     # Configuration reader
├── strategy.py          # Strategy implementation
├── main.py             # Main execution script
└── README.md           # This file
```

## Usage

### Running the Strategy

```bash
# From project root
python -m bot.bot_4.main

# Or directly
cd bot/bot_4
python main.py
```

### Prerequisites

1. Valid Groww API credentials
2. Configured `config.json` with correct parameters
3. At least one enabled account in configuration

## Strategy Components

### Doji Candle Detection

A candle is considered Doji if:
- Body size is less than 10% of total candle range
- Has wicks on both sides
- Can be green or red

### Wick Analysis

- **Upper Wick**: high - max(open, close)
- **Lower Wick**: min(open, close) - low
- **Condition**: lower_wick > 2 * upper_wick

### Strike Calculation

**For Call Spread:**
- Sell Strike: ATM + 2 * otm_points
- Buy Strike: Sell Strike + spread_gap

**For Put Spread:**
- Sell Strike: ATM - 2 * otm_points
- Buy Strike: Sell Strike - spread_gap

## Monitoring and Execution

### Simultaneous Multi-Account Execution

The bot supports **simultaneous execution across multiple accounts** using threading:
- All enabled accounts execute the strategy at the same time
- Each account runs in its own thread
- Ensures trades are placed simultaneously across all accounts
- Ideal for managing multiple trading accounts

### Case 1
- Immediate execution if conditions met at 9:30 AM
- All accounts execute simultaneously

### Case 2
- Continuous monitoring until 2:00 PM IST
- Checks spot price every 2 seconds
- Executes when level touched
- All accounts monitor and execute simultaneously

### Case 3
- Continuous monitoring until 3:30 PM IST
- Watches for two levels simultaneously
- Executes based on which level is touched first
- All accounts execute at the same time when level is touched

## Risk Management

1. **Time-based Exits**: Each case has specific time limits
2. **Level-based Triggers**: Trades only execute when specific levels are touched
3. **Spread Trading**: Limited risk through spread strategies
4. **Multiple Conditions**: Requires multiple conditions to be met before trade execution

## Output

The strategy provides detailed output including:
- Configuration details
- Candle analysis
- Case identification
- Level calculations
- Trade execution details
- Order responses
- Execution summary

## Error Handling

The strategy includes comprehensive error handling for:
- Configuration errors
- API connection issues
- Data fetching failures
- Order placement errors
- Account-specific failures

## Notes

1. **Market Hours**: Strategy operates during Indian market hours (9:15 AM - 3:30 PM IST)
2. **Previous Day High**: Automatically adjusts for weekends
3. **Real-time Monitoring**: Uses 2-second intervals for spot price checks
4. **Multi-account Support**: Executes strategy across multiple accounts **simultaneously** using threading
5. **Thread Safety**: Each account runs in its own thread for parallel execution
6. **Simultaneous Orders**: All enabled accounts place orders at the same time when conditions are met

## Support

For issues or questions:
1. Check configuration file syntax
2. Verify API credentials
3. Ensure market hours
4. Review error messages in output

## Version History

- **v1.0.0** - Initial implementation with three cases
  - Case 1: Previous day high below open
  - Case 2: Previous day high above open
  - Case 3: Red candle with large body
