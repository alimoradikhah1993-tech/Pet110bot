import requests
from bs4 import BeautifulSoup
import time
import re

TOKEN = "PUT_YOUR_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

last_update_id = 0


# ---------------- SEND MESSAGE ----------------
def send_message(chat_id, text):
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except:
        pass


# ---------------- SEARCH LINKS ----------------
def search_web(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        links = []
        for a in soup.select("a.result__a"):
            links.append({
                "title": a.get_text(),
                "url": a.get("href")
            })
            if len(links) >= 5:
                break

        return links
    except:
        return []


# ---------------- CLEAN TEXT FROM SITE ----------------
def extract_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = soup.find_all("p")

        text = []
        for p in paragraphs:
            t = p.get_text().strip()

            if len(t) > 50:
                # پاکسازی متن
                t = re.sub(r'\s+', ' ', t)
                text.append(t)

            if len(text) >= 6:
                break

        return " ".join(text)
    except:
        return ""


# ---------------- SIMPLE AI SUMMARY ----------------
def smart_summary(text):
    if not text:
        return "❌ اطلاعات کافی نیست"

    sentences = text.split(". ")

    summary = []
    for s in sentences:
        if len(s) > 40:
            summary.append(s.strip())
        if len(summary) >= 3:
            break

    return "\n• ".join(summary)


# ---------------- TELEGRAM UPDATES ----------------
def get_updates(offset):
    try:
        r = requests.get(
            f"{BASE_URL}/getUpdates",
            params={"offset": offset, "timeout": 10},
            timeout=15
        )
        return r.json()
    except:
        return {}


print("🤖 AI Web Research Bot V3 Started...")


# ---------------- MAIN LOOP ----------------
while True:
    updates = get_updates(last_update_id + 1)

    for update in updates.get("result", []):
        last_update_id = update["update_id"]

        msg = update.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text")

        if not chat_id or not text:
            continue

        text = text.strip()

        if text == "/start":
            send_message(chat_id,
                "👋 سلام!\n"
                "این ربات یک تحلیل‌گر اینترنتی است.\n"
                "هر موضوع یا کالا یا کشور بفرست 🔎"
            )
            continue

        send_message(chat_id, "🧠 در حال تحلیل چند منبع اینترنتی...")

        links = search_web(text)

        if not links:
            send_message(chat_id, "❌ چیزی پیدا نشد")
            continue

        report = "📊 گزارش تحلیل بازار اینترنتی:\n\n"

        for i, link in enumerate(links[:3]):
            report += f"🌐 منبع {i+1}:\n{link['title']}\n{link['url']}\n\n"

            raw_text = extract_text(link["url"])
            summary = smart_summary(raw_text)

            report += f"🧠 خلاصه:\n• {summary}\n\n"
            report += "----------------------\n\n"

        send_message(chat_id, report[:3500])

    time.sleep(1)
