# Groww API - Historical Data Documentation

## Overview
This guide describes how to fetch historical data of instruments easily using the SDK. Historical candle data is essential for backtesting strategies, technical analysis, and building trading algorithms.

## Historical Data Method

### Get Historical Candle Data
Fetch historical candle data for an instrument using the `get_historical_candle_data` method.

```python
from growwapi import GrowwAPI
import time

# Groww API Credentials (Replace with your actual credentials)
API_AUTH_TOKEN = "your_token"

# Initialize Groww API
groww = GrowwAPI(API_AUTH_TOKEN)

# you can give time programatically.
end_time_in_millis = int(time.time() * 1000)  # epoch time in milliseconds
start_time_in_millis = end_time_in_millis - (24 * 60 * 60 * 1000)  # last 24 hours

# OR

# you can give start time and end time in yyyy-MM-dd HH:mm:ss format.
end_time = "2025-02-27 14:00:00"
start_time = "2025-02-27 10:00:00"

historical_data_response = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time=start_time,
    end_time=end_time,
    interval_in_minutes=5  # Optional: Interval in minutes for the candle data
)

print(historical_data_response)
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| exchange | string | Yes* | Stock exchange (NSE, BSE, NFO, etc.) |
| segment | string | Yes* | Segment of the instrument such as CASH, FNO etc. |
| trading_symbol | string | Yes* | Trading Symbol of the instrument as defined by the exchange |
| start_time | string | Yes* | Time in YYYY-MM-DD HH:mm:ss or epoch milliseconds format from which data is required |
| end_time | string | Yes* | Time in YYYY-MM-DD HH:mm:ss or epoch milliseconds format till when data is required |
| interval_in_minutes | int | No | Interval in minutes for the candle data (default: 1) |

*Required parameters

## Response Structure

```json
{
  "candles": [
    [
      1633072800,  // candle timestamp in epoch second
      150,         // open price
      155,         // high price
      145,         // low price
      152,         // close price
      10000        // volume
    ]
  ],
  "start_time": "2025-01-01 15:30:00",
  "end_time": "2025-01-01 15:30:00",
  "interval_in_minutes": 5
}
```

## Response Schema

| Field | Type | Description |
|-------|------|-------------|
| candles | array[array] | List of candles. Each candle has: timestamp (epoch second), open (float), high (float), low (float), close (float), volume (int) in that order |
| start_time | string | Start time in yyyy-MM-dd HH:mm:ss |
| end_time | string | End time in yyyy-MM-dd HH:mm:ss |
| interval_in_minutes | int | Interval in minutes |

## Candle Data Structure

Each candle in the `candles` array is an array with 6 elements:
1. **Timestamp** (int): Candle timestamp in epoch seconds
2. **Open** (float): Opening price
3. **High** (float): Highest price in the interval
4. **Low** (float): Lowest price in the interval
5. **Close** (float): Closing price
6. **Volume** (int): Trading volume

## Supported Intervals and Limits

| Candle Interval | Max Duration per Request | Historical Data Available |
|-----------------|--------------------------|---------------------------|
| **1 min** | 7 days | Last 3 months |
| **5 min** | 15 days | Last 3 months |
| **10 min** | 30 days | Last 3 months |
| **1 hour (60 min)** | 150 days | Last 3 months |
| **4 hours (240 min)** | 365 days | Last 3 months |
| **1 day (1440 min)** | 1080 days (~3 years) | Full history |
| **1 week (10080 min)** | No Limit | Full history |

## Time Format Options

### Option 1: Epoch Milliseconds
```python
import time

end_time_in_millis = int(time.time() * 1000)
start_time_in_millis = end_time_in_millis - (7 * 24 * 60 * 60 * 1000)  # 7 days ago

historical_data = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time=start_time_in_millis,
    end_time=end_time_in_millis,
    interval_in_minutes=5
)
```

### Option 2: String Format (YYYY-MM-DD HH:mm:ss)
```python
historical_data = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-02-20 09:15:00",
    end_time="2025-02-27 15:30:00",
    interval_in_minutes=5
)
```

## Complete Examples

### Example 1: Fetch Daily Candles for Backtesting
```python
from growwapi import GrowwAPI
from datetime import datetime, timedelta

groww = GrowwAPI(API_AUTH_TOKEN)

# Get 1 year of daily data
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

historical_data = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time=start_date.strftime("%Y-%m-%d 00:00:00"),
    end_time=end_date.strftime("%Y-%m-%d 23:59:59"),
    interval_in_minutes=1440  # Daily candles
)

# Process candles
for candle in historical_data['candles']:
    timestamp, open_price, high, low, close, volume = candle
    date = datetime.fromtimestamp(timestamp)
    print(f"{date}: O={open_price}, H={high}, L={low}, C={close}, V={volume}")
```

### Example 2: Intraday Analysis with 5-minute Candles
```python
from growwapi import GrowwAPI
import pandas as pd
from datetime import datetime

groww = GrowwAPI(API_AUTH_TOKEN)

# Get today's 5-minute candles
historical_data = groww.get_historical_candle_data(
    trading_symbol="NIFTY",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-02-27 09:15:00",
    end_time="2025-02-27 15:30:00",
    interval_in_minutes=5
)

# Convert to pandas DataFrame for analysis
df = pd.DataFrame(
    historical_data['candles'],
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('datetime', inplace=True)

print(df.head())
print(f"\nTotal candles: {len(df)}")
print(f"Average volume: {df['volume'].mean()}")
```

### Example 3: Multi-timeframe Analysis
```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)

trading_symbol = "RELIANCE"
exchange = groww.EXCHANGE_NSE
segment = groww.SEGMENT_CASH

# Fetch different timeframes
timeframes = {
    "1min": 1,
    "5min": 5,
    "15min": 15,
    "1hour": 60,
    "1day": 1440
}

start_time = "2025-02-20 09:15:00"
end_time = "2025-02-27 15:30:00"

data = {}
for name, interval in timeframes.items():
    try:
        response = groww.get_historical_candle_data(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time,
            end_time=end_time,
            interval_in_minutes=interval
        )
        data[name] = response['candles']
        print(f"{name}: {len(response['candles'])} candles")
    except Exception as e:
        print(f"Error fetching {name}: {e}")
```

### Example 4: Calculate Technical Indicators
```python
from growwapi import GrowwAPI
import pandas as pd

groww = GrowwAPI(API_AUTH_TOKEN)

# Fetch historical data
historical_data = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-01-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440  # Daily
)

# Convert to DataFrame
df = pd.DataFrame(
    historical_data['candles'],
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)

# Calculate Simple Moving Averages
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['SMA_50'] = df['close'].rolling(window=50).mean()

# Calculate RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

print(df[['close', 'SMA_20', 'SMA_50', 'RSI']].tail())
```

### Example 5: Options Historical Data
```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)

# Fetch historical data for an option contract
option_data = groww.get_historical_candle_data(
    trading_symbol="NIFTY25N1823400CE",
    exchange=groww.EXCHANGE_NFO,
    segment=groww.SEGMENT_FNO,
    start_time="2025-02-20 09:15:00",
    end_time="2025-02-27 15:30:00",
    interval_in_minutes=15
)

print(f"Option candles: {len(option_data['candles'])}")

# Analyze option price movement
for candle in option_data['candles'][-5:]:  # Last 5 candles
    timestamp, open_p, high, low, close, volume = candle
    print(f"Time: {timestamp}, Close: {close}, Volume: {volume}")
```

## Important Limitations

### 1. Duration Limits
Each interval has a maximum duration per request:
- **1 min**: Max 7 days per request
- **5 min**: Max 15 days per request
- **10 min**: Max 30 days per request
- **1 hour**: Max 150 days per request
- **4 hours**: Max 365 days per request
- **1 day**: Max 1080 days (~3 years) per request
- **1 week**: No limit

### 2. Historical Data Availability
- **Intraday intervals** (1min to 4hours): Last 3 months only
- **Daily and weekly**: Full historical data available

### 3. Fetching Data Beyond Limits
For data beyond the max duration, make multiple requests:

```python
from datetime import datetime, timedelta

def fetch_extended_historical_data(groww, trading_symbol, exchange, segment, 
                                   start_date, end_date, interval_minutes):
    """Fetch historical data beyond single request limits"""
    
    # Determine max days per request based on interval
    max_days_map = {
        1: 7,
        5: 15,
        10: 30,
        60: 150,
        240: 365,
        1440: 1080
    }
    max_days = max_days_map.get(interval_minutes, 7)
    
    all_candles = []
    current_start = start_date
    
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=max_days), end_date)
        
        response = groww.get_historical_candle_data(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=current_start.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=current_end.strftime("%Y-%m-%d %H:%M:%S"),
            interval_in_minutes=interval_minutes
        )
        
        all_candles.extend(response['candles'])
        current_start = current_end + timedelta(seconds=1)
    
    return all_candles

# Usage
start = datetime(2024, 1, 1)
end = datetime(2025, 2, 27)

candles = fetch_extended_historical_data(
    groww=groww,
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_date=start,
    end_date=end,
    interval_minutes=1440  # Daily
)

print(f"Total candles fetched: {len(candles)}")
```

## Time Format Conversion

### Convert Epoch to Datetime
```python
from datetime import datetime

# Candle timestamp is in epoch seconds
timestamp = 1633072800
dt = datetime.fromtimestamp(timestamp)
print(dt.strftime("%Y-%m-%d %H:%M:%S"))
```

### Convert Datetime to Epoch
```python
from datetime import datetime
import time

dt = datetime(2025, 2, 27, 10, 0, 0)
epoch_seconds = int(dt.timestamp())
epoch_millis = int(dt.timestamp() * 1000)

print(f"Epoch seconds: {epoch_seconds}")
print(f"Epoch milliseconds: {epoch_millis}")
```

## Data Processing with Pandas

### Convert to DataFrame
```python
import pandas as pd

# Fetch data
response = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-02-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440
)

# Create DataFrame
df = pd.DataFrame(
    response['candles'],
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('datetime', inplace=True)

# Now you can use pandas for analysis
print(df.describe())
print(df.tail())
```

### Resample Data
```python
# Convert 5-minute candles to 15-minute candles
df_5min = pd.DataFrame(
    response['candles'],
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)
df_5min['datetime'] = pd.to_datetime(df_5min['timestamp'], unit='s')
df_5min.set_index('datetime', inplace=True)

# Resample to 15 minutes
df_15min = df_5min.resample('15T').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

print(df_15min.head())
```

## Use Cases

### 1. Backtesting Trading Strategy
```python
import pandas as pd

# Fetch historical data
response = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2024-01-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440
)

df = pd.DataFrame(response['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Simple moving average crossover strategy
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['SMA_50'] = df['close'].rolling(window=50).mean()

# Generate signals
df['signal'] = 0
df.loc[df['SMA_20'] > df['SMA_50'], 'signal'] = 1  # Buy signal
df.loc[df['SMA_20'] < df['SMA_50'], 'signal'] = -1  # Sell signal

# Calculate returns
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['signal'].shift(1) * df['returns']

print(f"Total return: {df['strategy_returns'].sum() * 100:.2f}%")
```

### 2. Volatility Analysis
```python
import pandas as pd
import numpy as np

response = groww.get_historical_candle_data(
    trading_symbol="NIFTY",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-01-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440
)

df = pd.DataFrame(response['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Calculate daily returns
df['returns'] = df['close'].pct_change()

# Calculate volatility (standard deviation of returns)
volatility = df['returns'].std() * np.sqrt(252)  # Annualized
print(f"Annualized Volatility: {volatility * 100:.2f}%")

# Calculate ATR (Average True Range)
df['high_low'] = df['high'] - df['low']
df['high_close'] = abs(df['high'] - df['close'].shift())
df['low_close'] = abs(df['low'] - df['close'].shift())
df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
df['ATR'] = df['true_range'].rolling(window=14).mean()

print(f"Current ATR: {df['ATR'].iloc[-1]:.2f}")
```

### 3. Support and Resistance Levels
```python
import pandas as pd

response = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-02-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440
)

df = pd.DataFrame(response['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Find support and resistance levels
resistance = df['high'].rolling(window=20).max()
support = df['low'].rolling(window=20).min()

print(f"Current Resistance: {resistance.iloc[-1]:.2f}")
print(f"Current Support: {support.iloc[-1]:.2f}")
```

### 4. Volume Analysis
```python
import pandas as pd

response = groww.get_historical_candle_data(
    trading_symbol="RELIANCE",
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    start_time="2025-02-01 00:00:00",
    end_time="2025-02-27 23:59:59",
    interval_in_minutes=1440
)

df = pd.DataFrame(response['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Calculate average volume
avg_volume = df['volume'].mean()
df['volume_ratio'] = df['volume'] / avg_volume

# Identify high volume days
high_volume_days = df[df['volume_ratio'] > 1.5]
print(f"High volume days: {len(high_volume_days)}")

# Volume-weighted average price
df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
print(f"Current VWAP: {df['vwap'].iloc[-1]:.2f}")
```

## Best Practices

1. **Choose Appropriate Interval**: 
   - Use 1-5 min for intraday strategies
   - Use 1 hour for swing trading
   - Use daily for long-term analysis

2. **Respect Duration Limits**: 
   - Don't request more data than the max duration per interval
   - Split large requests into multiple smaller ones

3. **Handle Missing Data**: 
   - Market holidays and non-trading hours won't have candles
   - Check for gaps in timestamp sequence

4. **Cache Historical Data**: 
   - Historical data doesn't change, so cache it locally
   - Only fetch new data incrementally

5. **Time Zone Awareness**: 
   - Timestamps are in IST (Indian Standard Time)
   - Convert to your local timezone if needed

6. **Data Validation**: 
   - Check for anomalies in OHLC data (e.g., high < low)
   - Validate volume is non-negative

7. **Memory Management**: 
   - Large datasets can consume significant memory
   - Process data in chunks if needed

## Common Intervals

| Interval | Minutes | Use Case |
|----------|---------|----------|
| 1 minute | 1 | Scalping, high-frequency trading |
| 5 minutes | 5 | Intraday trading |
| 15 minutes | 15 | Intraday trading |
| 30 minutes | 30 | Intraday/swing trading |
| 1 hour | 60 | Swing trading |
| 4 hours | 240 | Swing trading |
| 1 day | 1440 | Position trading, long-term analysis |
| 1 week | 10080 | Long-term trends |

## Error Handling

```python
from growwapi import GrowwAPI

groww = GrowwAPI(API_AUTH_TOKEN)

try:
    historical_data = groww.get_historical_candle_data(
        trading_symbol="RELIANCE",
        exchange=groww.EXCHANGE_NSE,
        segment=groww.SEGMENT_CASH,
        start_time="2025-02-20 09:15:00",
        end_time="2025-02-27 15:30:00",
        interval_in_minutes=5
    )
    
    if not historical_data.get('candles'):
        print("No candles returned")
    else:
        print(f"Fetched {len(historical_data['candles'])} candles")
        
except Exception as e:
    print(f"Error fetching historical data: {e}")
```

## Key Points

1. **Two Time Formats**: Supports both epoch milliseconds and "YYYY-MM-DD HH:mm:ss" string format

2. **Candle Array Structure**: Each candle is [timestamp, open, high, low, close, volume]

3. **Interval Flexibility**: Supports multiple intervals from 1 minute to 1 week

4. **Duration Constraints**: Each interval has maximum duration per request

5. **Historical Availability**: Intraday data limited to 3 months, daily data has full history

6. **Timestamp Format**: Response timestamps are in epoch seconds (not milliseconds)

7. **Market Hours Only**: Candles only exist for trading hours (no data for holidays/weekends)

8. **Segment Specific**: Must specify correct segment (CASH for equities, FNO for derivatives)

9. **No Gaps Handling**: API returns only available candles; handle gaps in your code

10. **Rate Limits**: Be mindful of API rate limits when fetching large amounts of data
