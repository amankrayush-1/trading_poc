# SOR (Sell on Rise) Trading Bot

## Overview
The SOR (Sell on Rise) bot implements a trading strategy based on analyzing the first 30-minute candle and monitoring specific price levels throughout the trading day.

## Strategy Logic

### Entry Conditions
1. **Wait until 9:45 AM**
2. **Check Entry Criteria**:
   - Current day Open > Previous day Close
   - First 30-minute candle (9:15-9:45 AM) should be RED

### Trading Cases

**Case 1: Call Spread (ITM)**
- **Trigger**: Spot price >= (Open - ATR - 12.5)
- **Action**: Execute ITM call spread
- **Strike**: ATM + ITM Points
- **Quantity**: Full lots

**Case 2: Put Spread (ITM)**
- **Trigger**: Spot price <= (First 15min Close - 2*ATR + 12.5)
- **Action**: Execute ITM put spread
- **Strike**: ATM - ITM Points
- **Quantity**: Full lots

### Time Management
- **Monitoring Period**: 9:45 AM to 12:00 PM
- **Cutoff**: If no level is touched by 12 PM, no trade is executed

## Configuration

### config.json Parameters
```json
{
  "expiry_to_trade": "5MAR",        // Expiry date for options
  "spread_gap": "200",               // Gap between buy and sell strikes
  "trading_symbol": "sensex",        // Trading symbol (sensex/nifty)
  "exchange": "bse",                 // Exchange (bse/nse)
  "number_of_lots": "1",             // Number of lots to trade
  "lot_size": "65",                  // Lot size for the instrument
  "itm_points": "50",                // ITM points for strike selection
  "atr": "46",                       // Average True Range value
  "accounts": [...]                  // Account configurations
}
```

## Execution

### Run the Bot
```bash
python bot/sor/main.py
```

### Multi-Account Support
The bot supports simultaneous execution across multiple accounts using threading. Enable/disable accounts in the configuration file.

## Files Structure
```
bot/sor/
├── __init__.py          # Package initialization
├── config.json          # Configuration file
├── config_reader.py     # Configuration reader
├── strategy.py          # Strategy implementation
├── main.py             # Main execution script
└── README.md           # This file
```

## Strategy Flow

1. **9:45 AM**: Bot starts execution
2. **Entry Check**: Validates entry conditions
3. **Level Monitoring**: Monitors two levels simultaneously
4. **Trade Execution**: Executes ITM spread when level is touched
5. **12:00 PM**: Cutoff time - stops if no trade executed

## Key Features
- ✅ ITM (In-The-Money) spread execution
- ✅ Dual level monitoring (call and put)
- ✅ 12 PM cutoff for risk management
- ✅ Multi-account simultaneous execution
- ✅ Comprehensive logging and error handling

## Notes
- The bot uses the first 30-minute candle for entry validation
- The bot uses the first 15-minute candle close for put spread level calculation
- ITM strikes provide better probability but lower premium
- Monitor the bot during market hours for optimal performance
