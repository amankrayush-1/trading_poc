# Groww API - Live Data Documentation

## Overview
This guide describes how to fetch live data of instruments easily using the SDK. The API provides real-time market data including prices, quotes, OHLC data, and option chain information.

## Live Data Methods

### 1. Get LTP (Last Traded Price)
Fetch the last traded price for one or more instruments.

```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)

ltp_response = groww.get_ltp(
    exchange_trading_symbols="NSE_RELIANCE,NSE_TCS",
    segment=groww.SEGMENT_CASH
)

print(ltp_response)
```

**Response:**
```json
{
    "NSE_RELIANCE": {
        "ltp": 2450.50
    },
    "NSE_TCS": {
        "ltp": 3250.75
    }
}
```

**Parameters:**
- `exchange_trading_symbols` (string): Comma-separated list of exchange_trading_symbol (format: `EXCHANGE_TRADINGSYMBOL`)
- `segment` (string): Market segment (CASH, FNO, COMMODITY)

### 2. Get Quote
Fetch detailed quote information including bid/ask prices, volumes, and more.

```python
quote_response = groww.get_quote(
    exchange_trading_symbols="NSE_RELIANCE",
    segment=groww.SEGMENT_CASH
)

print(quote_response)
```

**Response:**
```json
{
    "NSE_RELIANCE": {
        "ltp": 2450.50,
        "open": 2440.00,
        "high": 2460.00,
        "low": 2435.00,
        "close": 2445.00,
        "volume": 1234567,
        "last_traded_time": "2019-08-24T14:15:22Z",
        "oi": 0,
        "oi_day_high": 0,
        "oi_day_low": 0,
        "lower_circuit": 2200.00,
        "upper_circuit": 2690.00,
        "best_bid_price": 2450.00,
        "best_bid_quantity": 100,
        "best_ask_price": 2451.00,
        "best_ask_quantity": 50,
        "total_buy_quantity": 5000,
        "total_sell_quantity": 4500,
        "average_traded_price": 2447.50,
        "exchange": "NSE",
        "trading_symbol": "RELIANCE",
        "tick_size": 0.05
    }
}
```

**Parameters:**
- `exchange_trading_symbols` (string): Comma-separated list of exchange_trading_symbol
- `segment` (string): Market segment

### 3. Get OHLC (Open, High, Low, Close)
Fetch OHLC data for instruments.

```python
ohlc_response = groww.get_ohlc(
    exchange_trading_symbols="NSE_RELIANCE,NSE_TCS",
    segment=groww.SEGMENT_CASH
)

print(ohlc_response)
```

**Response:**
```json
{
    "NSE_RELIANCE": {
        "open": 2440.00,
        "high": 2460.00,
        "low": 2435.00,
        "close": 2445.00
    },
    "NSE_TCS": {
        "open": 3240.00,
        "high": 3260.00,
        "low": 3235.00,
        "close": 3245.00
    }
}
```

**Parameters:**
- `exchange_trading_symbols` (string): Comma-separated list of exchange_trading_symbol
- `segment` (string): Market segment

### 4. Get Option Chain
Fetch option chain data for a specific underlying and expiry.

```python
option_chain_response = groww.get_option_chain(
    exchange=groww.EXCHANGE_NFO,
    underlying="NIFTY",
    expiry="2025-11-18"
)

print(option_chain_response)
```

**Response:**
```json
{
    "expiry": "2025-11-18",
    "underlying": "NIFTY",
    "underlying_ltp": 23532.35,
    "strikes": {
        "23400": {
            "CE": {
                "greeks": {
                    "delta": 0.9936,
                    "gamma": 0,
                    "theta": -1.0787,
                    "vega": 0.6943,
                    "rho": 5.1862,
                    "iv": 25.3409
                },
                "trading_symbol": "NIFTY25N1823400CE",
                "ltp": 2200,
                "open_interest": 7,
                "volume": 5
            },
            "PE": {
                "greeks": {
                    "delta": -0.0064,
                    "gamma": 0,
                    "theta": -1.0787,
                    "vega": 0.6943,
                    "rho": -0.0373,
                    "iv": 25.3409
                },
                "trading_symbol": "NIFTY25N1823400PE",
                "ltp": 2.05,
                "open_interest": 7453,
                "volume": 9339
            }
        },
        "23450": {
            "CE": {
                "greeks": {
                    "delta": 0.9927,
                    "gamma": 0,
                    "theta": -1.2027,
                    "vega": 0.7774,
                    "rho": 5.1862,
                    "iv": 25.2306
                },
                "trading_symbol": "NIFTY25N1823450CE",
                "ltp": 2082.9,
                "open_interest": 4,
                "volume": 0
            },
            "PE": {
                "greeks": {
                    "delta": -0.0073,
                    "gamma": 0,
                    "theta": -1.2027,
                    "vega": 0.7774,
                    "rho": -0.0424,
                    "iv": 25.2306
                },
                "trading_symbol": "NIFTY25N1823450PE",
                "ltp": 2.35,
                "open_interest": 378,
                "volume": 74
            }
        }
    }
}
```

**Parameters:**
- `exchange` (string): Exchange (typically NFO for options)
- `underlying` (string): Underlying symbol (e.g., "NIFTY", "BANKNIFTY")
- `expiry` (string): Expiry date in YYYY-MM-DD format

### 5. Get Greeks
Fetch option Greeks for a specific option contract.

```python
greeks_response = groww.get_greeks(
    exchange=groww.EXCHANGE_NSE,
    underlying="NIFTY",
    trading_symbol="NIFTY25O1425100CE",
    expiry="2025-10-14"
)

print(greeks_response)
```

**Response:**
```json
{
    "delta": 0.9936,
    "gamma": 0,
    "theta": -1.0787,
    "vega": 0.6943,
    "rho": 5.1862,
    "iv": 8.2383
}
```

**Parameters:**
- `exchange` (string): Exchange
- `underlying` (string): Underlying symbol
- `trading_symbol` (string): Option trading symbol
- `expiry` (string): Expiry date in YYYY-MM-DD format

## Response Field Descriptions

### LTP Response Fields
| Field | Type | Description |
|-------|------|-------------|
| ltp | number | Last traded price |

### Quote Response Fields
| Field | Type | Description |
|-------|------|-------------|
| ltp | number | Last traded price |
| open | number | Opening price of the day |
| high | number | Highest price of the day |
| low | number | Lowest price of the day |
| close | number | Previous day's closing price |
| volume | number | Total volume traded |
| last_traded_time | string(date-time) | Timestamp of last trade |
| oi | number | Open Interest (for derivatives) |
| oi_day_high | number | Day's highest open interest |
| oi_day_low | number | Day's lowest open interest |
| lower_circuit | number | Lower circuit limit |
| upper_circuit | number | Upper circuit limit |
| best_bid_price | number | Best bid price |
| best_bid_quantity | number | Quantity at best bid |
| best_ask_price | number | Best ask price |
| best_ask_quantity | number | Quantity at best ask |
| total_buy_quantity | number | Total buy quantity in order book |
| total_sell_quantity | number | Total sell quantity in order book |
| average_traded_price | number | Average traded price |
| exchange | string | Exchange name |
| trading_symbol | string | Trading symbol |
| tick_size | number | Minimum price movement |

### OHLC Response Fields
| Field | Type | Description |
|-------|------|-------------|
| open | number | Opening price |
| high | number | Highest price |
| low | number | Lowest price |
| close | number | Closing/current price |

### Option Chain Response Fields
| Field | Type | Description |
|-------|------|-------------|
| expiry | string | Expiry date |
| underlying | string | Underlying symbol |
| underlying_ltp | number | Current price of underlying |
| strikes | object | Strike-wise option data |

**Strike Data (for each strike):**
- `CE` (Call Option) and `PE` (Put Option) objects containing:
  - `greeks`: Delta, Gamma, Theta, Vega, Rho, IV
  - `trading_symbol`: Option trading symbol
  - `ltp`: Last traded price
  - `open_interest`: Open interest
  - `volume`: Volume traded

### Greeks Response Fields
| Field | Type | Description |
|-------|------|-------------|
| delta | number | Rate of change of option price with respect to underlying price |
| gamma | number | Rate of change of delta with respect to underlying price |
| theta | number | Rate of change of option price with respect to time (time decay) |
| vega | number | Rate of change of option price with respect to volatility |
| rho | number | Rate of change of option price with respect to interest rate |
| iv | number | Implied Volatility (percentage) |

## Complete Example: Trading with Live Data

```python
from growwapi import GrowwAPI

# Initialize
groww = GrowwAPI(API_AUTH_TOKEN)

# 1. Get instrument details
instrument = groww.get_instrument_by_groww_symbol("NSE-RELIANCE")

# 2. Get current price
exchange_symbol = f"NSE_{instrument['trading_symbol']}"
ltp_data = groww.get_ltp(
    exchange_trading_symbols=exchange_symbol,
    segment=groww.SEGMENT_CASH
)
current_price = ltp_data[exchange_symbol]['ltp']
print(f"Current price: {current_price}")

# 3. Get detailed quote
quote_data = groww.get_quote(
    exchange_trading_symbols=exchange_symbol,
    segment=groww.SEGMENT_CASH
)
quote = quote_data[exchange_symbol]
print(f"Day High: {quote['high']}, Day Low: {quote['low']}")
print(f"Volume: {quote['volume']}")
print(f"Best Bid: {quote['best_bid_price']} x {quote['best_bid_quantity']}")
print(f"Best Ask: {quote['best_ask_price']} x {quote['best_ask_quantity']}")

# 4. Get OHLC data
ohlc_data = groww.get_ohlc(
    exchange_trading_symbols=exchange_symbol,
    segment=groww.SEGMENT_CASH
)
ohlc = ohlc_data[exchange_symbol]
print(f"OHLC: O={ohlc['open']}, H={ohlc['high']}, L={ohlc['low']}, C={ohlc['close']}")

# 5. For options: Get option chain
option_chain = groww.get_option_chain(
    exchange=groww.EXCHANGE_NFO,
    underlying="NIFTY",
    expiry="2025-11-18"
)
print(f"Underlying LTP: {option_chain['underlying_ltp']}")

# Get specific strike data
strike_23400 = option_chain['strikes']['23400']
ce_data = strike_23400['CE']
pe_data = strike_23400['PE']

print(f"23400 CE: LTP={ce_data['ltp']}, Delta={ce_data['greeks']['delta']}, IV={ce_data['greeks']['iv']}")
print(f"23400 PE: LTP={pe_data['ltp']}, Delta={pe_data['greeks']['delta']}, IV={pe_data['greeks']['iv']}")

# 6. Get Greeks for specific option
greeks = groww.get_greeks(
    exchange=groww.EXCHANGE_NFO,
    underlying="NIFTY",
    trading_symbol="NIFTY25O1425100CE",
    expiry="2025-10-14"
)
print(f"Greeks: Delta={greeks['delta']}, Theta={greeks['theta']}, IV={greeks['iv']}")
```

## Exchange Trading Symbol Format

The `exchange_trading_symbols` parameter uses a specific format:
- Format: `EXCHANGE_TRADINGSYMBOL`
- Examples:
  - `NSE_RELIANCE` - Reliance on NSE
  - `BSE_RELIANCE` - Reliance on BSE
  - `NFO_NIFTY25N1823400CE` - NIFTY option on NFO

**Multiple Symbols:**
Use comma-separated values: `"NSE_RELIANCE,NSE_TCS,NSE_INFY"`

## Key Points

1. **Multiple Instruments**: All methods support fetching data for multiple instruments in a single call using comma-separated symbols

2. **Response Format**: Responses are dictionaries with exchange_trading_symbol as keys

3. **Segment Requirement**: Segment must be specified for all live data calls

4. **Option Chain**: Provides comprehensive option data including:
   - All strikes for a given expiry
   - Both CE (Call) and PE (Put) data
   - Greeks for each option
   - Open Interest and Volume

5. **Greeks Availability**: 
   - Available only for option contracts
   - Includes Delta, Gamma, Theta, Vega, Rho, and IV
   - Can be fetched via `get_option_chain()` or `get_greeks()`

6. **Real-time Data**: All data is real-time during market hours

7. **Circuit Limits**: Quote data includes upper and lower circuit limits

8. **Order Book Depth**: Quote provides best bid/ask prices and total buy/sell quantities

## Option Greeks Explained

| Greek | Description | Interpretation |
|-------|-------------|----------------|
| **Delta** | Price sensitivity to underlying | 0 to 1 for CE, 0 to -1 for PE. Higher absolute value = more sensitive |
| **Gamma** | Rate of change of Delta | Higher gamma = Delta changes faster |
| **Theta** | Time decay | Negative value = option loses value over time |
| **Vega** | Volatility sensitivity | Higher vega = more sensitive to volatility changes |
| **Rho** | Interest rate sensitivity | Usually less significant for short-term options |
| **IV** | Implied Volatility | Higher IV = higher option premium |

## Use Cases

### 1. Price Monitoring
```python
# Monitor multiple stocks
symbols = "NSE_RELIANCE,NSE_TCS,NSE_INFY,NSE_HDFCBANK"
prices = groww.get_ltp(exchange_trading_symbols=symbols, segment=groww.SEGMENT_CASH)

for symbol, data in prices.items():
    print(f"{symbol}: ₹{data['ltp']}")
```

### 2. Market Depth Analysis
```python
# Analyze order book
quote = groww.get_quote(exchange_trading_symbols="NSE_RELIANCE", segment=groww.SEGMENT_CASH)
reliance = quote['NSE_RELIANCE']

bid_ask_spread = reliance['best_ask_price'] - reliance['best_bid_price']
buy_sell_ratio = reliance['total_buy_quantity'] / reliance['total_sell_quantity']

print(f"Spread: {bid_ask_spread}")
print(f"Buy/Sell Ratio: {buy_sell_ratio}")
```

### 3. Option Strategy Selection
```python
# Find ATM options
chain = groww.get_option_chain(
    exchange=groww.EXCHANGE_NFO,
    underlying="NIFTY",
    expiry="2025-11-18"
)

underlying_price = chain['underlying_ltp']
strikes = chain['strikes']

# Find nearest ATM strike
atm_strike = min(strikes.keys(), key=lambda x: abs(float(x) - underlying_price))
print(f"ATM Strike: {atm_strike}")

# Get ATM option data
atm_ce = strikes[atm_strike]['CE']
atm_pe = strikes[atm_strike]['PE']

print(f"ATM CE: Price={atm_ce['ltp']}, Delta={atm_ce['greeks']['delta']}")
print(f"ATM PE: Price={atm_pe['ltp']}, Delta={atm_pe['greeks']['delta']}")
```

### 4. Volatility Analysis
```python
# Compare IV across strikes
chain = groww.get_option_chain(
    exchange=groww.EXCHANGE_NFO,
    underlying="NIFTY",
    expiry="2025-11-18"
)

for strike, data in chain['strikes'].items():
    ce_iv = data['CE']['greeks']['iv']
    pe_iv = data['PE']['greeks']['iv']
    print(f"Strike {strike}: CE IV={ce_iv}%, PE IV={pe_iv}%")
```

## Important Notes

1. **Rate Limits**: Be mindful of API rate limits when fetching live data frequently

2. **Market Hours**: Live data is available during market hours; outside market hours, you'll get last available data

3. **Data Freshness**: LTP and Quote data are real-time with minimal delay

4. **Option Chain Size**: Option chains can be large; consider filtering strikes based on your needs

5. **Greeks Calculation**: Greeks are calculated by the exchange/broker and updated in real-time

6. **Segment Matching**: Ensure the segment matches the instrument type:
   - CASH for equities
   - FNO for futures and options
   - COMMODITY for commodity derivatives

7. **Symbol Format**: Always use the correct exchange_trading_symbol format (EXCHANGE_SYMBOL)

8. **Error Handling**: Handle cases where instruments might not have data (e.g., suspended stocks)

## Best Practices

1. **Batch Requests**: Fetch multiple instruments in one call instead of multiple individual calls
2. **Cache Data**: Cache instrument metadata to avoid repeated lookups
3. **Use Appropriate Method**: Use `get_ltp()` for just price, `get_quote()` for detailed data
4. **Option Chain Filtering**: Filter option chain data to relevant strikes to reduce data size
5. **Greeks Monitoring**: Monitor Greeks for option positions to manage risk effectively
