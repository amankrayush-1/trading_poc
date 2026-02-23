# Groww Trading API - Python SDK Documentation Summary

## Overview
The Groww Trading API enables automated trading strategies with seamless access to real-time market data, order placement, portfolio management, and more. The Python SDK wraps REST-like APIs into easy-to-use Python methods.

## Key Features
- **Trade with Ease**: Place, modify, and cancel orders across Equity, F&O, and Commodities
- **Real-time Market Data**: Fetch live market prices, historical data, and order book depth
- **Secure Authentication**: Industry-standard OAuth 2.0 for secure access
- **Comprehensive SDK**: Quick start with Python SDK
- **WebSockets for Streaming**: Subscribe to real-time market feeds and order updates
- **Multi-Asset Trading**: Trade across NSE, BSE, and MCX exchanges

## Prerequisites
1. A Groww account
2. Basic knowledge of Python and REST APIs
3. Python 3.9+ installed
4. Active Trading API Subscription (purchase from [Groww Trading APIs page](https://groww.in/user/profile/trading-apis))

**Note**: Supports equity (CASH), derivatives (FNO), and commodities (COMMODITY) trading across NSE, BSE, and MCX exchanges.

## Installation

```bash
pip install growwapi
```

To upgrade:
```bash
pip install --upgrade growwapi
```

## Authentication

There are two authentication approaches:

### Approach 1: API Key and Secret Flow
**Requires daily approval on Groww Cloud API Keys Page**

1. Go to [Groww Cloud API Keys Page](https://groww.in/trade-api/api-keys)
2. Log in to your Groww account
3. Click 'Generate API key'
4. Enter the name for the key and click Continue
5. Copy API Key and Secret

**Usage:**
```python
from growwapi import GrowwAPI
import pyotp

api_key = "YOUR_API_KEY"
secret = "YOUR_API_SECRET"

access_token = GrowwAPI.get_access_token(api_key=api_key, secret=secret)
# Use access_token to initiate GrowwAPI
groww = GrowwAPI(access_token)
```

### Approach 2: TOTP Flow (Recommended)
**No Expiry - Uses TOTP token and TOTP QR code**

1. Go to [Groww Cloud API Keys Page](https://groww.in/trade-api/api-keys)
2. Log in to your Groww account
3. Click 'Generate TOTP token' (dropdown under Generate API Key button)
4. Enter the name for the key and click Continue
5. Copy the TOTP token and Secret or scan QR via authenticator app

**Install pyotp library:**
```bash
pip install pyotp
```

**Usage:**
```python
from growwapi import GrowwAPI
import pyotp

api_key = "YOUR_TOTP_TOKEN"

# Generate TOTP using the secret
totp_gen = pyotp.TOTP('YOUR_TOTP_SECRET')
totp = totp_gen.now()

access_token = GrowwAPI.get_access_token(api_key=api_key, totp=totp)
# Use access_token to initiate GrowwAPI
groww = GrowwAPI(access_token)
```

## Sample Order Placement

```python
from growwapi import GrowwAPI

# Groww API Credentials
API_AUTH_TOKEN = "your_token"  # Access token from authentication

# Initialize Groww API
groww = GrowwAPI(API_AUTH_TOKEN)

place_order_response = groww.place_order(
    trading_symbol="WIPRO",
    quantity=1, 
    validity=groww.VALIDITY_DAY,
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    product=groww.PRODUCT_CNC,
    order_type=groww.ORDER_TYPE_LIMIT,
    transaction_type=groww.TRANSACTION_TYPE_BUY,
    price=250,               # Optional: Price for Limit orders
    trigger_price=245,       # Optional: Trigger price if applicable
    order_reference_id="Ab-654321234-1628190"  # Optional: 8-20 char alphanumeric reference ID
)
print(place_order_response)
```

## API Categories

The SDK provides the following main categories:

1. **Instruments** - Search and retrieve instrument details
2. **Orders** - Place, modify, cancel orders
3. **Smart Orders** - Advanced order types
4. **Portfolio** - Holdings and positions management
5. **Margin** - Margin calculations and requirements
6. **Live Data** - Real-time market quotes, LTP, OHLC
7. **Historical Data** - Historical price data
8. **Backtesting** - Test trading strategies
9. **Feed** - WebSocket streaming for live updates
10. **User** - User profile and account information
11. **Annexures** - Reference data and constants
12. **Exceptions** - Error handling

## Rate Limits

Rate limits are applied at the **type level**, not individual APIs. All APIs in a type share the same limit.

| Type | Requests | Limit (Per second) | Limit (Per minute) |
|------|----------|-------------------|-------------------|
| Orders | Create, Modify, Cancel Order | 15 | 250 |
| Live Data | Market Quote, LTP, OHLC | 10 | 300 |
| Non Trading | Order Status, Order list, Trade list, Positions, Holdings, Margin | 20 | 500 |

**Live Feed**: Up to 1000 subscriptions allowed at a time.

## Important Constants

### Exchanges
- `EXCHANGE_NSE` - National Stock Exchange
- `EXCHANGE_BSE` - Bombay Stock Exchange
- `EXCHANGE_MCX` - Multi Commodity Exchange

### Segments
- `SEGMENT_CASH` - Equity/Cash segment
- `SEGMENT_FNO` - Futures & Options
- `SEGMENT_COMMODITY` - Commodities

### Products
- `PRODUCT_CNC` - Cash and Carry (delivery)
- `PRODUCT_INTRADAY` - Intraday/MIS
- `PRODUCT_NORMAL` - Normal/NRML

### Order Types
- `ORDER_TYPE_LIMIT` - Limit order
- `ORDER_TYPE_MARKET` - Market order
- `ORDER_TYPE_SL` - Stop Loss order
- `ORDER_TYPE_SL_M` - Stop Loss Market order

### Transaction Types
- `TRANSACTION_TYPE_BUY` - Buy order
- `TRANSACTION_TYPE_SELL` - Sell order

### Validity
- `VALIDITY_DAY` - Valid for the day
- `VALIDITY_IOC` - Immediate or Cancel

## Documentation Links

- **Python SDK Docs**: https://groww.in/trade-api/docs/python-sdk
- **cURL Docs**: https://groww.in/trade-api/docs/curl
- **API Keys Management**: https://groww.in/trade-api/api-keys

## Next Steps

To explore specific functionality:
1. **Instruments** - Learn how to search for trading symbols
2. **Orders** - Detailed order management operations
3. **Smart Orders** - Advanced order types like GTT, OCO
4. **Portfolio** - View holdings and positions
5. **Live Data** - Real-time market data streaming
6. **Historical Data** - Access historical price data for backtesting

## Support

For issues and updates, refer to:
- **Exceptions** documentation for error handling
- **Changelog** for latest updates and changes
- **Annexures** for reference data and enumerations