import yfinance as yf
import numpy as np

# Define the stock symbol and parameters for moving averages
symbol = "AAPL"
short_window = 50
long_window = 200

# Fetch historical data
data = yf.download(symbol, period="1y")

# Calculate moving averages
data["short_mavg"] = data["Close"].rolling(window=short_window, min_periods=1).mean()
data["long_mavg"] = data["Close"].rolling(window=long_window, min_periods=1).mean()

# Initialize variables
position = 0  # 0: out of market, 1: long position
capital = 100000  # Initial capital
shares = 0  # Number of shares held
commission = 0.005  # Commission fee per trade

# Iterate over the data, starting from the long_window index
for i in range(long_window, len(data)):
    # Generate buy signal
    if data["short_mavg"][i] > data["long_mavg"][i] and position == 0:
        shares_to_buy = capital / data["Close"][i]
        shares = shares_to_buy
        capital -= shares_to_buy * data["Close"][i]
        position = 1
        print(f"Buy {symbol} at {data['Close'][i]}")

    # Generate sell signal
    elif data["short_mavg"][i] < data["long_mavg"][i] and position == 1:
        capital += shares * data["Close"][i] * (1 - commission)
        shares = 0
        position = 0
        print(f"Sell {symbol} at {data['Close'][i]}")

# Calculate final portfolio value
portfolio_value = capital + shares * data["Close"][-1]
print(f"Final portfolio value: {portfolio_value}")
