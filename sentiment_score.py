
import yfinance as yf
import requests
import datetime
import logging

logger = logging.getLogger("macro-bot")

def fetch_ratio(symbol1, symbol2, period="7d"):
    try:
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=7)
        s1 = yf.download(symbol1, start=start, end=end, progress=False)["Close"]
        s2 = yf.download(symbol2, start=start, end=end, progress=False)["Close"]
        ratio = (s1 / s2).dropna()
        return ratio
    except Exception as e:
        logger.warning(f"[WARNING] Failed to fetch ratio {symbol1}/{symbol2}: {e}")
        return None

def get_fear_greed_index():
    try:
        url = "https://fear-and-greed-index.p.rapidapi.com/v1/fgi"
        headers = {
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",  # Replace this with your real key
            "X-RapidAPI-Host": "fear-and-greed-index.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        value = int(data["fgi"]["now"]["value"])
        label = data["fgi"]["now"]["valueText"]
        return value, label
    except Exception as e:
        logger.warning(f"[WARNING] Fear & Greed index fetch failed: {e}")
        return None, None

def score_sentiment():
    score = 0
    reasons = []

    # BTC/VIX
    btc_vix = fetch_ratio("BTC-USD", "^VIX")
    if btc_vix is not None and len(btc_vix) >= 2:
        change = btc_vix.iloc[-1] - btc_vix.iloc[0]
        if change > 0:
            score += 1
            reasons.append("BTC/VIX rising")
        else:
            score -= 1
            reasons.append("BTC/VIX falling")

    # SPX/DXY
    spx_dxy = fetch_ratio("^GSPC", "DX-Y.NYB")
    if spx_dxy is not None and len(spx_dxy) >= 2:
        change = spx_dxy.iloc[-1] - spx_dxy.iloc[0]
        if change > 0:
            score += 1
            reasons.append("SPX/DXY rising")
        else:
            score -= 1
            reasons.append("SPX/DXY falling")

    # HYG/LQD
    hyg_lqd = fetch_ratio("HYG", "LQD")
    if hyg_lqd is not None and len(hyg_lqd) >= 2:
        change = hyg_lqd.iloc[-1] - hyg_lqd.iloc[0]
        if change > 0:
            score += 1
            reasons.append("HYG/LQD rising")
        else:
            score -= 1
            reasons.append("HYG/LQD falling")

    # VIX level
    try:
        vix = yf.Ticker("^VIX").history(period="2d")["Close"].iloc[-1]
        if vix < 15:
            score += 1
            reasons.append("VIX low")
        elif vix > 20:
            score -= 1
            reasons.append("VIX high")
    except Exception as e:
        logger.warning(f"[WARNING] Failed to fetch VIX: {e}")

    # Put/Call ratio
    try:
        put_call = yf.Ticker("^PUTCALL").history(period="2d")["Close"].iloc[-1]
        if put_call < 0.75:
            score += 1
            reasons.append("Put/Call low (bullish)")
        elif put_call > 1.0:
            score -= 1
            reasons.append("Put/Call high (bearish)")
    except Exception as e:
        logger.warning(f"[WARNING] Failed to fetch Put/Call: {e}")

    # Fear & Greed Index
    fgi_val, fgi_label = get_fear_greed_index()
    if fgi_val is not None:
        if fgi_val >= 70:
            score += 1
        elif fgi_val <= 30:
            score -= 1
        reasons.append(f"Fear & Greed Index: {fgi_val} ({fgi_label})")

    emoji = "🟢" if score > 1 else "🟡" if -1 <= score <= 1 else "🔴"
    label = "Risk-On" if score > 1 else "Neutral" if -1 <= score <= 1 else "Risk-Off"
    header = f"{emoji} {score:+d} {label} (Range: -5 to +5)"

    return header, reasons
