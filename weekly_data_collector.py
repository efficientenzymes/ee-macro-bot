
import datetime
import yfinance as yf
import requests
import os
import logging

logger = logging.getLogger("macro-bot")

def get_past_week_sentiment_summary():
    try:
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=7)

        data = {}
        for symbol, label in {
            "^VIX": "VIX",
            "^MOVE": "MOVE",
            "^PUTCALL": "Put/Call Ratio"
        }.items():
            df = yf.download(symbol, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)
            if df.empty:
                logger.warning(f"[WARNING] No data for {symbol}")
                continue
            pct_change = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
            data[label] = f"{pct_change:+.2f}% over the week"

        return data
    except Exception as e:
        logger.error(f"[ERROR] Sentiment summary failed: {e}")
        return {}

def get_past_week_megacap_earnings():
    try:
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY is not set.")

        end = datetime.datetime.now().strftime("%Y-%m-%d")
        start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/calendar/earnings?from={start}&to={end}&token={api_key}"

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Earnings fetch failed: HTTP {response.status_code}")

        earnings = response.json().get("earningsCalendar", [])
        megacaps = []

        for report in earnings:
            symbol = report.get("symbol")
            time = report.get("time", "").lower()
            if not symbol or ("bmo" not in time and "amc" not in time):
                continue

            # Profile lookup for market cap
            profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
            prof = requests.get(profile_url).json()
            if prof.get("marketCapitalization", 0) >= 10000:
                megacaps.append(symbol)

        return sorted(megacaps)
    except Exception as e:
        logger.error(f"[ERROR] Weekly megacap earnings fetch failed: {e}")
        return []

def get_past_week_summary():
    sentiment = get_past_week_sentiment_summary()
    earnings = get_past_week_megacap_earnings()

    summary = []

    for label, change in sentiment.items():
        summary.append(f"{label}: {change}")

    if earnings:
        summary.append("Earnings: " + ", ".join(earnings))

    return summary
