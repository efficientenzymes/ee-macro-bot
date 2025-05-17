
import requests
import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("macro-bot")

def get_weekly_macro_highlights():
    try:
        today = datetime.date.today()
        start = today - datetime.timedelta(days=7)

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

        highlights = []
        for row in rows:
            date_str = row.get("data-event-datetime")
            if not date_str:
                continue

            date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            if not (start <= date_obj <= today):
                continue

            event = row.select_one(".event")
            actual = row.select_one(".actual")
            forecast = row.select_one(".forecast")

            if event:
                event_name = event.get_text(strip=True)
                actual_val = actual.get_text(strip=True) if actual else "n/a"
                forecast_val = forecast.get_text(strip=True) if forecast else "n/a"
                summary = f"{event_name}: {actual_val} (exp {forecast_val})"
                highlights.append(summary)

        return highlights[:8]

    except Exception as e:
        logger.error(f"[ERROR] get_weekly_macro_highlights failed: {e}")
        return []
