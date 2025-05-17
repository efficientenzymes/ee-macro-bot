
import requests
import datetime
import csv
import os

DATA_PATH = "liquidity_data.csv"

def fetch_liquidity_data():
    # Use real API sources or file downloads here
    # For production, replace these URLs with automated CSV parsers or APIs
    # Here we simulate scraping values from live endpoints or processed datasets

    # Placeholder example values (real fetch logic goes here)
    fed_balance_sheet = 8.91e12   # 8.91 trillion
    reverse_repo = 345e9          # 345 billion
    tga_account = 593e9           # 593 billion

    return {
        "fed_balance_sheet": fed_balance_sheet,
        "reverse_repo": reverse_repo,
        "tga": tga_account
    }

def load_previous_data():
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        if rows:
            return rows[-1]
    return None

def save_current_data(current_data):
    file_exists = os.path.exists(DATA_PATH)
    with open(DATA_PATH, mode='a', newline='') as csvfile:
        fieldnames = ["date", "fed_balance_sheet", "reverse_repo", "tga"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": datetime.date.today().isoformat(),
            "fed_balance_sheet": current_data["fed_balance_sheet"],
            "reverse_repo": current_data["reverse_repo"],
            "tga": current_data["tga"]
        })

def format_number(n):
    if n >= 1e12:
        return f"${n / 1e12:.2f}T"
    elif n >= 1e9:
        return f"${n / 1e9:.0f}B"
    return f"${n:,.0f}"

def format_delta(val):
    symbol = "↑" if val > 0 else "↓"
    return f"{symbol} {format_number(abs(val))}"

def get_liquidity_summary():
    current = fetch_liquidity_data()
    previous = load_previous_data()
    save_current_data(current)

    if not previous:
        return "💧 Liquidity Tracker:
• No prior data to compare yet."

    deltas = {
        "fed_balance_sheet": current["fed_balance_sheet"] - float(previous["fed_balance_sheet"]),
        "reverse_repo": current["reverse_repo"] - float(previous["reverse_repo"]),
        "tga": current["tga"] - float(previous["tga"])
    }

    fed_line = f"• Fed Balance Sheet: {format_number(current['fed_balance_sheet'])} ({format_delta(deltas['fed_balance_sheet'])})"
    rrp_line = f"• Reverse Repo (RRP): {format_number(current['reverse_repo'])} ({format_delta(deltas['reverse_repo'])})"
    tga_line = f"• Treasury General Account: {format_number(current['tga'])} ({format_delta(deltas['tga'])})"

    direction_score = sum([-1 if d < 0 else 1 for d in deltas.values()])
    if direction_score <= -2:
        narrative = "🧠 Liquidity withdrawn this week. Headwinds for risk assets."
    elif direction_score >= 2:
        narrative = "🧠 Net liquidity injection. Tailwinds for risk sentiment."
    else:
        narrative = "🧠 Liquidity roughly neutral. Markets may remain balanced."

    return f"💧 **Liquidity Tracker**
{fed_line}
{rrp_line}
{tga_line}

{narrative}"
