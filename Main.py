import requests
import time

TOKEN = "8686109063:AAEYat6yfEX7LkRHHNDeoUyqtzQ1C4HNO4I"
last_update_id = 0
user_data = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=data)
    except:
        pass

print("ربات روشن شد!")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=10"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        for update in data.get("result", []):
            last_update_id = update["update_id"]
            msg = update.get("message", {})
            chat_id = str(msg.get("chat", {}).get("id"))
            text = msg.get("text", "").strip()
            
            if not chat_id or not text:
                continue
            
            if text == "/start":
                user_data[chat_id] = {"step": "product"}
                send_message(chat_id, "🔍 به ربات جستجوی کالا خوش آمدید!\n\n📦 لطفاً **نام کالا** را وارد کنید:")
                continue
            
            if chat_id in user_data:
                step = user_data[chat_id].get("step")
                
                if step == "product":
                    user_data[chat_id]["product"] = text
                    user_data[chat_id]["step"] = "country"
                    send_message(chat_id, f"✅ کالا: {text}\n\n🌍 حالا **نام کشور** را وارد کنید:")
                
                elif step == "country":
                    product = user_data[chat_id].get("product", "نامشخص")
                    country = text
                    del user_data[chat_id]
                    send_message(chat_id, f"🔎 در حال جستجوی: {product} در {country}\n\n(نتیجه جستجو بعداً اضافه می‌شود)")
                    send_message(chat_id, "🔁 برای جستجوی جدید /start را بزنید.")
            else:
                send_message(chat_id, "👋 لطفاً ابتدا /start را بزنید.")
        
        time.sleep(1)
    except Exception as e:
        print(f"خطا: {e}")
        time.sleep(5)
