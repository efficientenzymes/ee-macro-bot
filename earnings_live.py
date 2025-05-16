import requests
import datetime
import logging

logger = logging.getLogger("macro-bot")

def get_earnings_for_today():
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        url = f"https://query1.finance.yahoo.com/v7/finance/calendar/earnings?day={today}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch earnings: HTTP {response.status_code}")

        data = response.json()
        earnings = data.get("finance", {}).get("result", [])
        if not earnings:
            return []

        results = []
        for item in earnings:
            for report in item.get("earnings", []):
                ticker = report.get("symbol", "N/A")
                time = report.get("startdatetime", "").split("T")[-1].replace("Z", "")
                slot = "Before Open" if "08" in time else "After Close"
                results.append(f"{slot}: {ticker}")

        return sorted(results)

    except Exception as e:
        logger.error(f"[ERROR] get_earnings_for_today failed: {e}")
        return []
