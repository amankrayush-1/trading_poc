# Groww API - Instruments Documentation

## Overview
This guide explains how to download and use instrument data with the Groww API SDK.

## Key Concepts

### Instruments
Instruments are the financial securities that can be traded on exchanges. The Groww API provides methods to:
- Download instrument data as CSV
- Query instruments by various identifiers
- Access instrument metadata

## Methods

### 1. Load Instruments
```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)
groww._load_instruments()
```

### 2. Get Instrument by Groww Symbol
```python
selected = groww.get_instrument_by_groww_symbol("NSE-RELIANCE")
print(selected)
```

### 3. Get Instrument by Exchange and Trading Symbol
```python
response = groww.get_instrument_by_exchange_and_trading_symbol(
    exchange=groww.EXCHANGE_NSE,
    trading_symbol="RELIANCE"
)
print(response)
```

### 4. Get Instrument by Exchange Token
```python
response = groww.get_instrument_by_exchange_token(
    exchange_token="2885"
)
print(response)
```

### 5. Get All Instruments
```python
instruments_df = groww.get_all_instruments()
print(instruments_df.head())
```

## Complete Example

```python
import pandas as pd
from growwapi import GrowwAPI

# Groww API Credentials (Replace with your actual credentials)
API_AUTH_TOKEN = "your_token"

# Initialize Groww API
groww = GrowwAPI(API_AUTH_TOKEN)

# Select an instrument (example: Reliance Industries)
selected = groww.get_instrument_by_groww_symbol("NSE-RELIANCE")

# Fetch latest price data for the selected instrument
ltp_response = groww.get_ltp(
    exchange_trading_symbols="NSE_" + selected['trading_symbol'],
    segment=selected['segment'],
)

print("Live Data:", ltp_response)
```

**Output:**
```
# The latest price data for the selected instrument is printed
{"ltp" : 149.5}
```

## Instrument CSV Columns

The CSV contains the following columns (separated by commas):

| Name | Type | Description |
|------|------|-------------|
| exchange | string | The Exchange where the instrument is traded |
| exchange_token | string | The unique token assigned to the instrument by the exchange |
| trading_symbol | string | The trading symbol of the instrument to place orders with |
| groww_symbol | string | The symbol used by Groww to identify the instrument |
| name | string | The name of the instrument |
| instrument_type | string | The type of the instrument |
| segment | string | Segment of the instrument such as CASH, FNO etc. |
| series | string | The series of the instrument (e.g., EQ, A, B, etc.) |
| isin | string | The ISIN (International Securities Identification Number) of the instrument |
| underlying_symbol | string | The symbol of the underlying asset (for derivatives). Empty for stocks and indices |
| underlying_exchange_token | string | The exchange token of the underlying asset |
| lot_size | number | The minimum lot size for trading the instrument |
| expiry_date | string | The expiry date of the instrument (for Derivatives) |
| strike_price | number | The strike price of the instrument (for Options) |
| tick_size | number | The minimum price movement for the instrument |
| freeze_quantity | number | The quantity that is frozen for trading |
| is_reserved | boolean | Whether the instrument is reserved for trading |
| buy_allowed | boolean | Whether buying the instrument is allowed |
| sell_allowed | boolean | Whether selling the instrument is allowed |

## Advanced Uses

You can download the CSV file and use it for your own purposes:

```python
from growwapi import GrowwAPI
import pandas as pd

# Load the CSV file
instrument_df = pd.read_csv(groww.INSTRUMENT_CSV_URL)  
# groww.INSTRUMENT_CSV_URL points to the url to download the instrument csv file

# OR you can also do this
instrument_df = groww._load_instruments()
print(instrument_df.head())
```

## Key Points

1. **Instrument Identification**: Instruments can be identified by:
   - Groww Symbol (e.g., "NSE-RELIANCE")
   - Exchange + Trading Symbol (e.g., NSE + "RELIANCE")
   - Exchange Token (e.g., "2885")

2. **CSV Access**: The instrument CSV can be accessed via:
   - `groww.INSTRUMENT_CSV_URL` - URL to download the CSV
   - `groww._load_instruments()` - Load instruments as pandas DataFrame

3. **Data Usage**: The instrument data is essential for:
   - Placing orders (requires trading_symbol)
   - Fetching live prices (requires exchange_trading_symbols format)
   - Understanding instrument properties (lot_size, tick_size, etc.)

4. **Derivatives Support**: The CSV includes derivative instruments with:
   - Expiry dates
   - Strike prices
   - Underlying symbols and tokens

## Related Links
- Exchange types: See Annexures for Exchange definitions
- Instrument types: See Annexures for Instrument Type definitions
- Segments: See Annexures for Segment definitions (CASH, FNO, etc.)
