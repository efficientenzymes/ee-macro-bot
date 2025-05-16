import yfinance as yf
from earnings_live import get_earnings_for_today
from macro_events_live import get_macro_events_for_today

def get_sentiment_summary():
    try:
        vix = yf.Ticker("^VIX").history(period="2d")["Close"].iloc[-1]
        move = yf.Ticker("^MOVE").history(period="2d")["Close"].iloc[-1]
        put_call = yf.Ticker("^PUTCALL").history(period="2d")["Close"].iloc[-1]
    except Exception as e:
        print(f"Sentiment fetch error: {e}")
        vix, move, put_call = 15.0, 100.0, 0.75

    sentiment = {
        "vix": f"{vix:.2f}",
        "move": f"{move:.0f}",
        "put_call": f"{put_call:.2f}",
        "vix_level": "Low" if vix < 15 else "Elevated" if vix > 20 else "Neutral",
        "move_level": "Calm" if move < 95 else "Neutral" if move < 115 else "Elevated",
        "put_call_level": "Risk-on" if put_call < 0.75 else "Neutral" if put_call < 1.0 else "Risk-off"
    }

    return sentiment

