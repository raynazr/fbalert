from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

FB_URL = "https://www.facebook.com/marketplace/edmonton/search?query=2017%20car"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEEN_FILE = "seen_listings.json"

def load_seen():
    if Path(SEEN_FILE).exists():
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(data):
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def scrape_marketplace():
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    response = requests.get(FB_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = []

    for item in soup.find_all("a", href=True):
        title = item.text.strip()
        link = item["href"]
        if "marketplace" in link and title:
            listings.append({"title": title, "link": link})
    return listings

def main():
    seen = load_seen()
    current = scrape_marketplace()
    new = [entry for entry in current if entry["link"] not in [s["link"] for s in seen]]

    if new:
        print(f"Found {len(new)} new listing(s).")
        for entry in new:
            message = f"<b>{entry['title']}</b>\n<a href='{entry['link']}'>View Listing</a>"
            send_telegram(message)
        save_seen(current)
    else:
        print("No new listings found.")

if __name__ == "__main__":
    main()
