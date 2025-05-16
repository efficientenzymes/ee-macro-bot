import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

# Output folders
daily_dir = "charts"
weekly_dir = "charts_weekly"
os.makedirs(daily_dir, exist_ok=True)
os.makedirs(weekly_dir, exist_ok=True)

chart_pairs = [
    ("BTC-USD", "^VIX", "btc_vs_vix.png", "Tracks risk appetite: BTC outperforming VIX = risk-on"),
    ("GLD", "SLV", "gold_vs_silver.png", "Gold/Silver strength shows flight to safety or inflation hedging"),
    ("^GSPC", "DX-Y.NYB", "spx_vs_dxy.png", "Strong SPX/DXY = equities outperform USD; weak = risk-off"),
    ("USO", "QQQ", "oil_vs_nasdaq.png", "Commodities vs Tech: rotation into hard assets or out of growth"),
    ("QQQ", "IWM", "qqq_vs_iwm.png", "Growth vs small caps — a shift in leadership"),
    ("TLT", "SPY", "tlt_vs_spy.png", "Bond vs equity regime shift (risk-off if rising)"),
    ("HYG", "LQD", "hyg_vs_lqd.png", "Junk vs quality credit — shows credit market risk appetite"),
    ("XLE", "XLF", "xle_vs_xlf.png", "Energy vs Financials — inflation and rate narratives"),
    ("BTC-USD", "GLD", "btc_vs_gold.png", "Digital vs traditional store of value — macro hedge rotation"),
]

def compute_change_stats(series):
    changes = {}
    if len(series) >= 2:
        changes["1d"] = (series.iloc[-1] / series.iloc[-2] - 1) * 100
    if len(series) >= 6:
        changes["1w"] = (series.iloc[-1] / series.iloc[-6] - 1) * 100
    if len(series) >= 22:
        changes["1m"] = (series.iloc[-1] / series.iloc[-22] - 1) * 100
    return changes

def detect_breakout(series):
    rolling_max = series.rolling(window=100).max()
    return series > rolling_max.shift(1)

def generate_ratio_chart(asset1, asset2, filename, explanation):
    df1 = yf.download(asset1, period="6mo", auto_adjust=False)
    df2 = yf.download(asset2, period="6mo", auto_adjust=False)
    data1 = df1["Adj Close"]
    data2 = df2["Adj Close"]
    combined = pd.concat([data1, data2], axis=1, join="inner")
    combined.columns = [asset1, asset2]
    combined["Ratio"] = combined[asset1] / combined[asset2]

    changes = compute_change_stats(combined["Ratio"])
    breakout_mask = detect_breakout(combined["Ratio"])

    plt.figure(figsize=(12, 6))
    plt.plot(combined.index, combined["Ratio"], label="Ratio", color="blue")
    plt.scatter(combined.index[breakout_mask], combined["Ratio"][breakout_mask], color="red", label="Breakout", s=20)
    plt.yscale("log")
    plt.title(f"{asset1} / {asset2} (Log Scale)")
    plt.grid(True)
    plt.legend()
    plt.text(0.99, 0.01, "EE MacroBot", fontsize=9, color="gray", ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.6)
    plt.tight_layout()

    filepath = os.path.join(daily_dir, filename)
    plt.savefig(filepath)
    plt.close()

    caption = (
        f"📊 **{asset1} / {asset2}**\n"
        f"> **1D:** {changes.get('1d', 0):+.2f}% | "
        f"**1W:** {changes.get('1w', 0):+.2f}% | "
        f"**1M:** {changes.get('1m', 0):+.2f}%\n"
        f"> _{explanation}_"
    )

    signal = None
    if breakout_mask.iloc[-1]:
        signal = f"{asset1}/{asset2} breakout 🔺"
    elif abs(changes.get("1d", 0)) > 1.5:
        trend = "up" if changes["1d"] > 0 else "down"
        signal = f"{asset1}/{asset2} moving {trend} {changes['1d']:+.2f}%"

    return filepath, caption, signal

def generate_put_call_chart():
    data = yf.download("^CPCE", period="6mo", auto_adjust=False)["Adj Close"]
    changes = compute_change_stats(data)

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data, color="purple", label="Put/Call Ratio (^CPCE)")
    plt.axhline(0.75, color="red", linestyle="--", label="Fear Zone")
    plt.axhline(0.45, color="green", linestyle="--", label="Greed Zone")
    plt.title("CBOE Equity Put/Call Ratio (Daily)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    file_path = os.path.join(daily_dir, "put_call_ratio.png")
    plt.savefig(file_path)
    plt.close()

    sentiment = "fear" if data.iloc[-1] > 0.75 else "greed" if data.iloc[-1] < 0.45 else "neutral sentiment"
    caption = (
        f"📊 **Put/Call Ratio (^CPCE)**\n"
        f"> **1D:** {changes.get('1d', 0):+.2f}% | "
        f"**1W:** {changes.get('1w', 0):+.2f}% | "
        f"**1M:** {changes.get('1m', 0):+.2f}%\n"
        f"> _Retail options activity shows {sentiment}_"
    )

    return file_path, caption, f"Put/Call ratio suggesting {sentiment}"

def generate_all_charts():
    chart_files = []
    signal_lines = []

    for asset1, asset2, filename, explanation in chart_pairs:
        try:
            path, caption, signal = generate_ratio_chart(asset1, asset2, filename, explanation)
            chart_files.append((path, caption))
            if signal:
                signal_lines.append(f"• {signal}")
        except Exception as e:
            print(f"❌ Error generating chart {filename}: {e}")

    # Add Put/Call chart
    try:
        pc_path, pc_caption, pc_signal = generate_put_call_chart()
        chart_files.append((pc_path, pc_caption))
        if pc_signal:
            signal_lines.append(f"• {pc_signal}")
    except Exception as e:
        print(f"❌ Error generating Put/Call chart: {e}")

    summary = "\n📌 **Macro Watchlist Summary**\n" + "\n".join(signal_lines) if signal_lines else ""
    return chart_files, summary
