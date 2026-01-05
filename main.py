import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

BOT_TOKEN = "8534697832:AAGYuvTIV7Aei4wQQR6mv_ZWi0T_tmHYwLo"
CHAT_ID = "-5152131952"

BMS_URL = "https://in.bookmyshow.com/explore/movies-coimbatore"
DISTRICT_URL = "https://www.district.in/movies/coimbatore"
TICKETNEW_URL = "https://ticketnew.com/movies/jana-nayagan-movie-detail-188681"

END_TIME = datetime.utcnow() + timedelta(days=6)
seen_theatres = set()

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    })

def extract_theatres(text):
    theatres = set()
    keywords = ["theatre", "cinemas", "inox", "pvr", "kg", "broadway", "miraj", "cinepolis", "karpagam"]
    for line in text.splitlines():
        for key in keywords:
            if key in line.lower():
                theatres.add(line.strip())
    return theatres

def check_page(platform, url):
    global seen_theatres
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(separator="\n").lower()

    if "jana nayagan" not in text:
        return

    theatres = extract_theatres(text)

    for theatre in theatres:
        if theatre not in seen_theatres:
            seen_theatres.add(theatre)
            send_alert(
                f"🚨 NEW THEATRE OPENED 🚨\n\n"
                f"🎬 Jana Nayagan\n"
                f"🏢 {theatre}\n"
                f"📍 Coimbatore\n"
                f"🌐 Platform: {platform}\n"
                f"🕒 {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
                f"👉 Book now:\n{url}"
            )

send_alert("🎬 Jana Nayagan booking watcher started (All theatres, 6 days)")

while datetime.utcnow() < END_TIME:
    try:
        check_page("BookMyShow", BMS_URL)
        check_page("District", DISTRICT_URL)
        check_page("TicketNew", TICKETNEW_URL)
        time.sleep(60)
    except:
        time.sleep(60)

send_alert("⏹ Monitoring stopped — 6 days completed")
