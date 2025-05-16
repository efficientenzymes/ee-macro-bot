import yfinance as yf
import datetime
import pytz

# === Mock economic calendar (replace with real API later if needed) ===
def get_macro_events_for_today():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(eastern)
    if now.strftime("%Y-%m-%d") == "2025-05-15":
        return [
            "8:30 AM – CPI (m/m): Forecast 0.3%",
            "8:30 AM – Core CPI (y/y): Forecast 3.6%",
            "10:30 AM – EIA Crude Oil Inventories"
        ]
    return []

def get_past_week_events():
    return [
        "Monday – Empire State Manufacturing",
        "Tuesday – PPI & Retail Sales",
        "Wednesday – CPI",
        "Thursday – Jobless Claims",
        "Friday – UoM Sentiment"
    ]

# === Mock earnings (can be linked to Earnings Whisper or Yahoo API later) ===
def get_earnings_for_today():
    return [
        "Before Open: TGT, JD",
        "After Close: CSCO, SONY"
    ]

# === Sentiment Summary ===
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

    try:
        put_call = yf.Ticker("PCALL").history(period="2d")["Close"].iloc[-1]
    except Exception as e:
        print(f"Put/Call fetch error: {e}")
        put_call = 0.75

    sentiment = {
        "vix": f"{vix:.2f}",
        "move": f"{move:.0f}",
        "put_call": f"{put_call:.2f}",
        "vix_level": "Low" if vix < 15 else "Elevated" if vix > 20 else "Neutral",
        "move_level": "Calm" if move < 95 else "Neutral" if move < 115 else "Elevated",
        "put_call_level": "Risk-on" if put_call < 0.75 else "Neutral" if put_call < 1.0 else "Risk-off"
    }

    return sentiment
