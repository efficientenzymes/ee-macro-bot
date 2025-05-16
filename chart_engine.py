import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

output_dir = "charts"
os.makedirs(output_dir, exist_ok=True)

chart_pairs = [
    ("BTC-USD", "^VIX", "btc_vs_vix.png", "Tracks risk appetite: BTC outperforming VIX = risk-on"),
    ("GLD", "SLV", "gold_vs_silver.png", "Gold/Silver strength shows flight to safety or inflation hedging"),
    ("^GSPC", "DXY", "spx_vs_dxy.png", "Strong SPX/DXY = equities outperform USD; weak = risk-off"),
    ("USO", "QQQ", "oil_vs_nasdaq.png", "Commodities vs Tech: rotation into hard assets or out of growth"),
    ("QQQ", "IWM", "qqq_vs_iwm.png", "Growth vs small caps — a shift in leadership"),
    ("TLT", "SPY", "tlt_vs_spy.png", "Bond vs equity regime shift (risk-off if rising)"),
    ("HYG", "LQD", "hyg_vs_lqd.png", "Junk vs quality credit — shows credit market risk appetite"),
    ("XLE", "XLF", "xle_vs_xlf.png", "Energy vs Financials — inflation and rate narratives"),
    ("BTC-USD", "GLD", "btc_vs_gold.png", "Digital vs traditional store of value — macro hedge rotation"),
]

def detect_breakout(series):
    rolling_max = series.rolling(window=100).max()
    return series > rolling_max.shift(1)

def compute_change_stats(series):
    changes = {}
    if len(series) >= 2:
        changes["1d"] = (series[-1] / series[-2] - 1) * 100
    if len(series) >= 6:
        changes["1w"] = (series[-1] / series[-6] - 1) * 100
    if len(series) >= 22:
        changes["1m"] = (series[-1] / series[-22] - 1) * 100
    return changes

def generate_ratio_chart(asset1, asset2, filename, explanation):
    df1 = yf.download(asset1, period="6mo", auto_adjust=False)
    df2 = yf.download(asset2, period="6mo", auto_adjust=False)

    data1 = df1["Adj Close"] if "Adj Close" in df1.columns else df1
    data2 = df2["Adj Close"] if "Adj Close" in df2.columns else df2

    combined = pd.concat([data1, data2], axis=1, join="inner")
    combined.columns = [asset1, asset2]
    combined["Ratio"] = combined[asset1] / combined[asset2]

    breakout_mask = detect_breakout(combined["Ratio"])
    changes = compute_change_stats(combined["Ratio"])

    # Plot chart
    plt.figure(figsize=(12, 6))
    plt.plot(combined.index, combined["Ratio"], label="Ratio", color="blue")
    plt.scatter(combined.index[breakout_mask], combined["Ratio"][breakout_mask],
                color="red", label="Breakout", s=20)
    plt.yscale("log")
    plt.title(f"{asset1} / {asset2} (Log Scale)")
    plt.grid(True)
    plt.legend()
    plt.text(0.99, 0.01, "EE MacroBot", fontsize=9, color="gray",
             ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.6)
    plt.tight_layout()

    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()

    # Caption for Discord
    caption = (
        f"📊 **{asset1} / {asset2}**\n"
        f"> **1D:** {changes.get('1d', 0):+.2f}% | "
        f"**1W:** {changes.get('1w', 0):+.2f}% | "
        f"**1M:** {changes.get('1m', 0):+.2f}%\n"
        f"> _{explanation}_"
    )
    return filepath, caption

def generate_all_charts():
    chart_files = []
    for asset1, asset2, filename, explanation in chart_pairs:
        try:
            path, caption = generate_ratio_chart(asset1, asset2, filename, explanation)
            chart_files.append((path, caption))
        except Exception as e:
            print(f"❌ Error generating chart {filename}: {e}")
    return chart_files
