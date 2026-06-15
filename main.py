from flask import Flask
import requests
import threading
import time
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

last_update_id = 0
BASE_URL = "https://api.telegram.org/botYOUR_BOT_TOKEN"


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


# ---------------- CLEAN TEXT ----------------
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
                t = re.sub(r'\s+', ' ', t)
                text.append(t)

            if len(text) >= 6:
                break

        return " ".join(text)
    except:
        return ""


# ---------------- SUMMARY ----------------
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

    return "\n• " + "\n• ".join(summary)


# ---------------- TELEGRAM LOOP ----------------
def bot_loop():
    global last_update_id

    while True:
        try:
            r = requests.get(
                f"{BASE_URL}/getUpdates",
                params={"offset": last_update_id + 1},
                timeout=10
            )

            updates = r.json()

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
                        "ربات تحلیل اینترنت فعال است 🔎"
                    )
                    continue

                send_message(chat_id, "🧠 در حال تحلیل...")

                links = search_web(text)

                if not links:
                    send_message(chat_id, "❌ چیزی پیدا نشد")
                    continue

                report = "📊 گزارش:\n\n"

                for i, link in enumerate(links[:3]):
                    report += f"🌐 منبع {i+1}:\n{link['title']}\n{link['url']}\n\n"

                    raw_text = extract_text(link["url"])
                    summary = smart_summary(raw_text)

                    report += f"🧠 خلاصه:\n• {summary}\n\n"
                    report += "-----------------\n\n"

                send_message(chat_id, report[:3500])

        except:
            pass

        time.sleep(1)


# ---------------- WEB SERVER ----------------
@app.route("/")
def home():
    return "Bot is running ✔"


# ---------------- START BOT THREAD ----------------
threading.Thread(target=bot_loop).start()


# ---------------- RUN FLASK ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
