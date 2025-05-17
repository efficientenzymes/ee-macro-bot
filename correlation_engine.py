import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

TICKERS = {
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "BTC": "BTC-USD",
    "GOLD": "GC=F",
    "QQQ": "QQQ",
    "TLT": "TLT",
    "HYG": "HYG",
    "LQD": "LQD",
    "DXY": "DX-Y.NYB"
}

def get_weekly_correlation_matrix():
    end = datetime.now()
    start = end - timedelta(days=14)

    data = yf.download(list(TICKERS.values()), start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))["Adj Close"]
    data.columns = list(TICKERS.keys())
    data.dropna(axis=1, inplace=True)

    returns = data.pct_change().dropna()
    corr = returns.corr()

    return corr

def get_correlation_summary():
    corr = get_weekly_correlation_matrix()
    lines = [f"🔗 **Correlation Matrix (Past 2 Weeks)**"]

    for i, a in enumerate(corr.columns):
        for b in corr.columns[i+1:]:
            val = corr.loc[a, b]
            if abs(val) > 0.5:
                symbol = "↑" if val > 0 else "↓"
                lines.append(f"• {a}/{b}: {symbol} {val:.2f}")

    return lines or ["No strong correlations detected."]
