
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import os
import logging

plt.style.use("dark_background")

logger = logging.getLogger("macro-bot")

def fetch_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty or "Close" not in data:
            raise ValueError(f"No price data for {ticker}")
        return data["Close"]
    except Exception as e:
        logger.error(f"[ERROR] fetch_data failed for {ticker}: {repr(e)}")
        return pd.Series()

def calculate_ratio(series1, series2):
    try:
        return (series1 / series2).dropna()
    except Exception as e:
        logger.error(f"[ERROR] Failed ratio calculation: {repr(e)}")
        return pd.Series()

def generate_chart(spread_name, series, yscale="log"):
    try:
        logger.info(f"[DEBUG] Plotting spread chart for {spread_name}")
        plt.figure(figsize=(10, 4))
        plt.plot(series.index, series.values, linewidth=2.0)
        plt.title(f"{spread_name}", fontsize=12)
        plt.xlabel("Date")
        plt.ylabel("Ratio")
        if yscale == "log":
            plt.yscale("log")

        plt.annotate("@EEMacroBot", xy=(0.01, 0.01), xycoords='axes fraction',
                     ha='left', va='bottom', fontsize=8, alpha=0.3, color="white")

        filepath = f"charts/{spread_name.replace('/', '_').replace(' ', '')}.png"
        logger.info(f"[DEBUG] Saving chart to: {filepath}")
        os.makedirs("charts", exist_ok=True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        logger.info(f"[DEBUG] Saved spread chart: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"[ERROR] Failed to plot spread {spread_name}: {repr(e)}")
        return None

def generate_all_charts():
    spreads = {
        "BTC / VIX": ("BTC-USD", "^VIX"),
        "SPX / TLT": ("^GSPC", "TLT"),
        "NDX / MOVE": ("^NDX", "^MOVE"),
        "Gold / VIX": ("GC=F", "^VIX"),
        "SPX / Gold": ("^GSPC", "GC=F"),
        "BTC / DXY": ("BTC-USD", "DXY")
    }

    chart_paths = []

    for name, (num, denom) in spreads.items():
        logger.info(f"[DEBUG] Generating spread: {name}")
        num_series = fetch_data(num)
        denom_series = fetch_data(denom)
        ratio_series = calculate_ratio(num_series, denom_series)

        if not ratio_series.empty:
            path = generate_chart(name, ratio_series)
            if path:
                chart_paths.append(path)
        else:
            logger.warning(f"[WARNING] Empty ratio series for {name}")

    logger.info(f"[DEBUG] Finished generating {len(chart_paths)} spread chart(s)")
    return chart_paths
