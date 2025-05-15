import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import os
import datetime

plt.style.use("dark_background")

def _fetch(ticker, label):
    print(f"🔄 Fetching {label} ({ticker})...")
    try:
        df = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True)
        if df.empty:
            raise ValueError(f"No data for {ticker}")
        return df["Close"]
    except Exception as e:
        print(f"❌ Error fetching {label}: {e}")
        return pd.Series()

def _plot_chart(data_dict, title, filename, logo_path="assets/logo.png"):
    fig, ax = plt.subplots(figsize=(10, 5))
    for label, series in data_dict.items():
        if not series.empty:
            ax.plot(series.index, series / series.iloc[0], label=label, linewidth=2)
    ax.set_title(title)
    ax.legend()
    if os.path.exists(logo_path):
        try:
            img = plt.imread(logo_path)
            ax.figure.figimage(img, xo=fig.bbox.xmax - 130, yo=fig.bbox.ymin + 10, alpha=0.2, zorder=10)
        except Exception as e:
            print(f"⚠️ Failed to load watermark: {e}")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Saved: {filename}")

def generate_all_charts():
    charts = []

    # BTC vs SPX
    btc = _fetch("BTC-USD", "BTC")
    spx = _fetch("^GSPC", "S&P 500")
    _plot_chart({"BTC": btc, "S&P 500": spx}, "BTC vs SPX - Last 3 Months", "btc_vs_spx.png")
    charts.append("btc_vs_spx.png")

    # Gold vs Silver
    gold = _fetch("GC=F", "Gold")
    silver = _fetch("SI=F", "Silver")
    _plot_chart({"Gold": gold, "Silver": silver}, "Gold vs Silver - Last 3 Months", "gold_vs_silver.png")
    charts.append("gold_vs_silver.png")

    # BTC vs ETH
    eth = _fetch("ETH-USD", "ETH")
    _plot_chart({"BTC": btc, "ETH": eth}, "BTC vs ETH - Last 3 Months", "btc_vs_eth.png")
    charts.append("btc_vs_eth.png")

    # BTC vs VIX
    vix = _fetch("^VIX", "VIX")
    _plot_chart({"BTC": btc, "VIX": vix}, "BTC vs VIX - Last 3 Months", "btc_vs_vix.png")
    charts.append("btc_vs_vix.png")

    # Yield Curve (10Y - 2Y)
    ten_year = _fetch("^TNX", "10Y Yield")
    two_year = _fetch("^IRX", "2Y Yield")
    if not ten_year.empty and not two_year.empty:
        curve = ten_year - two_year
        _plot_chart({"10Y - 2Y": curve}, "Yield Curve Inversion (10Y - 2Y)", "yield_curve.png")
        charts.append("yield_curve.png")

    # DXY
    dxy = _fetch("DX-Y.NYB", "Dollar Index")
    _plot_chart({"DXY": dxy}, "DXY (Dollar Index) - Last 3 Months", "dxy.png")
    charts.append("dxy.png")

    # Put/Call Ratio
    pcr = _fetch("^CPC", "Put/Call Ratio")
    _plot_chart({"Put/Call Ratio": pcr}, "Put/Call Ratio (CBOE) - Last 3 Months", "put_call_ratio.png")
    charts.append("put_call_ratio.png")

    return charts
