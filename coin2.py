from binance import Client
import pandas as pd
import numpy as np
import time
from datetime import date

def download_data(day, period):
    client = Client()
    info = client.get_exchange_info()
    sembol = [x['symbol'] for x in info['symbols']]
    sembol_usd = [symbol for symbol in sembol if symbol.endswith('USDT')]

    dfs = []
    for coin in sembol_usd:
        dfs.append(get_detailed_data(client, coin, day, period))

    mergedf = pd.concat(dict(zip(sembol_usd, dfs)), axis=1)
    closedf = mergedf.loc[:, mergedf.columns.get_level_values(1).isin(['Close'])]
    closedf.columns = closedf.columns.droplevel(1)
    logretdf = np.log(closedf.pct_change() + 1)
    logretdf.to_csv("logretdf.csv")

def get_detailed_data(client, symbol, day, period):
    msg = f"{day} ago UTC"
    frame = pd.DataFrame(client.get_historical_klines(symbol, period, msg))
    if len(frame) > 0:
        frame = frame.iloc[:, :5]
        frame.columns = ["Time", "Open", "High", "Low", "Close"]
        frame.index = pd.to_datetime(frame.index, unit="ms")
        frame = frame.astype(float)
        return frame
