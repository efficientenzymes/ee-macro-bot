import requests
import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("macro-bot")

def get_macro_events_for_today():
    events = []
    try:
        # Try Investing.com first
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        url = "https://www.investing.com/economic-calendar/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Investing.com HTTP {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("tr.js-event-item")

        for row in rows:
            date_attr = row.get("data-event-datetime")
            if not date_attr or not date_attr.startswith(today):
                continue

            time = row.select_one(".time")
            event = row.select_one(".event")
            if time and event:
                time_str = time.get_text(strip=True)
                event_str = event.get_text(strip=True)
                if event_str:
                    events.append(f"{time_str} – {event_str}")

        if events:
            return events[:10]
        else:
            raise Exception("Investing scrape returned no data.")

    except Exception as e:
        logger.warning(f"[WARNING] Investing.com failed: {e}")

    # Fallback: Try ForexFactory
    try:
        url = "https://www.forexfactory.com/calendar"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"ForexFactory HTTP {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("tr.calendar__row")

        for row in rows:
            time = row.select_one(".calendar__time")
            event = row.select_one(".calendar__event-title")
            if time and event:
                time_str = time.get_text(strip=True)
                event_str = event.get_text(strip=True)
                if event_str:
                    events.append(f"{time_str} – {event_str}")

    except Exception as e:
        logger.error(f"[ERROR] ForexFactory fallback failed: {e}")

    return events[:10]
