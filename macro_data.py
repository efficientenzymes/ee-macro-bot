from datetime import datetime, timedelta

# ✅ These are mock implementations using real dates.
# Replace the contents with live calendar/earnings API logic if needed.

def get_macro_events_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        f"CPI report at 8:30 AM ET ({today})",
        f"10Y Treasury Auction at 1:00 PM ET ({today})"
    ]

def get_macro_events_for_tomorrow():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return [
        f"Jobless Claims at 8:30 AM ET ({tomorrow})",
        f"Natural Gas Inventory at 10:30 AM ET ({tomorrow})"
    ]

def get_earnings_for_today():
    return ["Pre-market: JPM, DAL", "After hours: NFLX, TSLA"]

def get_earnings_for_tomorrow():
    return ["Pre-market: MS, UNH", "After hours: AAPL, AMZN"]

def get_sentiment_summary():
    return {
        "vix": "15.00",
        "move": "100",
        "put_call": "0.75",
        "vix_level": "Neutral",
        "move_level": "Neutral",
        "put_call_level": "Neutral"
    }
