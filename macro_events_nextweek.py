def get_macro_events_for_next_week():
    try:
        today = datetime.date.today()
        start = today + datetime.timedelta(days=(7 - today.weekday()))  # Next Monday
        end = start + datetime.timedelta(days=5)

        url = "https://www.investing.com/economic-calendar/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch macro events: HTTP {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("tr.js-event-item")

        events = []
        for row in rows:
            date_str = row.get("data-event-datetime")
            if not date_str:
                continue

            date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            if start <= date_obj <= end:
                time = row.select_one(".time")
                event = row.select_one(".event")
                if time and event:
                    time_str = time.get_text(strip=True)
                    event_str = event.get_text(strip=True)
                    weekday = date_obj.strftime("%A")
                    if event_str:
                        events.append(f"{weekday} {time_str} – {event_str}")

        return events[:10]

    except Exception as e:
        logger.error(f"[ERROR] get_macro_events_for_next_week failed: {e}")
        return []
