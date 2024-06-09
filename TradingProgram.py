import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import ta
import logging
from datetime import datetime, timedelta
import time

# Alpaca API credentials
API_KEY = 'YOUR_ALPACA_API_KEY'
API_SECRET = 'YOUR_ALPACA_API_SECRET'
BASE_URL = 'https://paper-api.alpaca.markets'  # For paper trading

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Configure logging
logging.basicConfig(filename='trading_log.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Function to get historical price data
def get_price_history(symbol, start, end, timeframe='day'):
    try:
        barset = api.get_barset(symbol, timeframe, start=start, end=end)
        bars = barset[symbol]
        data = pd.DataFrame([{
            'time': bar.t,
            'open': bar.o,
            'high': bar.h,
            'low': bar.l,
            'close': bar.c,
            'volume': bar.v
        } for bar in bars])
        return data
    except Exception as e:
        logging.error(f'Error fetching price history: {e}')
        return pd.DataFrame()

# Function to place an order
def place_order(symbol, qty, side, order_type='market', time_in_force='gtc'):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force
        )
        logging.info(f'Order placed: {order}')
    except Exception as e:
        logging.error(f'Error placing order: {e}')

# Moving Average Crossover Strategy
def moving_average_crossover(symbol, short_window=50, long_window=200):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    data = get_price_history(symbol, start_date.isoformat(), end_date.isoformat())

    if data.empty:
        logging.error(f'No data fetched for {symbol}. Exiting.')
        return

    # Calculate moving averages
    data['short_mavg'] = data['close'].rolling(window=short_window).mean()
    data['long_mavg'] = data['close'].rolling(window=long_window).mean()
    data.dropna(inplace=True)

    # Generate trading signals
    data['signal'] = 0
    data['signal'][short_window:] = np.where(data['short_mavg'][short_window:] > data['long_mavg'][short_window:], 1, 0)
    data['positions'] = data['signal'].diff()

    # Execute trades based on the signals
    for i in range(len(data)):
        if data['positions'].iloc[i] == 1:
            logging.info(f'Buy signal for {symbol} at {data["close"].iloc[i]} on {data["time"].iloc[i]}')
            place_order(symbol, 10, 'buy')  # Example: buy 10 shares
        elif data['positions'].iloc[i] == -1:
            logging.info(f'Sell signal for {symbol} at {data["close"].iloc[i]} on {data["time"].iloc[i]}')
            place_order(symbol, 10, 'sell')  # Example: sell 10 shares

# Backtesting Function
def backtest_strategy(symbol, short_window=50, long_window=200):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 5)  # 5 years of historical data
    data = get_price_history(symbol, start_date.isoformat(), end_date.isoformat())

    if data.empty:
        logging.error(f'No data fetched for {symbol}. Exiting.')
        return

    # Calculate moving averages
    data['short_mavg'] = data['close'].rolling(window=short_window).mean()
    data['long_mavg'] = data['close'].rolling(window=long_window).mean()
    data.dropna(inplace=True)

    # Generate trading signals
    data['signal'] = 0
    data['signal'][short_window:] = np.where(data['short_mavg'][short_window:] > data['long_mavg'][short_window:], 1, 0)
    data['positions'] = data['signal'].diff()

    # Backtesting results
    initial_capital = 100000.0
    positions = pd.DataFrame(index=data.index).fillna(0.0)
    positions[symbol] = 10 * data['signal']
    portfolio = positions.multiply(data['close'], axis=0)
    pos_diff = positions.diff()
    portfolio['holdings'] = (positions.multiply(data['close'], axis=0)).sum(axis=1)
    portfolio['cash'] = initial_capital - (pos_diff.multiply(data['close'], axis=0)).sum(axis=1).cumsum()
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()

    logging.info(f"Backtesting results for {symbol}:")
    logging.info(f"Total Returns: {portfolio['total'][-1] - initial_capital}")
    logging.info(f"Average Daily Return: {portfolio['returns'].mean()}")
    logging.info(f"Annualized Sharpe Ratio: {np.sqrt(252) * (portfolio['returns'].mean() / portfolio['returns'].std())}")

# Run the strategy and backtest
symbols = ['AAPL', 'MSFT', 'GOOGL']
for symbol in symbols:
    moving_average_crossover(symbol)
    backtest_strategy(symbol)

