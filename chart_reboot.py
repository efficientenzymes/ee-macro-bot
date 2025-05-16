import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import os
import logging

plt.style.use("dark_background")  # Dark mode theme

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

def calculate_change(series):
    if len(series) < 2:
        return None, None, None
    daily = (series.iloc[-1] - series.iloc[-2]) / series.iloc[-2] * 100
    weekly = (series.iloc[-1] - series.iloc[-6]) / series.iloc[-6] * 100 if len(series) >= 6 else None
    monthly = (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100
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
        plt.plot(series.index, series.values, linewidth=2.0)
        plt.title(f"{name} ({ticker})", fontsize=12)
        plt.xlabel("Date")
        plt.ylabel("Price")

        label = None
        try:
            daily_val = float(daily) if daily is not None else 'n/a'
            weekly_val = float(weekly) if weekly is not None else 'n/a'
            monthly_val = float(monthly) if monthly is not None else 'n/a'
            label = (
                f"Day: {daily_val if isinstance(daily_val, str) else f'{daily_val:.2f}'}%\n"
                f"Week: {weekly_val if isinstance(weekly_val, str) else f'{weekly_val:.2f}'}%\n"
                f"Month: {monthly_val if isinstance(monthly_val, str) else f'{monthly_val:.2f}'}%"
            )
        except Exception as e:
            logger.warning(f"[WARNING] Skipping annotation for {ticker} due to: {repr(e)}")

        if label:
            plt.annotate(label, xy=(0.99, 0.01), xycoords='axes fraction',
                         ha='right', va='bottom', fontsize=9,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="gray", alpha=0.4))

        # ✅ Add subtle watermark
        plt.annotate("@EEMacroBot", xy=(0.01, 0.01), xycoords='axes fraction',
                     ha='left', va='bottom', fontsize=8, alpha=0.3, color="white")

        filepath = f"charts/{ticker.replace('^', '').replace('=', '')}.png"
        logger.info(f"[DEBUG] Saving chart to: {filepath}")
        os.makedirs("charts", exist_ok=True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        logger.info(f"[DEBUG] Saved chart for {ticker}")
        return filepath

    except Exception as e:
        logger.error(f"[ERROR] Chart failed for {ticker}: {repr(e)}")
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
            logger.error(f"[ERROR] Chart failed for {ticker}: {repr(e)}")

    logger.info(f"[DEBUG] Finished generating {len(chart_paths)} chart(s)")
    return chart_paths
