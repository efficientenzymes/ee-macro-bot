import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

# Output folder
output_dir = "charts"
os.makedirs(output_dir, exist_ok=True)

chart_pairs = [
    ("BTC-USD", "^VIX", "btc_vs_vix.png"),
    ("GLD", "SLV", "gold_vs_silver.png"),
    ("SPY", "DXY", "spx_vs_dxy.png"),
    ("USO", "QQQ", "oil_vs_nasdaq.png"),
    ("QQQ", "IWM", "qqq_vs_iwm.png"),
    ("TLT", "SPY", "tlt_vs_spy.png"),
    ("HYG", "LQD", "hyg_vs_lqd.png"),
    ("XLE", "XLF", "xle_vs_xlf.png"),
    ("BTC-USD", "GLD", "btc_vs_gold.png"),
]

def detect_breakout(series):
    rolling_max = series.rolling(window=100).max()
    return series > rolling_max.shift(1)

def generate_ratio_chart(asset1, asset2, filename):
    df1 = yf.download(asset1, period="5y", auto_adjust=False)
    df2 = yf.download(asset2, period="5y", auto_adjust=False)

    data1 = df1["Adj Close"] if "Adj Close" in df1.columns else df1
    data2 = df2["Adj Close"] if "Adj Close" in df2.columns else df2

    combined = pd.concat([data1, data2], axis=1, join="inner")
    combined.columns = [asset1, asset2]
    combined["Ratio"] = combined[asset1] / combined[asset2]

    breakout_mask = detect_breakout(combined["Ratio"])

    plt.figure(figsize=(12, 6))
    plt.plot(combined.index, combined["Ratio"], label="Ratio", color="blue")
    plt.scatter(combined.index[breakout_mask], combined["Ratio"][breakout_mask],
                color="red", label="Breakout", s=20)
    plt.yscale("log")
    plt.title(f"{asset1} / {asset2} (Log Scale) with Breakouts")
    plt.grid(True)
    plt.legend()

    # Watermark
    plt.text(0.99, 0.01, "EE MacroBot", fontsize=9, color="gray",
             ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.6)

    plt.tight_layout()
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath

def generate_all_charts():
    chart_files = []
    for asset1, asset2, filename in chart_pairs:
        try:
            path = generate_ratio_chart(asset1, asset2, filename)
            chart_files.append(path)
        except Exception as e:
            print(f"❌ Error generating chart {filename}: {e}")
    return chart_files
