import requests
import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("macro-bot")

def get_macro_events_for_today():
    try:
        today = datetime.datetime.now().strftime("%b %d")  # Format like "May 16"
        url = "https://www.investing.com/economic-calendar/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch macro events: HTTP {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("tr.js-event-item")

        events = []
        for row in rows:
            date_text = row.get("data-event-datetime")
            if not date_text:
                continue

            if not date_text.startswith(datetime.datetime.utcnow().strftime("%Y-%m-%d")):
                continue

            time_cell = row.select_one(".time")
            event_cell = row.select_one(".event")
            if time_cell and event_cell:
                time_str = time_cell.get_text(strip=True)
                event_str = event_cell.get_text(strip=True)
                if event_str:
                    events.append(f"{time_str} – {event_str}")

        if not events:
            logger.warning("[WARNING] No macro events found for today.")
        return events[:10]

    except Exception as e:
        logger.error(f"[ERROR] get_macro_events_for_today failed: {e}")
        return []
