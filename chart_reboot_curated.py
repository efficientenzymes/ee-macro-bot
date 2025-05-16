
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

def calculate_trends(series):
    if len(series) < 2:
        return None, None, None
    try:
        daily = (series.iloc[-1] - series.iloc[-2]) / series.iloc[-2] * 100
        weekly = (series.iloc[-1] - series.iloc[-6]) / series.iloc[-6] * 100 if len(series) >= 6 else None
        monthly = (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100
        return daily, weekly, monthly
    except Exception as e:
        logger.error(f"[ERROR] calculate_trends failed: {repr(e)}")
        return None, None, None

def generate_chart(spread_name, series, daily, weekly, monthly, blurb, yscale="log"):
    try:
        logger.info(f"[DEBUG] Plotting chart for {spread_name}")
        plt.figure(figsize=(10, 4))
        plt.plot(series.index, series.values, linewidth=2.0)
        plt.title(f"{spread_name}", fontsize=12)
        plt.xlabel("Date")
        plt.ylabel("Ratio")
        if yscale == "log":
            plt.yscale("log")

        label = (
            f"1D: {daily:.2f}% | 1W: {weekly:.2f}% | 1M: {monthly:.2f}%\n{blurb}"
            if all(x is not None for x in [daily, weekly, monthly])
            else blurb
        )
        plt.annotate(label, xy=(0.01, 0.01), xycoords='axes fraction',
                     ha='left', va='bottom', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="gray", alpha=0.4))

        # Watermark
        plt.annotate("@EEMacroBot", xy=(0.99, 0.01), xycoords='axes fraction',
                     ha='right', va='bottom', fontsize=8, alpha=0.3, color="white")

        filepath = f"charts/{spread_name.replace('/', '_').replace(' ', '')}.png"
        os.makedirs("charts", exist_ok=True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        logger.info(f"[DEBUG] Saved chart: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"[ERROR] Chart failed for {spread_name}: {repr(e)}")
        return None

def generate_all_charts():
    spreads = {
        "BTC / VIX": ("BTC-USD", "^VIX", "Tracks risk appetite: BTC outperforming VIX = risk-on"),
        "GLD / SLV": ("GLD", "SLV", "Gold/Silver strength shows flight to safety or inflation hedging"),
        "SPX / DXY": ("^GSPC", "DX-Y.NYB", "Strong SPX/DXY = equities outperform USD; weak = risk-off"),
        "USO / QQQ": ("USO", "QQQ", "Commodities vs Tech: rotation into hard assets or out of growth"),
        "QQQ / IWM": ("QQQ", "IWM", "Growth vs small caps — a shift in leadership"),
        "TLT / SPY": ("TLT", "SPY", "Bond vs equity regime shift (risk-off if rising)"),
        "HYG / LQD": ("HYG", "LQD", "Junk vs quality credit — shows credit market risk appetite"),
        "XLE / XLF": ("XLE", "XLF", "Energy vs Financials — inflation and rate narratives"),
        "BTC / GLD": ("BTC-USD", "GLD", "Digital vs traditional store of value — macro hedge rotation")
    }

    chart_paths = []

    for name, (numerator, denominator, blurb) in spreads.items():
        logger.info(f"[DEBUG] Generating spread: {name}")
        num_series = fetch_data(numerator)
        denom_series = fetch_data(denominator)

        if num_series.empty or denom_series.empty:
            logger.warning(f"[WARNING] Empty data for {name}")
            continue

        ratio_series = pd.concat([num_series, denom_series], axis=1).dropna()
        if ratio_series.empty:
            logger.warning(f"[WARNING] Empty aligned ratio for {name}")
            continue

        ratio = ratio_series.iloc[:, 0] / ratio_series.iloc[:, 1]
        daily, weekly, monthly = calculate_trends(ratio)

        path = generate_chart(name, ratio, daily, weekly, monthly, blurb)
        if path:
            chart_paths.append(path)

    logger.info(f"[DEBUG] Finished generating {len(chart_paths)} curated charts")
    return chart_paths
