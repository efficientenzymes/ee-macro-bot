import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

def fetch_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty or "Close" not in data:
            raise ValueError(f"No price data found for {ticker}")
        return data["Close"]
    except Exception as e:
        print(f"[ERROR] Failed to fetch {ticker}: {e}")
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
        print(f"[WARNING] No chart generated for {ticker} (empty data)")
        return None

    daily, weekly, monthly = calculate_change(series)
    name = name or ticker

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

    filepath = f"charts/{ticker.replace('=', '').replace('^', '')}.png"
    os.makedirs("charts", exist_ok=True)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    return filepath

def generate_all_charts():
    assets = {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^RUT": "Russell 2000",
        "^VIX": "VIX",
        "TLT": "20Y Bonds",
        "GC=F": "Gold",
        "CL=F": "Crude Oil",
        "BTC-USD": "Bitcoin",
        "^MOVE": "MOVE Index",
        "^TNX": "10Y Yield"
    }

    chart_paths = []
    for ticker, name in assets.items():
        print(f"[DEBUG] Generating chart for: {ticker} ({name})")
        path = generate_chart(ticker, name)
        if path:
            chart_paths.append(path)
        else:
            print(f"[SKIPPED] No chart for {ticker}")
    return chart_paths
