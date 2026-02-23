# Groww Instrument CSV - Structure and Analysis

## Overview
The instrument CSV file contains comprehensive information about all tradeable instruments on Groww, including equities, indices, futures, and options across NSE and BSE exchanges.

## CSV Column Structure

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| exchange | string | Exchange name | NSE, BSE |
| exchange_token | string | Unique token by exchange | 2885, 1594, 11536 |
| trading_symbol | string | Symbol for placing orders | RELIANCE, TCS, INFY, NIFTY26APRFUT |
| groww_symbol | string | Groww's internal identifier | NSE-RELIANCE, BSE-TCS |
| name | string | Full name of instrument | Reliance Industries, Infosys |
| instrument_type | string | Type of instrument | EQ, CE, PE, FUT, IDX |
| segment | string | Market segment | CASH, FNO |
| series | string | Series classification | EQ, A, B (for stocks) |
| isin | string | ISIN code | INE002A01018 |
| underlying_symbol | string | Underlying asset (for derivatives) | RELIANCE, NIFTY |
| underlying_exchange_token | string | Token of underlying | 2885, 26000 |
| expiry_date | string | Expiry date (for derivatives) | 2026-04-28 |
| strike_price | number | Strike price (for options) | 1200, 1400 |
| lot_size | number | Minimum trading lot | 1 (stocks), 500 (options) |
| tick_size | number | Minimum price movement | 0.1, 0.05 |
| freeze_quantity | number | Max quantity per order | 15001, 20001 |
| is_reserved | boolean | Reserved status | 0, 1 |
| buy_allowed | boolean | Can buy | 0, 1 |
| sell_allowed | boolean | Can sell | 0, 1 |
| internal_trading_symbol | string | Internal symbol | RELIANCE-EQ |
| is_intraday | boolean | Intraday allowed | 0, 1 |

## Instrument Types

### 1. Equity Stocks (EQ)
**Segment**: CASH  
**Example - NSE:**
```csv
NSE,2885,RELIANCE,NSE-RELIANCE,Reliance Industries,EQ,CASH,EQ,INE002A01018,,,,,1,0.1,,,1,1,RELIANCE-EQ,0
NSE,1594,INFY,NSE-INFY,Infosys,EQ,CASH,EQ,INE009A01021,,,,,1,0.1,,,1,1,INFY-EQ,0
NSE,11536,TCS,NSE-TCS,TCS,EQ,CASH,EQ,INE467B01029,,,,,1,0.1,,,1,1,TCS-EQ,0
```

**Example - BSE:**
```csv
BSE,500325,RELIANCE,BSE-RELIANCE,Reliance Industries,EQ,CASH,A,INE002A01018,,,,,1,0.05,,,1,1,RELIANCE,0
BSE,500209,INFY,BSE-INFY,Infosys,EQ,CASH,A,INE009A01021,,,,,1,0.05,,,1,1,INFY,0
BSE,532540,TCS,BSE-TCS,TCS,EQ,CASH,A,INE467B01029,,,,,1,0.05,,,1,1,TCS,0
```

**Key Points:**
- `trading_symbol`: Simple symbol name (e.g., RELIANCE, TCS, INFY)
- `groww_symbol`: Format is `EXCHANGE-SYMBOL` (e.g., NSE-RELIANCE)
- `lot_size`: 1 (can buy single shares)
- `tick_size`: 0.1 for NSE, 0.05 for BSE
- `segment`: CASH
- `series`: EQ for NSE, A/B for BSE

### 2. Indices (IDX)
**Segment**: CASH  
**Example:**
```csv
NSE,NIFTY,NIFTY,NSE-NIFTY,NIFTY 50,IDX,CASH,,NIFTY,,,,,,,,,0,0,,0
NSE,BANKNIFTY,BANKNIFTY,NSE-BANKNIFTY,NIFTY Bank,IDX,CASH,,BANKNIFTY,,,,,,,,,0,0,,0
NSE,FINNIFTY,FINNIFTY,NSE-FINNIFTY,Nifty Financial Services,IDX,CASH,,FINNIFTY,,,,,,,,,0,0,,0
```

**Key Points:**
- `exchange_token`: Same as trading_symbol (NIFTY, BANKNIFTY)
- `instrument_type`: IDX
- `buy_allowed` and `sell_allowed`: 0 (indices cannot be traded directly)
- Used as underlying for derivatives

### 3. Futures (FUT)
**Segment**: FNO  
**Example:**
```csv
NSE,66691,NIFTY26APRFUT,NSE-NIFTY-28Apr26-FUT,,FUT,FNO,,,NIFTY,26000,2026-04-28,-0.01,65,0.1,1801,0,1,1,NIFTY26APRFUT,0
NSE,59175,BANKNIFTY26FEBFUT,NSE-BANKNIFTY-24Feb26-FUT,,FUT,FNO,,,BANKNIFTY,26009,2026-02-24,-0.01,30,0.2,601,0,1,1,BANKNIFTY26FEBFUT,0
NSE,66689,FINNIFTY26APRFUT,NSE-FINNIFTY-28Apr26-FUT,,FUT,FNO,,,FINNIFTY,26037,2026-04-28,-0.01,60,0.1,1801,0,1,1,FINNIFTY26APRFUT,0
```

**Key Points:**
- `trading_symbol`: Format is `SYMBOL##MMMFUT` (e.g., NIFTY26APRFUT)
- `underlying_symbol`: The index/stock it's based on
- `underlying_exchange_token`: Token of the underlying
- `expiry_date`: Contract expiry date
- `strike_price`: -0.01 (not applicable for futures)
- `lot_size`: Varies (30 for BANKNIFTY, 65 for NIFTY, 60 for FINNIFTY)

### 4. Call Options (CE)
**Segment**: FNO  
**Example:**
```csv
NSE,68532,360ONE26FEB1200CE,NSE-360ONE-24Feb26-1200-CE,,CE,FNO,,,360ONE,13061,2026-02-24,1200,500,0.05,20001,0,1,1,360ONE26FEB1200CE,0
NSE,56971,360ONE26FEB940CE,NSE-360ONE-24Feb26-940-CE,,CE,FNO,,,360ONE,13061,2026-02-24,940,500,0.05,20001,0,1,1,360ONE26FEB940CE,0
```

**Key Points:**
- `trading_symbol`: Format is `SYMBOL##MMM####CE` (e.g., 360ONE26FEB1200CE)
- `instrument_type`: CE (Call European)
- `strike_price`: The strike price (e.g., 1200, 940)
- `expiry_date`: Option expiry date
- `underlying_symbol`: The stock/index it's based on
- `lot_size`: Varies by underlying (500 for 360ONE, 400 for INFY)

### 5. Put Options (PE)
**Segment**: FNO  
**Example:**
```csv
NSE,68533,360ONE26FEB1200PE,NSE-360ONE-24Feb26-1200-PE,,PE,FNO,,,360ONE,13061,2026-02-24,1200,500,0.05,20001,0,1,1,360ONE26FEB1200PE,0
NSE,56970,360ONE26FEB900PE,NSE-360ONE-24Feb26-900-PE,,PE,FNO,,,360ONE,13061,2026-02-24,900,500,0.05,20001,1,1,1,360ONE26FEB900PE,0
```

**Key Points:**
- `trading_symbol`: Format is `SYMBOL##MMM####PE` (e.g., 360ONE26FEB1200PE)
- `instrument_type`: PE (Put European)
- Similar structure to CE options
- `strike_price`: The strike price
- `lot_size`: Same as corresponding CE options

## Trading Symbol Naming Convention

### Equity Stocks
- **NSE**: Simple symbol (e.g., `RELIANCE`, `TCS`, `INFY`)
- **BSE**: Simple symbol (e.g., `RELIANCE`, `TCS`, `INFY`)

### Indices
- Simple name (e.g., `NIFTY`, `BANKNIFTY`, `FINNIFTY`)

### Futures
- Format: `SYMBOL##MMMFUT`
  - `SYMBOL`: Underlying symbol
  - `##`: Last 2 digits of year (26 for 2026)
  - `MMM`: 3-letter month code (FEB, MAR, APR)
  - `FUT`: Futures identifier
- Examples:
  - `NIFTY26APRFUT` - NIFTY futures expiring April 2026
  - `BANKNIFTY26FEBFUT` - BANKNIFTY futures expiring February 2026

### Options (CE/PE)
- Format: `SYMBOL##MMM####CE/PE`
  - `SYMBOL`: Underlying symbol
  - `##`: Last 2 digits of year
  - `MMM`: 3-letter month code
  - `####`: Strike price (may vary in digits)
  - `CE`: Call option
  - `PE`: Put option
- Examples:
  - `360ONE26FEB1200CE` - 360ONE Call option, Feb 2026, Strike 1200
  - `360ONE26FEB1200PE` - 360ONE Put option, Feb 2026, Strike 1200

## Groww Symbol Format

The `groww_symbol` follows a consistent pattern:
- **Equity**: `EXCHANGE-SYMBOL` (e.g., `NSE-RELIANCE`, `BSE-TCS`)
- **Index**: `EXCHANGE-SYMBOL` (e.g., `NSE-NIFTY`)
- **Futures**: `EXCHANGE-UNDERLYING-DDMmmYY-FUT` (e.g., `NSE-NIFTY-28Apr26-FUT`)
- **Options**: `EXCHANGE-UNDERLYING-DDMmmYY-STRIKE-CE/PE` (e.g., `NSE-360ONE-24Feb26-1200-CE`)

## Exchange Trading Symbol Format

For API calls using `exchange_trading_symbols` parameter:
- Format: `EXCHANGE_TRADINGSYMBOL`
- Examples:
  - `NSE_RELIANCE` - Reliance stock on NSE
  - `NSE_NIFTY26APRFUT` - NIFTY April 2026 futures
  - `NSE_360ONE26FEB1200CE` - 360ONE Feb 2026 1200 Call option

## Key Instrument Properties

### Exchange Tokens
- **Unique identifier** assigned by the exchange
- Used for internal tracking
- Examples:
  - RELIANCE (NSE): 2885
  - TCS (NSE): 11536
  - INFY (NSE): 1594
  - NIFTY (Index): NIFTY
  - BANKNIFTY (Index): BANKNIFTY

### Lot Sizes
Different instruments have different lot sizes:

| Instrument | Lot Size | Example |
|------------|----------|---------|
| Equity Stocks | 1 | Can buy 1 share |
| NIFTY Futures | 65 | Must buy in multiples of 65 |
| BANKNIFTY Futures | 30 | Must buy in multiples of 30 |
| FINNIFTY Futures | 60 | Must buy in multiples of 60 |
| 360ONE Options | 500 | Must buy in multiples of 500 |
| INFY Options | 400 | Must buy in multiples of 400 |
| RELIANCE Options | 500 | Must buy in multiples of 500 |
| TCS Options | 175 | Must buy in multiples of 175 |

### Tick Sizes
Minimum price movement:

| Instrument Type | Tick Size | Example |
|----------------|-----------|---------|
| NSE Equity | 0.1 | Prices move in ₹0.10 increments |
| BSE Equity | 0.05 | Prices move in ₹0.05 increments |
| Options | 0.05 | Prices move in ₹0.05 increments |
| NIFTY Futures | 0.1 | Prices move in ₹0.10 increments |
| BANKNIFTY Futures | 0.2 | Prices move in ₹0.20 increments |

### Freeze Quantities
Maximum quantity allowed per order:

| Instrument | Freeze Quantity |
|------------|-----------------|
| RELIANCE Options | 15001 |
| 360ONE Options | 20001 |
| INFY Options | 16001 |
| TCS Options | 7001 |
| NIFTY Futures | 1801 |
| BANKNIFTY Futures | 601 |

## Practical Examples

### Example 1: Finding an Equity Stock
```python
import pandas as pd

# Load instruments
df = pd.read_csv('instrument.csv')

# Find RELIANCE on NSE
reliance = df[(df['exchange'] == 'NSE') & 
              (df['trading_symbol'] == 'RELIANCE') & 
              (df['segment'] == 'CASH')]

print(f"Exchange Token: {reliance['exchange_token'].values[0]}")
print(f"Groww Symbol: {reliance['groww_symbol'].values[0]}")
print(f"ISIN: {reliance['isin'].values[0]}")
print(f"Lot Size: {reliance['lot_size'].values[0]}")
print(f"Tick Size: {reliance['tick_size'].values[0]}")
```

**Output:**
```
Exchange Token: 2885
Groww Symbol: NSE-RELIANCE
ISIN: INE002A01018
Lot Size: 1
Tick Size: 0.1
```

### Example 2: Finding Current Month Futures
```python
import pandas as pd
from datetime import datetime

df = pd.read_csv('instrument.csv')

# Find NIFTY futures expiring in February 2026
nifty_fut = df[(df['underlying_symbol'] == 'NIFTY') & 
               (df['instrument_type'] == 'FUT') &
               (df['expiry_date'] == '2026-02-24')]

print(f"Trading Symbol: {nifty_fut['trading_symbol'].values[0]}")
print(f"Lot Size: {nifty_fut['lot_size'].values[0]}")
print(f"Expiry: {nifty_fut['expiry_date'].values[0]}")
```

**Output:**
```
Trading Symbol: NIFTY26FEBFUT
Lot Size: 65
Expiry: 2026-02-24
```

### Example 3: Finding ATM Options
```python
import pandas as pd

df = pd.read_csv('instrument.csv')

# Assume NIFTY is at 23500
current_nifty = 23500
expiry = '2026-02-24'

# Find options for this expiry
options = df[(df['underlying_symbol'] == 'NIFTY') & 
             (df['expiry_date'] == expiry) &
             (df['instrument_type'].isin(['CE', 'PE']))]

# Find ATM strike (closest to current price)
options['strike_diff'] = abs(options['strike_price'] - current_nifty)
atm_strike = options.loc[options['strike_diff'].idxmin(), 'strike_price']

# Get ATM CE and PE
atm_ce = options[(options['strike_price'] == atm_strike) & 
                 (options['instrument_type'] == 'CE')]
atm_pe = options[(options['strike_price'] == atm_strike) & 
                 (options['instrument_type'] == 'PE')]

print(f"ATM Strike: {atm_strike}")
print(f"CE Trading Symbol: {atm_ce['trading_symbol'].values[0]}")
print(f"PE Trading Symbol: {atm_pe['trading_symbol'].values[0]}")
```

### Example 4: Get All Strikes for an Expiry
```python
import pandas as pd

df = pd.read_csv('instrument.csv')

# Get all NIFTY options for Feb 2026 expiry
nifty_options = df[(df['underlying_symbol'] == 'NIFTY') & 
                   (df['expiry_date'] == '2026-02-24') &
                   (df['instrument_type'].isin(['CE', 'PE']))]

# Get unique strikes
strikes = sorted(nifty_options['strike_price'].unique())
print(f"Available strikes: {strikes[:10]}...")  # First 10
print(f"Total strikes: {len(strikes)}")

# Get CE and PE for a specific strike
strike = 23500
ce = nifty_options[(nifty_options['strike_price'] == strike) & 
                   (nifty_options['instrument_type'] == 'CE')]
pe = nifty_options[(nifty_options['strike_price'] == strike) & 
                   (nifty_options['instrument_type'] == 'PE')]

print(f"\nStrike {strike}:")
print(f"CE: {ce['trading_symbol'].values[0]}")
print(f"PE: {pe['trading_symbol'].values[0]}")
```

## Using with Groww API

### Example 1: Place Order Using CSV Data
```python
from growwapi import GrowwAPI
import pandas as pd

groww = GrowwAPI(API_AUTH_TOKEN)
df = pd.read_csv('instrument.csv')

# Find instrument
instrument = df[(df['exchange'] == 'NSE') & 
                (df['trading_symbol'] == 'RELIANCE') & 
                (df['segment'] == 'CASH')].iloc[0]

# Place order
order = groww.place_order(
    exchange=instrument['exchange'],
    trading_symbol=instrument['trading_symbol'],
    transaction_type=groww.TRANSACTION_TYPE_BUY,
    quantity=instrument['lot_size'],  # Use lot_size from CSV
    price=0,
    order_type=groww.ORDER_TYPE_MARKET,
    product=groww.PRODUCT_CNC,
    validity=groww.VALIDITY_DAY,
    segment=instrument['segment']
)

print(f"Order placed: {order['groww_order_id']}")
```

### Example 2: Get Live Data Using CSV
```python
from growwapi import GrowwAPI
import pandas as pd

groww = GrowwAPI(API_AUTH_TOKEN)
df = pd.read_csv('instrument.csv')

# Find instrument
instrument = df[(df['exchange'] == 'NSE') & 
                (df['trading_symbol'] == 'RELIANCE') & 
                (df['segment'] == 'CASH')].iloc[0]

# Construct exchange_trading_symbol
exchange_trading_symbol = f"{instrument['exchange']}_{instrument['trading_symbol']}"

# Get LTP
ltp_data = groww.get_ltp(
    exchange_trading_symbols=exchange_trading_symbol,
    segment=instrument['segment']
)

print(f"LTP: {ltp_data[exchange_trading_symbol]['ltp']}")
```

### Example 3: Option Chain with CSV
```python
from growwapi import GrowwAPI
import pandas as pd

groww = GrowwAPI(API_AUTH_TOKEN)
df = pd.read_csv('instrument.csv')

# Get all NIFTY options for a specific expiry
expiry = '2026-02-24'
nifty_options = df[(df['underlying_symbol'] == 'NIFTY') & 
                   (df['expiry_date'] == expiry) &
                   (df['instrument_type'].isin(['CE', 'PE']))]

# Get option chain from API
option_chain = groww.get_option_chain(
    exchange=groww.EXCHANGE_NFO,
    underlying='NIFTY',
    expiry=expiry
)

# Match CSV data with API data
for strike, data in option_chain['strikes'].items():
    # Find CE and PE from CSV
    ce_csv = nifty_options[(nifty_options['strike_price'] == float(strike)) & 
                           (nifty_options['instrument_type'] == 'CE')]
    pe_csv = nifty_options[(nifty_options['strike_price'] == float(strike)) & 
                           (nifty_options['instrument_type'] == 'PE')]
    
    if not ce_csv.empty and not pe_csv.empty:
        print(f"\nStrike {strike}:")
        print(f"  CE Symbol: {ce_csv['trading_symbol'].values[0]}, LTP: {data['CE']['ltp']}")
        print(f"  PE Symbol: {pe_csv['trading_symbol'].values[0]}, LTP: {data['PE']['ltp']}")
        print(f"  Lot Size: {ce_csv['lot_size'].values[0]}")
```

## Important Relationships

### 1. Exchange Token Mapping
- Each instrument has a unique `exchange_token` on its exchange
- The same stock on different exchanges has different tokens:
  - RELIANCE on NSE: 2885
  - RELIANCE on BSE: 500325

### 2. Underlying Relationships
For derivatives:
- `underlying_symbol` links to the base instrument
- `underlying_exchange_token` is the token of that base instrument
- Example: 360ONE options have underlying_exchange_token = 13061

### 3. Groww Symbol Usage
- Used in `get_instrument_by_groww_symbol()` method
- Format: `EXCHANGE-SYMBOL` for equities
- Format: `EXCHANGE-UNDERLYING-DATE-STRIKE-TYPE` for options

## Filtering Strategies

### Get All Equity Stocks
```python
equities = df[(df['instrument_type'] == 'EQ') & (df['segment'] == 'CASH')]
```

### Get All Indices
```python
indices = df[df['instrument_type'] == 'IDX']
```

### Get All Futures for an Underlying
```python
nifty_futures = df[(df['underlying_symbol'] == 'NIFTY') & 
                   (df['instrument_type'] == 'FUT')]
```

### Get All Options for an Underlying and Expiry
```python
options = df[(df['underlying_symbol'] == 'NIFTY') & 
             (df['expiry_date'] == '2026-02-24') &
             (df['instrument_type'].isin(['CE', 'PE']))]
```

### Get Specific Strike Options
```python
strike_options = df[(df['underlying_symbol'] == 'NIFTY') & 
                    (df['expiry_date'] == '2026-02-24') &
                    (df['strike_price'] == 23500)]
```

### Get Only Tradeable Instruments
```python
tradeable = df[(df['buy_allowed'] == 1) & (df['sell_allowed'] == 1)]
```

### Get Non-Reserved Instruments
```python
non_reserved = df[df['is_reserved'] == 0]
```

## Key Insights

1. **Exchange Differences**:
   - NSE has tick_size of 0.1 for equities
   - BSE has tick_size of 0.05 for equities
   - Different exchange_tokens for same stock

2. **Derivative Naming**:
   - Consistent pattern: SYMBOL + YY + MMM + STRIKE (for options) + TYPE
   - Year is 2-digit (26 for 2026)
   - Month is 3-letter uppercase (FEB, MAR, APR)

3. **Lot Sizes**:
   - Equities: Always 1
   - Futures: Varies by underlying (30-120)
   - Options: Varies by underlying (175-500)

4. **Segments**:
   - CASH: Equity stocks and indices
   - FNO: Futures and Options

5. **Trading Restrictions**:
   - Some instruments have `is_reserved = 1` (may have trading restrictions)
   - Indices have `buy_allowed = 0` and `sell_allowed = 0` (not directly tradeable)

6. **ISIN Codes**:
   - Only available for equity stocks
   - Empty for derivatives and indices
   - Useful for regulatory and settlement purposes

## Complete Workflow Example

```python
from growwapi import GrowwAPI
import pandas as pd

# Initialize
groww = GrowwAPI(API_AUTH_TOKEN)

# Load instruments (or use groww._load_instruments())
df = pd.read_csv('instrument.csv')

# Step 1: Find the instrument you want to trade
symbol = 'RELIANCE'
exchange = 'NSE'
segment = 'CASH'

instrument = df[(df['exchange'] == exchange) & 
                (df['trading_symbol'] == symbol) & 
                (df['segment'] == segment)].iloc[0]

print(f"Found: {instrument['name']}")
print(f"Exchange Token: {instrument['exchange_token']}")
print(f"Groww Symbol: {instrument['groww_symbol']}")

# Step 2: Get current price
exchange_trading_symbol = f"{exchange}_{symbol}"
ltp_data = groww.get_ltp(
    exchange_trading_symbols=exchange_trading_symbol,
    segment=segment
)
current_price = ltp_data[exchange_trading_symbol]['ltp']
print(f"Current Price: ₹{current_price}")

# Step 3: Place order
order = groww.place_order(
    exchange=exchange,
    trading_symbol=symbol,
    transaction_type=groww.TRANSACTION_TYPE_BUY,
    quantity=1,  # Use lot_size from CSV
    price=0,  # Market order
    order_type=groww.ORDER_TYPE_MARKET,
    product=groww.PRODUCT_CNC,
    validity=groww.VALIDITY_DAY,
    segment=segment
)

print(f"Order ID: {order['groww_order_id']}")
```

## Summary

The instrument CSV provides:
1. **Complete instrument universe** - All tradeable instruments
2. **Metadata** - Exchange tokens, lot sizes, tick sizes, freeze quantities
3. **Derivative details** - Underlying, expiry, strike prices
4. **Trading permissions** - Buy/sell allowed, reserved status
5. **Identification** - Multiple ways to identify instruments (exchange_token, trading_symbol, groww_symbol, ISIN)

**Key Usage:**
- Use `trading_symbol` for placing orders
- Use `groww_symbol` for Groww API lookups
- Use `exchange_token` for exchange-specific operations
- Use `segment` to determine CASH vs FNO
- Use `lot_size` to calculate order quantities
- Use `underlying_symbol` and `expiry_date` to filter derivatives
