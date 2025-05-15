import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import os

def generate_chart(chart_name="btc_vs_spx", out_path="btc_vs_spx.png", logo_path="assets/logo.png"):
    print("📊 Generating BTC vs SPX chart...")

    # Download 3 months of data
    btc = yf.download("BTC-USD", period="3mo", interval="1d")["Close"]
    spx = yf.download("^GSPC", period="3mo", interval="1d")["Close"]

    # Align by date and normalize
    data = pd.DataFrame({"BTC": btc, "SPX": spx}).dropna()
    data /= data.iloc[0]  # normalize to 1.0
    data.index = pd.to_datetime(data.index)

    # Plot
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data["BTC"], label="BTC-USD", linewidth=2)
    ax.plot(data.index, data["SPX"], label="S&P 500", linewidth=2)
    ax.set_title("BTC vs SPX - Last 3 Months")
    ax.legend()

    # Add watermark if logo exists
    if os.path.exists(logo_path):
        img = plt.imread(logo_path)
        ax.figure.figimage(img, xo=fig.bbox.xmax - 130, yo=fig.bbox.ymin + 10, alpha=0.2, zorder=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"✅ Chart saved to {out_path}")
