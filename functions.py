import json
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import pearsonr
from binance.client import Client

# Binance API credentials (update with your own credentials)
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
client = Client(API_KEY, API_SECRET)

# JSON file path
DATA_FILE = "static/data.json"

# Save data to JSON
def save_data_to_json(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Load data from JSON
def load_data_from_json():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

# Update download_data to create a symbol map
def download_data(days, interval):
    tickers = client.get_ticker()
    symbols = [t["symbol"] for t in tickers if t["symbol"].endswith("USDT")]

    # Symbol map to store short names (e.g., BTC -> BTCUSDT)
    symbol_map = {}

    data = {}
    for symbol in symbols:
        try:
            klines = client.get_historical_klines(symbol, interval, f"{days} days ago UTC")
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            data[symbol] = df["close"].tolist()

            # Add short symbol to map (e.g., BTC -> BTCUSDT)
            short_symbol = symbol.replace("USDT", "")
            symbol_map[short_symbol] = symbol
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Save data and symbol map
    save_data_to_json({"data": data, "symbol_map": symbol_map})


# Find top correlated coins
def find_top_correlated(base_coin):
    data_bundle = load_data_from_json()
    if data_bundle is None:
        raise ValueError("No data available. Please download data first.")

    data = data_bundle["data"]
    symbol_map = data_bundle["symbol_map"]

    # Normalize input to Binance symbol
    base_coin = symbol_map.get(base_coin.upper(), base_coin)

    if base_coin not in data:
        raise ValueError(f"Coin {base_coin} not found in data.")

    base_prices = np.array(data[base_coin])
    correlations = []

    for coin, prices in data.items():
        if coin == base_coin or len(prices) != len(base_prices):
            continue
        corr, _ = pearsonr(base_prices, np.array(prices))
        correlations.append((coin, corr))

    correlations.sort(key=lambda x: x[1], reverse=True)
    return correlations[:10]



# Create correlation chart
def create_correlation_chart(coin1, coin2):
    data_bundle = load_data_from_json()
    if data_bundle is None:
        raise ValueError("No data available. Please download data first.")

    data = data_bundle["data"]
    symbol_map = data_bundle["symbol_map"]

    # Normalize coins to Binance symbol format
    coin1 = symbol_map.get(coin1.upper(), coin1)
    coin2 = symbol_map.get(coin2.upper(), coin2)

    if coin1 not in data or coin2 not in data:
        raise ValueError(f"One or both coins ({coin1}, {coin2}) not found in data.")

    prices1 = data[coin1]
    prices2 = data[coin2]

    if len(prices1) != len(prices2):
        raise ValueError("The selected coins have different data lengths.")

    plt.figure(figsize=(10, 6))
    plt.scatter(prices1, prices2, alpha=0.7)
    plt.title(f"Correlation between {coin1} and {coin2}")
    plt.xlabel(f"{coin1} Prices")
    plt.ylabel(f"{coin2} Prices")
    plt.grid(True)
    output_path = "static/output.png"
    plt.savefig(output_path)
    plt.close()
    return output_path
