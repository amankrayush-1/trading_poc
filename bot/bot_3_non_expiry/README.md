# Bot 3 Non-Expiry Strategy

## Overview
This bot implements a complex trading strategy based on the first 15-minute candle analysis, with different execution paths for bald candles and doji candles.

## Strategy Logic

### Main Flow

1. **Wait until 9:30 AM** and capture the OHLC data of the first 15-minute candle (9:15–9:30 AM)

2. **Check if the candle is a bald candle**
   - Condition: `abs(close - open) / open > 0.001`
   - If YES → Execute **Bald Candle Strategy** (Steps 3-5)
   - If NO → Check for doji candle (Step 6)

3. **If neither bald nor doji** → Stop execution for the day

---

### Bald Candle Strategy (Steps 3-5)

**Step 3:** Calculate reference level X
- `X = (15-minute close + high) / 2`

**Step 4:** Monitor subsequent 15-minute candles until 12:00 PM for a strong red candle
- Conditions for strong red candle:
  - Bearish: `open > close`
  - Real body larger than total wick: `(open - close) > (high - open + close - low)`
  - Closes below level X: `close < X`

**Step 5:** When all conditions in Step 4 are met
- Place a **call spread at ITM** (ATM + itm_points)
- Use `expiry_to_trade` from config
- If no strong red candle found by 12:00 PM → Stop execution

---

### Doji Candle Strategy (Steps 6-11)

**Step 6:** Check if the first 15-minute candle is a doji candle
- Conditions:
  - `abs(close - open) / close < 0.001`
  - Body smaller than combined wicks: `abs(close - open) < (high - close + open - low)`

**Step 7:** Get OTM call option strike
- Based on spot price (15-minute candle closing price)
- Strike = ATM + otm_points (from config)
- Use `expiry_to_check` from config

**Step 8:** Calculate EMA 33 for the option chart
- Get EMA 33 OHLC values for the option's 15-minute candles

**Step 9:** Validate option position relative to EMA
- Check: First 15-minute option closing price < EMA 33 low
- If condition NOT met → Stop trade execution

**Step 10:** Monitor option candles until 12:00 PM
- Watch 15-minute candles of the OTM call option
- Look for candle high touching EMA 33 high

**Step 11:** Enter trade when EMA touch occurs
- Place **call spread** with strike price based on current spot price
- Use `expiry_to_trade` from config
- If no EMA touch by 12:00 PM → Stop execution

---

## Configuration

The strategy uses `config.json` with the following parameters:

```json
{
  "expiry_to_trade": "28FEB",      // Expiry date for actual trades
  "expiry_to_check": "28FEB",      // Expiry date for option monitoring
  "spread_gap": "200",              // Gap between call spread strikes
  "trading_symbol": "nifty",        // Underlying symbol
  "exchange": "nse",                // Exchange (NSE or BSE)
  "number_of_lots": "2",            // Number of lots to trade
  "lot_size": "65",                 // Lot size
  "itm_points": "50",               // Points for ITM calculation
  "otm_points": "50",               // Points for OTM calculation
  "accounts": [...]                 // Account configurations
}
```

### Key Parameters

- **expiry_to_trade**: The expiry date used when placing actual trades
- **expiry_to_check**: The expiry date used for monitoring option behavior
- **itm_points**: Points added to ATM for ITM strike (used in bald candle strategy)
- **otm_points**: Points added to ATM for OTM strike (used in doji candle strategy)
- **spread_gap**: Difference between buy and sell strikes in the spread

---

## Execution

Run the bot using:

```bash
cd /Users/amankumarayush/PycharmProjects/trading_poc/bot/bot_3_non_expiry
python main.py
```

The bot will:
1. Load configuration from `config.json`
2. Initialize Groww API for all enabled accounts
3. Execute the strategy in parallel across all accounts
4. Display execution summary for each account

---

## Key Features

- **Parallel Execution**: Runs strategy across multiple accounts simultaneously
- **Time-based Monitoring**: Waits for specific times and monitors candles until 12:00 PM
- **Dual Strategy Paths**: Different logic for bald vs doji candles
- **EMA-based Entry**: Uses EMA 33 for option entry signals in doji strategy
- **Reference Level Trading**: Uses calculated reference level for bald candle strategy

---

## Dependencies

- `growwapi`: Groww API SDK for trading operations
- `bot.utils`: Utility functions for candle data, strikes, and order placement
- Standard Python libraries: `datetime`, `time`, `concurrent.futures`

---

## Notes

- The strategy only trades on days when the first 15-minute candle is either a bald or doji candle
- All monitoring stops at 12:00 PM regardless of conditions
- The bot uses market orders for all trades
- Call spreads are used to limit risk (buy higher strike, sell lower strike)
