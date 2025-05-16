import requests
import datetime
import os
import logging

logger = logging.getLogger("macro-bot")

def get_earnings_for_today():
    try:
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY is not set.")

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/calendar/earnings?from={today}&to={today}&token={api_key}"

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch earnings: HTTP {response.status_code}")

        data = response.json()
        earnings = data.get("earningsCalendar", [])

        results = []
        for report in earnings:
            symbol = report.get("symbol")
            time = report.get("time", "").lower()
            if not symbol:
                continue

            slot = (
                "Before Open" if "bmo" in time else
                "After Close" if "amc" in time else
                "Time N/A"
            )
            results.append(f"{slot}: {symbol}")

        return sorted(results)

    except Exception as e:
        logger.error(f"[ERROR] get_earnings_for_today failed: {e}")
        return []
