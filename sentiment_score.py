import os
from dotenv import load_dotenv
import requests

load_dotenv()

FNG_API_KEY = os.getenv("FNG_API_KEY")

def get_fear_and_greed_score():
    try:
        response = requests.get(
            "https://api.alternative.me/fng/",
            params={"limit": 1, "format": "json", "api_key": FNG_API_KEY},
            timeout=10
        )
        data = response.json()
        value = int(data["data"][0]["value"])
        return value
    except Exception as e:
        print(f"Error fetching Fear & Greed Index: {e}")
        return None

def calculate_sentiment_score(metrics: dict) -> str:
    """
    Accepts a dict with the following keys:
    - btc_vix_ratio: float
    - vix_level: float
    - put_call_ratio: float
    - hyg_lqd_trend: str ("up", "down", or "flat")
    - spx_dxy_ratio: float
    """
    score = 0
    breakdown = []

    # BTC/VIX
    if metrics["btc_vix_ratio"] > 0.5:
        score += 1
        breakdown.append("↑ BTC/VIX")
    else:
        score -= 1
        breakdown.append("↓ BTC/VIX")

    # VIX Level
    if metrics["vix_level"] < 14:
        score += 1
        breakdown.append("🟢 Low VIX")
    elif metrics["vix_level"] > 20:
        score -= 1
        breakdown.append("🔴 High VIX")

    # Put/Call Ratio
    if metrics["put_call_ratio"] < 0.8:
        score += 1
        breakdown.append("🟢 Bullish Put/Call")
    elif metrics["put_call_ratio"] > 1.0:
        score -= 1
        breakdown.append("🔴 Bearish Put/Call")

    # HYG/LQD Trend
    trend = metrics["hyg_lqd_trend"]
    if trend == "up":
        score += 1
        breakdown.append("↑ HYG/LQD")
    elif trend == "down":
        score -= 1
        breakdown.append("↓ HYG/LQD")

    # SPX/DXY Ratio
    if metrics["spx_dxy_ratio"] > 1.5:
        score += 1
        breakdown.append("↑ SPX/DXY")
    else:
        score -= 1
        breakdown.append("↓ SPX/DXY")

    # Fear & Greed Index
    fng_score = get_fear_and_greed_score()
    if fng_score is not None:
        if fng_score > 60:
            score += 1
            breakdown.append("🟢 High F&G")
        elif fng_score < 40:
            score -= 1
            breakdown.append("🔴 Low F&G")
        else:
            breakdown.append("🟡 Neutral F&G")

    # Final Sentiment
    if score >= 3:
        symbol = "🟢"
        label = "Risk-On"
    elif score <= -3:
        symbol = "🔴"
        label = "Risk-Off"
    else:
        symbol = "🟡"
        label = "Neutral"

    return f"{symbol} {score:+} {label} (Range: -5 to +5) | " + ", ".join(breakdown)
