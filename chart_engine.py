import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

# Output folder for charts
output_dir = "charts"
os.makedirs(output_dir, exist_ok=True)

# Define ratio chart pairs
chart_pairs = [
    ("BTC-USD", "^VIX", "btc_vs_vix.png"),
    ("GLD", "SLV", "gold_vs_silver.png"),
    ("SPY", "DXY", "spx_vs_dxy.png"),
    ("USO", "QQQ", "oil_vs_nasdaq.png"),
]

def generate_ratio_chart(asset1, asset2, filename):
    df1 = yf.download(asset1, period="5y", auto_adjust=False)
    df2 = yf.download(asset2, period="5y", auto_adjust=False)

    # Extract adjusted close safely
    if "Adj Close" in df1.columns:
        data1 = df1["Adj Close"]
    elif isinstance(df1, pd.Series):
        data1 = df1
    else:
        raise ValueError(f"'Adj Close' not found for {asset1}")

    if "Adj Close" in df2.columns:
        data2 = df2["Adj Close"]
    elif isinstance(df2, pd.Series):
        data2 = df2
    else:
        raise ValueError(f"'Adj Close' not found for {asset2}")

    # Merge and calculate ratio
    combined = pd.concat([data1, data2], axis=1, join="inner")
    combined.columns = [asset1, asset2]
    combined["Ratio"] = combined[asset1] / combined[asset2]

    # Plot chart
    plt.figure(figsize=(12, 6))
    plt.plot(combined.index, combined["Ratio"])
    plt.yscale("log")
    plt.title(f"{asset1} / {asset2} (Log Scale)")
    plt.grid(True)
    plt.tight_layout()

    # Save to file
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
