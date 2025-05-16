import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging

logger = logging.getLogger("macro-bot")

def fetch_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty or "Close" not in data:
            raise ValueError(f"No price data for {ticker}")
        return data["Close"]
    except Exception as e:
        logger.error(f"[ERROR] fetch_data failed for {ticker}: {e}")
        return pd.Series()

def calculate_change(series):
    if len(series) < 2:
        return None, None, None
    daily = (series[-1] - series[-2]) / series[-2] * 100
    weekly = (series[-1] - series[-6]) / series[-6] * 100 if len(series) >= 6 else None
    monthly = (series[-1] - series[0]) / series[0] * 100
    return daily, weekly, monthly

def generate_chart(ticker, name=None):
    series = fetch_data(ticker)
    if series.empty:
        logger.warning(f"[WARNING] No chart for {ticker} — empty data")
        return None

    daily, weekly, monthly = calculate_change(series)
    name = name or ticker

    try:
        logger.info(f"[DEBUG] Plotting chart for {ticker}")
        plt.figure(figsize=(10, 4))
        plt.plot(series.index, series.values)
        plt.title(f"{name} ({ticker})")
        plt.xlabel("Date")
        plt.ylabel("Price")

        if daily is not None:
            label = f"Day: {daily:.2f}%\nWeek: {weekly:.2f}%\nMonth: {monthly:.2f}%"
            plt.annotate(label, xy=(0.99, 0.01), xycoords='axes fraction',
                         ha='right', va='bottom', fontsize=10,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgrey", alpha=0.5))

        filepath = f"charts/{ticker.replace('^', '').replace('=', '')}.png"
        logger.info(f"[DEBUG] Saving chart to: {filepath}")
        os.makedirs("charts", exist_ok=True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        logger.info(f"[DEBUG] Saved chart for {ticker}")
        return filepath

    except Exception as e:
        logger.error(f"[ERROR] Chart failed for {ticker}: {e}")
        return None

def generate_all_charts():
    assets = {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^RUT": "Russell 2000",
        "^VIX": "VIX",
        "TLT": "20Y Bonds",
        "DXY": "Dollar Index",
        "GC=F": "Gold",
        "CL=F": "Crude Oil",
        "BTC-USD": "Bitcoin",
        "^MOVE": "MOVE Index",
        "^TNX": "10Y Yield",
        "^IRX": "3M Yield",
        "^FVX": "5Y Yield",
        "^TYX": "30Y Yield"
    }

    chart_paths = []

    for ticker, name in assets.items():
        logger.info(f"[DEBUG] Attempting chart for {ticker} ({name})")
        try:
            path = generate_chart(ticker, name)
            if path:
                chart_paths.append(path)
            else:
                logger.warning(f"[WARNING] Chart not generated for {ticker}")
        except Exception as e:
            logger.error(f"[ERROR] Chart failed for {ticker}: {e}")

    logger.info(f"[DEBUG] Finished generating {len(chart_paths)} chart(s)")
    return chart_paths
