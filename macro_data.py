
import requests
from datetime import datetime, timedelta
import os

# 🔐 Your real API keys from environment
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_economic_events(date_str):
    try:
        url = "https://economic-calendar.p.rapidapi.com/events-by-date"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "economic-calendar.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params={"date": date_str})
        response.raise_for_status()
        data = response.json()

        if not data or "data" not in data:
            return [f"No macro events found for {date_str}"]

        events = []
        for item in data["data"]:
            time = item.get("date", "")[11:16]
            name = item.get("event", "Unknown Event")
            country = item.get("country", "")
            events.append(f"{name} ({country}) at {time} ({date_str})")

        return events or [f"No macro events found for {date_str}"]
    except Exception as e:
        return [f"Error fetching economic events: {str(e)}"]

def fetch_earnings(date_str):
    try:
        url = f"https://finnhub.io/api/v1/calendar/earnings?from={date_str}&to={date_str}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "earningsCalendar" not in data:
            return [f"No earnings found for {date_str}"]

        earnings = data["earningsCalendar"]
        if not earnings:
            return [f"No earnings scheduled for {date_str}"]

        pre = [e["symbol"] for e in earnings if e["hour"] == "bmo"]
        after = [e["symbol"] for e in earnings if e["hour"] == "amc"]

        result = []
        if pre:
            result.append("Pre-market: " + ", ".join(pre))
        if after:
            result.append("After hours: " + ", ".join(after))
        return result or [f"Earnings data available, but no time classified for {date_str}"]
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
    # Replace this when sentiment engine is live; safe fallback for now
    return {
        "vix": "15.00",
        "move": "100",
        "put_call": "0.75",
        "vix_level": "Neutral",
        "move_level": "Neutral",
        "put_call_level": "Neutral"
    }
