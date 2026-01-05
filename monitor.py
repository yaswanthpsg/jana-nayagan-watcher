import requests
import time
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ===================== CONFIG =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# URLs to monitor
BMS_URL = "https://in.bookmyshow.com/movies/coimbatore/jana-nayagan/buytickets/ET00430817/20260109"
DISTRICT_URL = "https://www.district.in/movies/coimbatore"
TICKETNEW_URL = "https://ticketnew.com/movies/jana-nayagan-movie-detail-188681"

CHECK_INTERVAL = 60  # seconds
RUN_DAYS = 6

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Track already-alerted theatres
seen_theatres = set()

END_TIME = datetime.utcnow() + timedelta(days=RUN_DAYS)

# ==================================================


def send_alert(message):
    """Send message to Telegram group"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload, timeout=10)


def extract_theatres_from_text(text):
    """Extract possible theatre names from page text"""
    theatres = set()
    keywords = [
        "pvr", "inox", "cinepolis", "kg", "broadway",
        "miraj", "karpagam", "theatre", "cinema"
    ]

    for line in text.splitlines():
        clean = line.strip()
        if len(clean) < 5:
            continue
        for key in keywords:
            if key in clean.lower():
                theatres.add(clean[:80])
    return theatres


def check_bookmyshow():
    resp = requests.get(BMS_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n").lower()

    # If booking page is live, theatre names will appear
    theatres = extract_theatres_from_text(text)

    for theatre in theatres:
        key = f"BMS::{theatre}"
        if key not in seen_theatres:
            seen_theatres.add(key)
            send_alert(
                f"🚨 NEW THEATRE OPENED 🚨\n\n"
                f"🎬 Jana Nayagan\n"
                f"🏢 {theatre}\n"
                f"📍 Coimbatore\n"
                f"🌐 Platform: BookMyShow\n"
                f"🕒 {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
                f"👉 Book now:\n{BMS_URL}"
            )


def check_district():
    resp = requests.get(DISTRICT_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n").lower()

    if "jana nayagan" not in text:
        return

    theatres = extract_theatres_from_text(text)

    for theatre in theatres:
        key = f"DISTRICT::{theatre}"
        if key not in seen_theatres:
            seen_theatres.add(key)
            send_alert(
                f"🚨 NEW THEATRE OPENED 🚨\n\n"
                f"🎬 Jana Nayagan\n"
                f"🏢 {theatre}\n"
                f"📍 Coimbatore\n"
                f"🌐 Platform: District\n"
                f"🕒 {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
                f"👉 Book now:\n{DISTRICT_URL}"
            )


def check_ticketnew():
    resp = requests.get(TICKETNEW_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n").lower()

    if "no shows" in text or "not available" in text:
        return

    theatres = extract_theatres_from_text(text)

    for theatre in theatres:
        key = f"TICKETNEW::{theatre}"
        if key not in seen_theatres:
            seen_theatres.add(key)
            send_alert(
                f"🚨 NEW THEATRE OPENED 🚨\n\n"
                f"🎬 Jana Nayagan\n"
                f"🏢 {theatre}\n"
                f"📍 Coimbatore\n"
                f"🌐 Platform: TicketNew\n"
                f"🕒 {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
                f"👉 Book now:\n{TICKETNEW_URL}"
            )


# ===================== MAIN LOOP =====================

send_alert("🎬 Jana Nayagan booking watcher started (All theatres, 6 days monitoring)")

while datetime.utcnow() < END_TIME:
    try:
        check_bookmyshow()
        check_district()
        check_ticketnew()
    except Exception as e:
        send_alert(f"⚠️ Watcher error:\n{str(e)}")

    time.sleep(CHECK_INTERVAL)

send_alert("⏹ Jana Nayagan booking watcher stopped (6 days completed)")
