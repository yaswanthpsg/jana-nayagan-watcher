import requests
import time
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ===================== ENV VARIABLES =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("BOT_TOKEN or CHAT_ID not set in environment variables")

# ===================== CONFIG =====================

RUN_DAYS = 6
CHECK_INTERVAL = 60  # seconds

END_TIME = datetime.utcnow() + timedelta(days=RUN_DAYS)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://in.bookmyshow.com/"
}

# ===== BOOKMYSHOW CONFIG =====
BMS_MOVIE_CODE = "ET00430817"
BMS_CITY = "coimbatore"
BMS_BOOKING_URL = (
    f"https://in.bookmyshow.com/movies/{BMS_CITY}/jana-nayagan/"
    f"buytickets/{BMS_MOVIE_CODE}/20260109"
)

# ===== TICKETNEW CONFIG =====
TICKETNEW_URL = "https://ticketnew.com/movies/coimbatore"

# ===================== STATE =====================

seen_theatres = set()

# ===================== UTILS =====================

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload, timeout=10)


def now():
    return datetime.now().strftime("%d %b %Y %I:%M %p")


# ===================== BOOKMYSHOW (API) =====================

def check_bookmyshow_per_theatre():
    api_url = (
        "https://in.bookmyshow.com/api/explore/v1/showtimes"
        f"?movieCode={BMS_MOVIE_CODE}"
        f"&city={BMS_CITY}"
    )

    resp = requests.get(api_url, headers=HEADERS, timeout=15)

    if resp.status_code != 200:
        return

    data = resp.json()
    cinemas = data.get("cinemas", [])

    for cinema in cinemas:
        theatre = cinema.get("cinemaName", "").strip()
        shows = cinema.get("shows", [])

        if not theatre or not shows:
            continue

        key = f"BMS::{theatre}"

        if key not in seen_theatres:
            seen_theatres.add(key)
            send_alert(
                f"🚨 NEW THEATRE OPENED 🚨\n\n"
                f"🎬 Jana Nayagan\n"
                f"🏢 {theatre}\n"
                f"📍 Coimbatore\n"
                f"🌐 Platform: BookMyShow\n"
                f"🕒 {now()}\n\n"
                f"👉 Book now:\n{BMS_BOOKING_URL}"
            )

# ===================== TICKETNEW =====================

def extract_theatres_from_text(text):
    theatres = set()
    keywords = [
        "pvr", "inox", "cinepolis", "kg",
        "broadway", "miraj", "karpagam",
        "theatre", "cinema"
    ]

    for line in text.splitlines():
        clean = line.strip()
        if len(clean) < 5:
            continue
        for key in keywords:
            if key in clean.lower():
                theatres.add(clean[:80])
    return theatres


def check_ticketnew_coimbatore():
    resp = requests.get(TICKETNEW_URL, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n")

    if "jana nayagan" not in text.lower():
        return

    if "coimbatore" not in text.lower():
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
                f"🕒 {now()}\n\n"
                f"👉 Book now:\n{TICKETNEW_URL}"
            )

# ===================== MAIN LOOP =====================

send_alert("🎬 Jana Nayagan watcher started (Coimbatore only • Per theatre • 6 days)")

while datetime.utcnow() < END_TIME:
    try:
        check_bookmyshow_per_theatre()
        check_ticketnew_coimbatore()
    except Exception as e:
        send_alert(f"⚠️ Watcher error:\n{str(e)}")

    time.sleep(CHECK_INTERVAL)

send_alert("⏹ Jana Nayagan watcher stopped (6 days completed)")
