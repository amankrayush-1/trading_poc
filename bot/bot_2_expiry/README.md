# Bot 2 - G1/G2/R1 Level Strategy

Standalone trading bot with support and resistance level-based strategy.

## Overview

Bot 2 is a standalone trading bot that uses three key levels (G1, G2, R1) to make trading decisions based on the first 15-minute candle of the trading day.

## Configuration

Edit [`config.json`](config.json) to set your parameters:

```json
{
  "g1": "23000",      // Support level 1 (G1 < G2)
  "g2": "23200",      // Support level 2
  "r1": "23500",      // Resistance level
  "expiry": "28FEB",
  "spread_gap": "200",
  "trading_symbol": "nifty",
  "exchange": "nse",
  "number_of_lots": "2",
  "lot_size": "65",
  "itm_points": "50",
  "atr": 40,
  "accounts": [...]
}
```

**Important:** G1 must be less than G2

## Strategy Logic

### Step 1: Wait till 9:30 AM
Bot waits until market opens and first 15-minute candle completes.

### Step 2: Get First 15-Minute Candle (9:15-9:30 AM)
Fetches OHLC data for the first 15 minutes of trading.

### Step 3: Green Candle Scenario
**Conditions:**
- Candle is green: `close > open`
- `open < G1`
- `open < G2`
- `close < R1`

**Action:**
- Calculate target: `(15min_close + R1) / 2`
- Monitor spot price till 2 PM
- Place call spread when spot >= target

### Step 4: Red Candle Scenario
**Conditions:**
- Candle is red: `open > close`
- `close < G1`
- `close < G2`

**Action:**
- Target level: `G1`
- Monitor spot price till 2 PM
- Place call spread when spot >= G1

## Usage

### Run Bot 2:
```bash
python bot/bot_2_expiry/main.py
```

### Run from project root:
```bash
cd /Users/amankumarayush/PycharmProjects/trading_poc
python bot/bot_2_expiry/main.py
```

## Features

- ✓ Standalone execution (independent from main bot)
- ✓ Separate configuration file
- ✓ Multi-account parallel execution
- ✓ Support and resistance level-based entries
- ✓ 2 PM timeout for level monitoring
- ✓ Supports both NSE and BSE exchanges
- ✓ Comprehensive logging and error handling

## Example Scenarios

### Scenario 1: Green Candle Below Levels
```
15-min Candle: O=22900, H=23100, L=22850, C=23050
G1=23000, G2=23200, R1=23500

Conditions:
- Green: 23050 > 22900 ✓
- open < G1: 22900 < 23000 ✓
- open < G2: 22900 < 23200 ✓
- close < R1: 23050 < 23500 ✓

Target: (23050 + 23500) / 2 = 23275
Action: Place call spread when spot reaches 23275
```

### Scenario 2: Red Candle Below Levels
```
15-min Candle: O=23100, H=23150, L=22950, C=22980
G1=23000, G2=23200, R1=23500

Conditions:
- Red: 23100 > 22980 ✓
- close < G1: 22980 < 23000 ✓
- close < G2: 22980 < 23200 ✓

Target: G1 = 23000
Action: Place call spread when spot reaches 23000
```

## Files

- [`main.py`](main.py) - Entry point and driver
- [`strategy.py`](strategy.py) - Strategy implementation
- [`config.json`](config.json) - Configuration file
- [`__init__.py`](__init__.py) - Package initialization
