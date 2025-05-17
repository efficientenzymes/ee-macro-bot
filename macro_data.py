import requests
from datetime import datetime, timedelta
import os

TRADINGECONOMICS_API_KEY = os.getenv("TRADINGECON_API_KEY")

def fetch_economic_events(date: str):
    try:
        url = f"https://api.tradingeconomics.com/calendar?c={TRADINGECONOMICS_API_KEY}&d={date}"
        response = requests.get(url)
        data = response.json()

        events = []
        for item in data:
            if "event" in item and item.get("date")[:10] == date:
                time = item.get("date", "")[11:16]
                events.append(f"{item['event']} at {time} ({date})")

        return events if events else [f"No scheduled events found for {date}."]
    except Exception as e:
        return [f"Error fetching events: {str(e)}"]

def fetch_earnings(date: str):
    try:
        # 🔧 Replace with real earnings API (e.g. Nasdaq, Yahoo Finance, or TradingView scraping)
        return [f"(Stub) Live earnings data for {date} coming soon."]
    except Exception as e:
        return [f"Error fetching earnings: {str(e)}"]

def get_macro_events_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    return fetch_economic_events(today)

def get_macro_events_for_tomorrow():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return fetch_economic_events(tomorrow)

def get_earnings_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    return fetch_earnings(today)

def get_earnings_for_tomorrow():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return fetch_earnings(tomorrow)

def get_sentiment_summary():
    # 🔧 You should eventually replace this with values fetched from your live indicator system.
    return {
        "vix": "15.00",
        "move": "100",
        "put_call": "0.75",
        "vix_level": "Neutral",
        "move_level": "Neutral",
        "put_call_level": "Neutral"
    }
