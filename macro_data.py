import yfinance as yf
import datetime
import pytz

def get_macro_events_for_today():
    return [
        "8:30 AM – Initial Jobless Claims",
        "10:00 AM – Existing Home Sales"
    ]

def get_past_week_events():
    return [
        "Monday – Empire State Manufacturing",
        "Tuesday – Retail Sales",
        "Wednesday – CPI",
        "Thursday – Jobless Claims",
        "Friday – Leading Indicators"
    ]

def get_earnings_for_today():
    return [
        "Before Open: WMT, HD",
        "After Close: NVDA, AMAT"
    ]

def get_sentiment_summary():
    try:
        vix = yf.Ticker("^VIX").history(period="2d")["Close"].iloc[-1]
    except Exception as e:
        print(f"VIX fetch error: {e}")
        vix = 15.0

    try:
        move = yf.Ticker("^MOVE").history(period="2d")["Close"].iloc[-1]
    except Exception as e:
        print(f"MOVE fetch error: {e}")
        move = 100.0

    put_call = 0.74  # Static fallback

    sentiment = {
        "vix": f"{vix:.2f}",
        "move": f"{move:.0f}",
        "put_call": f"{put_call:.2f}",
        "vix_level": "Low" if vix < 15 else "Elevated" if vix > 20 else "Neutral",
        "move_level": "Calm" if move < 95 else "Neutral" if move < 115 else "Elevated",
        "put_call_level": "Risk-on" if put_call < 0.75 else "Neutral" if put_call < 1.0 else "Risk-off"
    }

    return sentiment
