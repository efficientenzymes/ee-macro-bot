import datetime
import pytz

# Mock economic calendar data
def get_macro_events_for_today():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(eastern)
    if now.strftime("%Y-%m-%d") == "2025-05-16":
        return [
            "8:30 AM – CPI (m/m): Actual 0.3%",
            "8:30 AM – Core CPI (y/y): Actual 3.6%",
            "10:30 AM – EIA Crude Oil Inventories"
        ]
    return ["No major economic events scheduled for today"]

def get_past_week_events():
    return [
        "Monday – Empire State Manufacturing",
        "Tuesday – PPI & Retail Sales",
        "Wednesday – CPI",
        "Thursday – Jobless Claims",
        "Friday – UoM Sentiment"
    ]

# Mock earnings data
def get_earnings_for_today():
    return [
        "Before Open: TGT, JD",
        "After Close: CSCO, SONY"
    ]

# Simplified sentiment summary with static data
def get_sentiment_summary():
    # Static values instead of fetching from yfinance
    sentiment = {
        "vix": "17.25",
        "move": "105",
        "put_call": "0.74",
        "vix_level": "Neutral",
        "move_level": "Neutral",
        "put_call_level": "Risk-on"
    }
    
    return sentiment