# Groww API - Orders Documentation

## Overview
This guide describes how to manage orders using the SDK. You can create, modify, cancel, and retrieve order details for equities, derivatives, and commodities.

## Order Management Methods

### 1. Place Order
Place a new order for buying or selling instruments.

```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)

place_order_response = groww.place_order(
    exchange=groww.EXCHANGE_NSE,
    trading_symbol="RELIANCE",
    transaction_type=groww.TRANSACTION_TYPE_BUY,
    quantity=1,
    price=0,  # 0 for market orders
    order_type=groww.ORDER_TYPE_MARKET,
    product=groww.PRODUCT_CNC,
    validity=groww.VALIDITY_DAY,
    segment=groww.SEGMENT_CASH,
    trigger_price=0,  # For stop-loss orders
    order_reference_id="unique_reference_id"  # Optional: User-provided reference
)

print(place_order_response)
```

**Response:**
```json
{
    "groww_order_id": "GMK39038RDT490CCVRO",
    "exchange_order_id": "1234567890123456",
    "order_reference_id": "Ab-654321234-1628190"
}
```

### 2. Modify Order
Modify an existing pending order.

```python
modify_order_response = groww.modify_order(
    groww_order_id="GMK39038RDT490CCVRO",
    segment=groww.SEGMENT_CASH,
    quantity=2,  # New quantity
    price=250,  # New price
    order_type=groww.ORDER_TYPE_LIMIT,
    validity=groww.VALIDITY_DAY,
    trigger_price=0
)

print(modify_order_response)
```

**Response:**
```json
{
    "groww_order_id": "GMK39038RDT490CCVRO",
    "exchange_order_id": "1234567890123456",
    "order_reference_id": "Ab-654321234-1628190"
}
```

### 3. Cancel Order
Cancel a pending order.

```python
cancel_order_response = groww.cancel_order(
    groww_order_id="GMK39038RDT490CCVRO",
    segment=groww.SEGMENT_CASH
)

print(cancel_order_response)
```

**Response:**
```json
{
    "groww_order_id": "GMK39038RDT490CCVRO",
    "exchange_order_id": "1234567890123456",
    "order_reference_id": "Ab-654321234-1628190"
}
```

### 4. Get All Orders
Retrieve all orders for the current trading day.

```python
all_orders_response = groww.get_all_orders()
print(all_orders_response)
```

**Response:**
```json
{
    "orders": [
        {
            "groww_order_id": "GMK39038RDT490CCVRO",
            "exchange_order_id": "1234567890123456",
            "trading_symbol": "RELIANCE",
            "groww_symbol": "NSE-RELIANCE",
            "status": "COMPLETE",
            "quantity": 100,
            "price": 250,
            "trigger_price": 245,
            "filled_quantity": 100,
            "remaining_quantity": 10,
            "average_fill_price": 250,
            "deliverable_quantity": 10,
            "amo_status": "PENDING",
            "validity": "DAY",
            "exchange": "NSE",
            "order_type": "MARKET",
            "transaction_type": "BUY",
            "segment": "CASH",
            "product": "CNC",
            "created_at": "2019-08-24T14:15:22Z",
            "exchange_time": "2019-08-24T14:15:22Z",
            "trade_date": "2019-08-24T14:15:22Z",
            "order_reference_id": "Ab-654321234-1628190"
        }
    ]
}
```

### 5. Get Order Detail
Get detailed information about a specific order.

```python
order_detail_response = groww.get_order_detail(
    groww_order_id="GMK39038RDT490CCVRO",
    segment=groww.SEGMENT_CASH
)

print(order_detail_response)
```

**Response:**
```json
{
    "groww_order_id": "GMK39038RDT490CCVRO",
    "exchange_order_id": "1234567890123456",
    "trading_symbol": "RELIANCE",
    "groww_symbol": "NSE-RELIANCE",
    "status": "COMPLETE",
    "quantity": 100,
    "price": 250,
    "trigger_price": 245,
    "filled_quantity": 100,
    "remaining_quantity": 10,
    "average_fill_price": 250,
    "deliverable_quantity": 10,
    "amo_status": "PENDING",
    "validity": "DAY",
    "exchange": "NSE",
    "order_type": "MARKET",
    "transaction_type": "BUY",
    "segment": "CASH",
    "product": "CNC",
    "created_at": "2019-08-24T14:15:22Z",
    "exchange_time": "2019-08-24T14:15:22Z",
    "trade_date": "2019-08-24T14:15:22Z",
    "order_reference_id": "Ab-654321234-1628190"
}
```

## Order Parameters

### Required Parameters for Place Order

| Parameter | Type | Description |
|-----------|------|-------------|
| exchange | string | Exchange where the instrument is traded (NSE, BSE, NFO, etc.) |
| trading_symbol | string | Trading symbol of the instrument |
| transaction_type | string | BUY or SELL |
| quantity | number | Number of shares/contracts to trade |
| price | number | Order price (0 for market orders) |
| order_type | string | MARKET, LIMIT, SL, SL-M |
| product | string | CNC (Cash and Carry), MIS (Intraday), NRML (Normal) |
| validity | string | DAY, IOC (Immediate or Cancel) |
| segment | string | CASH, FNO, COMMODITY, etc. |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| trigger_price | number | Trigger price for stop-loss orders (default: 0) |
| order_reference_id | string | User-provided reference ID to track order status |

## Order Response Fields

| Field | Type | Description |
|-------|------|-------------|
| groww_order_id | string | Unique order ID assigned by Groww |
| exchange_order_id | string | Order ID assigned by the exchange |
| trading_symbol | string | Trading symbol of the instrument |
| groww_symbol | string | Groww's internal symbol |
| status | string | Order status (PENDING, COMPLETE, CANCELLED, REJECTED, etc.) |
| quantity | number | Total order quantity |
| price | number | Order price |
| trigger_price | number | Trigger price for stop-loss orders |
| filled_quantity | number | Quantity that has been filled |
| remaining_quantity | number | Quantity remaining to be filled |
| average_fill_price | number | Average price at which order was filled |
| deliverable_quantity | number | Quantity available for delivery |
| amo_status | string | After Market Order status (PENDING, PLACED, etc.) |
| validity | string | Order validity (DAY, IOC) |
| exchange | string | Exchange name |
| order_type | string | Type of order (MARKET, LIMIT, SL, SL-M) |
| transaction_type | string | BUY or SELL |
| segment | string | Market segment (CASH, FNO, etc.) |
| product | string | Product type (CNC, MIS, NRML) |
| created_at | string(date-time) | Timestamp when order was created |
| exchange_time | string(date-time) | Timestamp from exchange |
| trade_date | string(date-time) | Date on which trade has taken place |
| order_reference_id | string | User provided reference id to track the status of an order |

## Constants Available

### Exchange Constants
- `groww.EXCHANGE_NSE` - National Stock Exchange
- `groww.EXCHANGE_BSE` - Bombay Stock Exchange
- `groww.EXCHANGE_NFO` - NSE Futures & Options
- `groww.EXCHANGE_MCX` - Multi Commodity Exchange

### Transaction Type Constants
- `groww.TRANSACTION_TYPE_BUY` - Buy transaction
- `groww.TRANSACTION_TYPE_SELL` - Sell transaction

### Order Type Constants
- `groww.ORDER_TYPE_MARKET` - Market order
- `groww.ORDER_TYPE_LIMIT` - Limit order
- `groww.ORDER_TYPE_SL` - Stop Loss order
- `groww.ORDER_TYPE_SL_M` - Stop Loss Market order

### Product Constants
- `groww.PRODUCT_CNC` - Cash and Carry (delivery)
- `groww.PRODUCT_MIS` - Margin Intraday Square-off
- `groww.PRODUCT_NRML` - Normal (for F&O)

### Validity Constants
- `groww.VALIDITY_DAY` - Valid for the day
- `groww.VALIDITY_IOC` - Immediate or Cancel

### Segment Constants
- `groww.SEGMENT_CASH` - Cash segment (equity)
- `groww.SEGMENT_FNO` - Futures and Options segment
- `groww.SEGMENT_COMMODITY` - Commodity segment

## Order Status Values

Common order status values:
- `PENDING` - Order is pending
- `OPEN` - Order is open/active
- `COMPLETE` - Order is fully executed
- `CANCELLED` - Order has been cancelled
- `REJECTED` - Order was rejected
- `TRIGGER_PENDING` - Stop-loss order waiting for trigger

## Key Points

1. **Order Placement**: Use `place_order()` with all required parameters
2. **Order Modification**: Only pending orders can be modified using `modify_order()`
3. **Order Cancellation**: Only pending/open orders can be cancelled using `cancel_order()`
4. **Order Tracking**: Use `groww_order_id` to track orders, or use `order_reference_id` for custom tracking
5. **Market Orders**: Set `price=0` for market orders
6. **Stop Loss Orders**: Use `ORDER_TYPE_SL` or `ORDER_TYPE_SL_M` and set `trigger_price`
7. **Intraday vs Delivery**: Use `PRODUCT_MIS` for intraday, `PRODUCT_CNC` for delivery
8. **Order History**: `get_all_orders()` returns all orders for the current trading day

## Example: Complete Order Flow

```python
from growwapi import GrowwAPI

# Initialize
groww = GrowwAPI(API_AUTH_TOKEN)

# 1. Place a limit order
order = groww.place_order(
    exchange=groww.EXCHANGE_NSE,
    trading_symbol="RELIANCE",
    transaction_type=groww.TRANSACTION_TYPE_BUY,
    quantity=1,
    price=2500,
    order_type=groww.ORDER_TYPE_LIMIT,
    product=groww.PRODUCT_CNC,
    validity=groww.VALIDITY_DAY,
    segment=groww.SEGMENT_CASH,
    trigger_price=0,
    order_reference_id="my_order_001"
)

groww_order_id = order['groww_order_id']
print(f"Order placed: {groww_order_id}")

# 2. Check order status
order_detail = groww.get_order_detail(
    groww_order_id=groww_order_id,
    segment=groww.SEGMENT_CASH
)
print(f"Order status: {order_detail['status']}")

# 3. Modify order if needed
if order_detail['status'] == 'PENDING':
    modify_response = groww.modify_order(
        groww_order_id=groww_order_id,
        segment=groww.SEGMENT_CASH,
        quantity=2,
        price=2450,
        order_type=groww.ORDER_TYPE_LIMIT,
        validity=groww.VALIDITY_DAY,
        trigger_price=0
    )
    print(f"Order modified: {modify_response}")

# 4. Cancel order if needed
if order_detail['status'] in ['PENDING', 'OPEN']:
    cancel_response = groww.cancel_order(
        groww_order_id=groww_order_id,
        segment=groww.SEGMENT_CASH
    )
    print(f"Order cancelled: {cancel_response}")

# 5. Get all orders
all_orders = groww.get_all_orders()
print(f"Total orders today: {len(all_orders['orders'])}")
```

## Important Notes

1. **Order Validation**: Ensure all required parameters are provided correctly
2. **Segment Requirement**: Segment must be specified for modify, cancel, and get_order_detail operations
3. **Price for Market Orders**: Set price to 0 for market orders
4. **Trigger Price**: Only required for stop-loss orders (SL, SL-M)
5. **Order Reference ID**: Optional but useful for tracking orders in your application
6. **Order Lifecycle**: PENDING → OPEN → COMPLETE (or CANCELLED/REJECTED)
7. **Modification Restrictions**: Only pending orders can be modified
8. **Cancellation Restrictions**: Only pending/open orders can be cancelled
