import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

def fetch_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        return data['Close']
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
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
        return None

    daily, weekly, monthly = calculate_change(series)
    name = name or ticker

    plt.figure(figsize=(10, 4))
    plt.plot(series.index, series.values)
    plt.title(f"{name} ({ticker})")
    plt.xlabel("Date")
    plt.ylabel("Price")

    label = f"Day: {daily:.2f}%\nWeek: {weekly:.2f}%\nMonth: {monthly:.2f}%" if daily is not None else "N/A"
    plt.annotate(label, xy=(0.99, 0.01), xycoords='axes fraction',
                 ha='right', va='bottom', fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgrey", alpha=0.5))

    filepath = f"charts/{ticker}.png"
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
        "DXY": "Dollar Index",
        "GC=F": "Gold",
        "CL=F": "Crude Oil",
        "BTC-USD": "Bitcoin",
        "^VVIX": "VVIX",
        "^MOVE": "MOVE Index",
        "^TNX": "10Y Yield",
        "^IRX": "3M Yield",
        "^FVX": "5Y Yield",
        "^TYX": "30Y Yield",
        "^PUTCALL": "Put/Call Ratio"
    }

    chart_paths = []
    for ticker, name in assets.items():
        path = generate_chart(ticker, name)
        if path:
            chart_paths.append(path)
    return chart_paths

def generate_weekly_charts():
    tickers = {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^RUT": "Russell 2000",
        "DXY": "Dollar Index",
        "TLT": "20Y Bonds",
        "^PCALL": "Put/Call Ratio"
    }
    
    chart_paths = []
    for ticker, name in tickers.items():
        series = fetch_data(ticker, period='3mo', interval='1d')
        if series.empty:
            continue

        plt.figure(figsize=(10, 4))
        plt.plot(series.index, series.values)
        plt.title(f"{name} Weekly View ({ticker})")
        plt.xlabel("Date")
        plt.ylabel("Price")
        filepath = f"charts/weekly_{ticker}.png"
        os.makedirs("charts", exist_ok=True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        chart_paths.append(filepath)
    return chart_paths
