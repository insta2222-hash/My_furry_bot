import os
import re
from datetime import datetime, timedelta
import telebot
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ==================== НАСТРОЙКИ БОТА ====================
BOT_TOKEN = "8825377598:AAGh1okP02lBDfi2imGamHk8sUHO0Dl0Yqc"
CHANNEL_ID = "https://t.me/test_furry"
# ========================================================

bot = telebot.TeleBot(BOT_TOKEN)
TIME_SLOTS = [12, 14, 16, 18, 20]
DB_FILE = "last_post_time.txt"
HASHTAGS = "\n\n#furry #furryart #cute #anthro"

# --- Маленький веб-сервер, чтобы Render не спал ---
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8080))), WebServer)
    server.serve_forever()
# --------------------------------------------------

def get_last_post_time():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
            except: pass
    return datetime.now()

def save_last_post_time(dt):
    with open(DB_FILE, "w") as f:
        f.write(dt.strftime("%Y-%m-%d %H:%M:%S"))

def calculate_next_slot(last_dt):
    current_date = last_dt.date()
    current_hour = last_dt.hour
    available_slots = [slot for slot in TIME_SLOTS if slot > current_hour]
    if not available_slots:
        next_date = current_date + timedelta(days=1)
        next_hour = TIME_SLOTS[0]
    else:
        next_date = current_date
        next_hour = min(available_slots)
    return datetime.combine(next_date, datetime.min.time()).replace(hour=next_hour)

def extract_author(text):
    if not text: return None
    twitter_match = re.search(r'(?:x|twitter)\.com/([a-zA-Z0-9_]{1,15})', text)
    if twitter_match: return f"Art by: @{twitter_match.group(1)}"
    fa_match = re.search(r'furaffinity\.net/user/([a-zA-Z0-9_\-]+)', text)
    if fa_match: return f"Art by: {fa_match.group(1)}"
    return None

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption_text = message.caption if message.caption else ""
    author_info = extract_author(caption_text)
    final_text = f"{author_info}{HASHTAGS}" if author_info else HASHTAGS.strip()
    
    last_time = get_last_post_time()
    if last_time < datetime.now():
        last_time = datetime.now()
        
    next_slot = calculate_next_slot(last_time)
    post_timestamp = int(next_slot.timestamp())
    
    try:
        bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=final_text, until_date=post_timestamp)
        save_last_post_time(next_slot)
        bot.reply_to(message, f"✅ Пост отложен на:\n📅 {next_slot.strftime('%d.%m.%Y в %H:%M')}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Бот запущен...")
    bot.infinity_polling()
